# Loader_3D.py ----> Model_Converter.py ----> Mesh_Gen.py ----> SU2
#
# Takes the converted aircraft surface (vertices + triangles, already in AADP/SU2
# axes and real-world metres), wraps it in a farfield box, and uses Gmsh to
# generate the tetrahedral volume mesh for SU2.
#
# Gmsh is the only volumetric meshing library used by AADP.

from pathlib import Path
import tempfile

import gmsh
FARFIELD_FACTOR, NEAR_SIZE, FAR_SIZE = 5.0, 1.0, 40.0

def _write_surface_stl(vertices, faces, path):

    # Gmsh can import the STL surface directly.
    # Write a temporary STL from the already-cleaned
    # vertices and triangle faces.

    with open(path, "w") as file:

        file.write("solid aircraft\n")

        for face in faces:

            p1 = vertices[face[0]]
            p2 = vertices[face[1]]
            p3 = vertices[face[2]]

            file.write(
                "facet normal 0 0 0\n"
            )

            file.write(
                "outer loop\n"
            )

            file.write(
                f"vertex {p1[0]} {p1[1]} {p1[2]}\n"
            )

            file.write(
                f"vertex {p2[0]} {p2[1]} {p2[2]}\n"
            )

            file.write(
                f"vertex {p3[0]} {p3[1]} {p3[2]}\n"
            )

            file.write(
                "endloop\n"
            )

            file.write(
                "endfacet\n"
            )

        file.write("endsolid aircraft\n")

def _add_farfield_box(lo, hi, size):
    g = gmsh.model.geo
    p = [g.addPoint(x, y, lo[2], size) for x, y in ((lo[0], lo[1]), (hi[0], lo[1]), (hi[0], hi[1]), (lo[0], hi[1]))]
    s = g.addPlaneSurface([g.addCurveLoop([g.addLine(p[i], p[(i + 1) % 4]) for i in range(4)])])
    ov = g.extrude([(2, s)], 0, 0, hi[2] - lo[2])
    g.remove([ov[1]])  # drop the solid box, keep only its skin
    g.synchronize()
    return [s, ov[0][1]] + [t for _, t in ov[2:]]

def generate_mesh(vertices, faces, name):

    vertices = vertices
    faces = faces

    if len(vertices) == 0:
        raise ValueError(
            "Aircraft mesh contains no vertices."
        )

    if len(faces) == 0:
        raise ValueError(
            "Aircraft mesh contains no faces."
        )

    project_folder = Path(__file__).parent.parent

    mesh_folder = (
        project_folder /
        "Assets" /
        "Mesh"
    )

    mesh_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        mesh_folder /
        f"{name}.su2"
    )

    gmsh.initialize()

    try:

        gmsh.option.setNumber(
            "General.Terminal",
            1
        )

        gmsh.model.add("AADP_Aircraft")

        lo, hi = vertices.min(axis=0), vertices.max(axis=0)
        pad = float(FARFIELD_FACTOR * (hi[0] - lo[0]))
        box_tags = _add_farfield_box((lo - pad).tolist(), (hi + pad).tolist(), FAR_SIZE)

        # ------------------------------------------
        # AIRCRAFT SURFACE
        # ------------------------------------------

        with tempfile.NamedTemporaryFile(
            suffix=".stl",
            delete=False
        ) as temporary_file:

            temporary_path = Path(
                temporary_file.name
            )

        try:

            _write_surface_stl(
                vertices,
                faces,
                temporary_path
            )

            gmsh.merge(
                str(temporary_path)
            )

        finally:

            temporary_path.unlink(
                missing_ok=True
            )

        # ------------------------------------------
        # CREATE GEOMETRY FROM STL
        # ------------------------------------------
        
        aircraft_tags = [t for _, t in gmsh.model.getEntities(2) if t not in box_tags]
        g = gmsh.model.geo
        air = g.addVolume([g.addSurfaceLoop(box_tags), g.addSurfaceLoop(aircraft_tags)])
        g.synchronize()
        gmsh.model.addPhysicalGroup(2, aircraft_tags, name="aircraft")
        gmsh.model.addPhysicalGroup(2, box_tags, name="farfield")
        gmsh.model.addPhysicalGroup(3, [air], name="air")
        f = gmsh.model.mesh.field
        d = f.add("Distance"); f.setNumbers(d, "SurfacesList", aircraft_tags)
        t = f.add("Threshold")
        for k, v in (("InField", d), ("SizeMin", NEAR_SIZE), ("SizeMax", FAR_SIZE), ("DistMin", 2.0), ("DistMax", pad)): f.setNumber(t, k, v)
        f.setAsBackgroundMesh(t)
        for o in ("Mesh.MeshSizeFromPoints", "Mesh.MeshSizeFromCurvature", "Mesh.MeshSizeExtendFromBoundary"): gmsh.option.setNumber(o, 0)

        # ------------------------------------------
        # MESH SETTINGS
        # ------------------------------------------

        gmsh.option.setNumber(
            "Mesh.Algorithm3D",
            1
        )

        gmsh.option.setNumber(
            "Mesh.ElementOrder",
            1
        )

        # ------------------------------------------
        # GENERATE TETRAHEDRAL MESH
        # ------------------------------------------

        print(
            "Generating tetrahedral mesh with Gmsh..."
        )

        gmsh.model.mesh.generate(
            3
        )

        # ------------------------------------------
        # SAVE
        # ------------------------------------------

        gmsh.write(
            str(output_path)
        )

        print(
            "Mesh written to:",
            output_path
        )

        return output_path

    finally:

        gmsh.finalize()