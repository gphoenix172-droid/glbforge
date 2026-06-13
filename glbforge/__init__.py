"""
glbforge — a tiny, dependency-light GLB (binary glTF 2.0) writer for Python.

Write 3D meshes to .glb with positions, normals, UVs, vertex colors,
indices, and PBR materials — using nothing but the Python standard library.

Built and open-sourced by WCN Development Co, LLC. MIT licensed.
https://github.com/WCN-DEV-CO/glbforge
"""
from .writer import GLB, Mesh, Material

__version__ = "0.1.0"
__all__ = ["GLB", "Mesh", "Material"]
