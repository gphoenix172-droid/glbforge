"""Minimal example: write a single colored triangle to triangle.glb."""
from glbforge import GLB, Mesh, Material

mesh = Mesh(
    positions=[(0, 0, 0), (1, 0, 0), (0, 1, 0)],
    indices=[0, 1, 2],
    normals=[(0, 0, 1), (0, 0, 1), (0, 0, 1)],
    uvs=[(0, 0), (1, 0), (0, 1)],
    material=Material(name="red", base_color=(0.9, 0.1, 0.1, 1.0), roughness=0.5),
    name="triangle",
)

GLB().add_mesh(mesh).save("triangle.glb")
print("wrote triangle.glb")
