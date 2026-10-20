# This Is Wehre The real Cfd 3D Magic And Heart Of AADP Starts From
# ALSO The 3D MODEL GOES TO TRIMESH LIB IT THEN GETS DETAILS OF THE MODEL AND THAT CAN BE USED FOR MESH MAKING OF SU2 AND FOR RENDERING OF AIRCRAFT IN OPENGL/VULKAN RENDER.

from pathlib import Path
import shutil

import trimesh
import numpy as np
from PySide6.QtWidgets import QFileDialog


class AircraftGeometry:

    def __init__(self, mesh, source_path):

        self.mesh = mesh
        self.source_path = Path(source_path)

        # Geometry information
        self.vertices = mesh.vertices.copy()
        self.faces = mesh.faces.copy()

        self.extents = mesh.extents.copy()
        self.centroid = mesh.centroid.copy()

        self.surface_area = float(mesh.area)

        try:
            self.volume = float(abs(mesh.volume))
        except Exception:
            self.volume = 0.0

        self.is_watertight = bool(mesh.is_watertight)

        self.length = float(self.extents[0])
        self.width = float(self.extents[1])
        self.height = float(self.extents[2])


def load_3D_Model():

    file, _ = QFileDialog.getOpenFileName(
        None,
        "Select Aircraft 3D Model",
        "",
        (
            "3D Models (*.stl *.obj *.ply *.off *.glb *.gltf);;"
            "STL (*.stl);;"
            "GLB (*.glb);;"
            "GLTF (*.gltf);;"
            "OBJ (*.obj);;"
            "PLY (*.ply);;"
            "OFF (*.off)"
        )
    )

    if not file:
        print("No aircraft model selected.")
        return None

    source = Path(file)

    print("Selected aircraft:", source)

    # AADP model folder
    project_folder = Path(__file__).parent.parent
    model_folder = project_folder / "Assets" / "3D Models"

    model_folder.mkdir(parents=True, exist_ok=True)

    destination = model_folder / source.name

    # Copy the original model into AADP's model folder
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)

    print("Loading model with trimesh...")

    try:

        loaded = trimesh.load(
            destination,
            force="scene"
        )

    except Exception as error:

        print("Failed to load aircraft model:")
        print(error)

        return None

    # Convert everything into one aircraft mesh.
    if isinstance(loaded, trimesh.Scene):

        if not loaded.geometry:
            print("The selected model contains no geometry.")
            return None

        # Convert the entire scene into one Trimesh.
        # This also applies the scene/node transforms.
        mesh = loaded.to_mesh()

    elif isinstance(loaded, trimesh.Trimesh):

        mesh = loaded

    else:

        print("Unsupported geometry returned by trimesh.")
        return None

    if mesh is None or len(mesh.vertices) == 0 or len(mesh.faces) == 0:

        print("Loaded model contains no usable triangles.")
        return None


    print("Successfully opened file!")
    print("Vertices:", len(mesh.vertices))
    print("Faces:", len(mesh.faces))
    print("Bounds:", mesh.bounds)
    print("Extents:", mesh.extents)
    print("Watertight:", mesh.is_watertight)

    return AircraftGeometry(mesh, destination)