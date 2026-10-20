# THIS TAKES THE DATA FROM TRIMESH IN Loader_3D.py AND ACCURATELY SCALES THEM FOR SU2 and Rendering and MAKES THE TRIMESH DATA INTO ACCURATELY SIZED MESH WHICH THEN
# GOES TO Mesh_Gen.py which makes the converted mesh from this file into an acceptable form that SU2 can take.
#AADP COORDINATE SYSTEM Same As Su2
#X → longitudinal / fuselage (same as SU2, freestream flows along +X)
#+X → tail
# -X = nose
#Y → lateral / wings
#+Y → right wing
# -Y = left wing
#Z → vertical
#+Z → up
# -Z = down

from pathlib import Path
import numpy as np
import trimesh
MAX_SCALE_MISMATCH = 0.07   # 7%

class ConvertedAircraft:

    def __init__(
        self,
        vertices,
        faces,
        reference_length,
        reference_wingspan
    ):

        self.vertices = np.asarray(
            vertices,
            dtype=float
        )

        self.faces = np.asarray(
            faces,
            dtype=np.int64
        )

        self.reference_length = float(
            reference_length
        )

        self.reference_wingspan = float(
            reference_wingspan
        )

        self.extents = (
            self.vertices.max(axis=0)
            - self.vertices.min(axis=0)
        )


def _axis_index(axis):

    axis = str(axis).lower()

    if axis not in ("x", "y", "z"):

        raise ValueError(
            f"Invalid axis '{axis}'. "
            "Expected x, y, or z."
        )

    return {
        "x": 0,
        "y": 1,
        "z": 2
    }[axis]


def _direction_value(direction, name):

    direction = str(direction).lower()

    if direction == "positive":

        return 1.0

    if direction == "negative":

        return -1.0

    raise ValueError(
        f"{name} must be "
        "'positive' or 'negative'. "
        f"Got: {direction}"
    )


def _build_axis_mapping(state):

    # The aircraft JSON tells us which source axis is:
    #
    # - nose/tail
    # - vertical/height
    #
    # The remaining source axis becomes the lateral axis.

    longitudinal_axis = _axis_index(
        state.nose_to_tail_axis
    )

    height_axis = _axis_index(
        state.height_axis
    )

    if longitudinal_axis == height_axis:

        raise ValueError(
            "nose_to_tail_axis and height_axis "
            "cannot be the same axis."
        )

    remaining_axes = [
        axis
        for axis in range(3)
        if axis not in (
            longitudinal_axis,
            height_axis
        )
    ]

    lateral_axis = remaining_axes[0]

    # Read the direction information from JSON.
    #
    # Your JSON uses:
    #
    # "positive"
    # "negative"

    towards_nose = _direction_value(
        state.towards_nose,
        "towards_nose"
    )

    towards_up = _direction_value(
        state.towards_up,
        "towards_up"
    )

    # --------------------------------------------------
    # AADP / SU2 TARGET AXES
    # --------------------------------------------------
    #
    # +X = tail
    # -X = nose
    #
    # +Y = right wing
    # -Y = left wing
    #
    # +Z = up
    # -Z = down

    mapping = np.zeros(
        (3, 3),
        dtype=float
    )

    # --------------------------------------------------
    # LONGITUDINAL AXIS
    # --------------------------------------------------
    #
    # If source +axis points toward the nose:
    #
    # source +axis -> AADP -X
    #
    # If source +axis points toward the tail:
    #
    # source +axis -> AADP +X

    mapping[0, longitudinal_axis] = (
        -towards_nose
    )

    # --------------------------------------------------
    # HEIGHT AXIS
    # --------------------------------------------------
    #
    # If source +axis points upward:
    #
    # source +axis -> AADP +Z
    #
    # If source +axis points downward:
    #
    # source +axis -> AADP -Z

    mapping[2, height_axis] = (
        towards_up
    )

    # --------------------------------------------------
    # LATERAL AXIS
    # --------------------------------------------------
    #
    # The remaining axis must be chosen so the final
    # coordinate system remains right-handed.
    #
    # AADP/SU2 requires:
    #
    # X cross Y = Z

    target_x = mapping[0]

    target_z = mapping[2]

    expected_y = np.cross(
        target_z,
        target_x
    )

    source_y = np.zeros(3)

    source_y[lateral_axis] = 1.0

    if np.dot(
        expected_y,
        source_y
    ) >= 0:

        mapping[1, lateral_axis] = 1.0

    else:

        mapping[1, lateral_axis] = -1.0

    return mapping


def _clean_mesh(mesh):

    # Make a copy so the original loaded aircraft
    # is not modified.

    mesh = mesh.copy()

    # --------------------------------------------------
    # Remove duplicate faces
    # --------------------------------------------------

    try:

        mesh.update_faces(
            mesh.unique_faces()
        )

    except Exception:

        pass

    # --------------------------------------------------
    # Remove degenerate faces
    # --------------------------------------------------

    try:

        mesh.update_faces(
            mesh.nondegenerate_faces()
        )

    except Exception:

        pass

    # --------------------------------------------------
    # Remove vertices that are no longer referenced
    # --------------------------------------------------

    try:

        mesh.remove_unreferenced_vertices()

    except Exception:

        pass

    # --------------------------------------------------
    # Remove non-finite geometry
    # --------------------------------------------------

    try:

        valid_mesh = (
            mesh.remove_infinite_values()
        )

        if valid_mesh is not None:

            mesh = valid_mesh

    except Exception:

        pass

    return mesh


def convert_and_export(
    state,
    output_folder
):

    # --------------------------------------------------
    # CHECK INPUT
    # --------------------------------------------------

    if state.model_geometry is None:

        raise ValueError(
            "No aircraft geometry has been loaded."
        )

    geometry = state.model_geometry

    mesh = geometry.mesh

    if mesh is None:

        raise ValueError(
            "Aircraft geometry does not contain "
            "a mesh."
        )

    print(
        "Starting aircraft conversion..."
    )

    # --------------------------------------------------
    # CLEAN MODEL
    # --------------------------------------------------

    mesh = _clean_mesh(mesh)

    if len(mesh.vertices) == 0:

        raise ValueError(
            "Aircraft mesh contains no vertices."
        )

    if len(mesh.faces) == 0:

        raise ValueError(
            "Aircraft mesh contains no faces."
        )

    print(
        "Cleaned mesh:",
        len(mesh.vertices),
        "vertices,",
        len(mesh.faces),
        "triangles"
    )

    # --------------------------------------------------
    # GET AXIS MAPPING FROM JSON
    # --------------------------------------------------

    mapping = _build_axis_mapping(
        state
    )

    print(
        "Axis mapping:"
    )

    print(mapping)

    # --------------------------------------------------
    # GET VERTICES AND FACES
    # --------------------------------------------------

    vertices = np.asarray(
        mesh.vertices,
        dtype=float
    )

    faces = np.asarray(
        mesh.faces,
        dtype=np.int64
    )

    # --------------------------------------------------
    # CONVERT SOURCE XYZ -> AADP/SU2 XYZ
    # --------------------------------------------------
    #
    # Every vertex is transformed using the matrix
    # generated from the aircraft JSON.
    #
    # converted = mapping * source
    #
    # Using row-vector vertices:
    #
    # converted_vertices = vertices @ mapping.T

    converted_vertices = (
        vertices @ mapping.T
    )

    # --------------------------------------------------
    # MODEL DIMENSIONS BEFORE SCALING
    # --------------------------------------------------

    source_extents = (
        converted_vertices.max(axis=0)
        - converted_vertices.min(axis=0)
    )

    model_length = float(
        source_extents[0]
    )

    model_wingspan = float(
        source_extents[1]
    )

    model_height = float(
        source_extents[2]
    )

    if model_length <= 0:

        raise ValueError(
            "Converted aircraft has zero length."
        )

    if model_wingspan <= 0:

        raise ValueError(
            "Converted aircraft has zero wingspan."
        )

    # --------------------------------------------------
    # TARGET DIMENSIONS FROM JSON
    # --------------------------------------------------

    target_length = float(
        state.length
    )

    target_wingspan = float(
        state.wingspan
    )

    if target_length <= 0:

        raise ValueError(
            "Aircraft JSON length must be "
            "greater than zero."
        )

    if target_wingspan <= 0:

        raise ValueError(
            "Aircraft JSON wingspan must be "
            "greater than zero."
        )

    # --------------------------------------------------
    # CALCULATE SCALE
    # --------------------------------------------------

    length_scale = (target_length /model_length)

    span_scale = (target_wingspan / model_wingspan)

    # Difference between length-based and
    # wingspan-based scale.

    mismatch = abs(length_scale - span_scale)

    # Average scale keeps the whole model
    # uniformly scaled.

    average_scale = (length_scale + span_scale) / 2.0

    mismatch = abs(length_scale - span_scale) / average_scale
    if mismatch > MAX_SCALE_MISMATCH:
     raise ValueError(f"Scale mismatch {mismatch*100:.1f}% (limit {MAX_SCALE_MISMATCH*100:.0f}%). Mapped extents: {source_extents}. Check JSON axes.")

    # --------------------------------------------------
    # APPLY SCALE
    # --------------------------------------------------

    converted_vertices *= (average_scale)

    # --------------------------------------------------
    # FINAL DIMENSIONS
    # --------------------------------------------------

    final_extents = (converted_vertices.max(axis=0) - converted_vertices.min(axis=0))

    final_length = float(final_extents[0])

    final_wingspan = float(final_extents[1])

    final_height = float(final_extents[2])

    print(
        f"length (X): {final_length:.3f} "
        f"span (Y): {final_wingspan:.3f} "
        f"height (Z): {final_height:.3f}"
    )

    print(f"Length scale: {length_scale:.6f}")

    print(f"Span scale: {span_scale:.6f}")

    # --------------------------------------------------
    # CREATE FINAL TRIMESH
    # --------------------------------------------------

    converted_mesh = trimesh.Trimesh(
        vertices=converted_vertices,
        faces=faces,
        process=False
    )

    # --------------------------------------------------
    # OUTPUT FOLDER
    # --------------------------------------------------

    output_folder = Path(output_folder)

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------
    # OUTPUT FILE NAME
    # --------------------------------------------------

    aircraft_name = str(state.aircraft_name)

    # Make the aircraft name safe for a filename.

    aircraft_name = "".join(
        character
        if (
            character.isalnum()
            or character in (
                " ",
                "-",
                "_"
            )
        )
        else "_"
        for character in aircraft_name
    ).strip()

    if not aircraft_name:

        aircraft_name = "aircraft"

    output_path = (output_folder /f"{aircraft_name}_converted.stl")

    # --------------------------------------------------
    # EXPORT STL
    # --------------------------------------------------

    converted_mesh.export(
        output_path,
        file_type="stl"
    )

    print("Converted aircraft exported to:",output_path)

    # --------------------------------------------------
    # CREATE RETURN OBJECT
    # --------------------------------------------------

    converted_aircraft = ConvertedAircraft(
        converted_vertices,
        faces,
        target_length,
        target_wingspan
    )

    # --------------------------------------------------
    # CONSISTENCY INFORMATION
    # --------------------------------------------------

    consistency = {

        "length_scale":
            length_scale,

        "span_scale":
            span_scale,

        "scale":
            average_scale,

        "mismatch":
            mismatch,

        "model_length":
            model_length,

        "model_wingspan":
            model_wingspan,

        "model_height":
            model_height,

        "final_length":
            final_length,

        "final_wingspan":
            final_wingspan,

        "final_height":
            final_height
    }

    # --------------------------------------------------
    # RETURN TO AADP.PY
    # --------------------------------------------------

    return (
        output_path,
        consistency,
        converted_aircraft.vertices,
        converted_aircraft.faces
    )