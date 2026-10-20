import numpy as np
import trimesh

PITCH = 0.3              # voxel size in metres (smaller = more detail, more faces)
MIN_PART_FRACTION = 0.001  # drop pieces smaller than 0.1% of total area

def _keep_big_parts(mesh):
    parts = mesh.split(only_watertight=False)
    return trimesh.util.concatenate([p for p in parts if p.area > MIN_PART_FRACTION * mesh.area])

def _voxel_wrap(mesh):
    vox = mesh.voxelized(PITCH).fill()
    wrapped = vox.marching_cubes
    wrapped.apply_transform(vox.transform)
    return wrapped

def clean_surface(vertices, faces):
    mesh = trimesh.Trimesh(vertices, faces, process=False)
    mesh.merge_vertices()
    mesh = _keep_big_parts(mesh)
    mesh = _voxel_wrap(mesh)
    print("Cleaned:", len(mesh.faces), "faces, watertight:", mesh.is_watertight, "volume:", mesh.volume)
    return np.asarray(mesh.vertices), np.asarray(mesh.faces)