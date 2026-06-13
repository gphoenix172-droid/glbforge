# glbforge

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) [![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org) [![Zero dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](#) [![Built by WCN](https://img.shields.io/badge/built%20by-WCN%20Development%20Co-1f6feb.svg)](https://github.com/WCN-DEV-CO)

**A tiny, dependency-light GLB (binary glTF 2.0) writer for Python.**

Write 3D meshes to `.glb` — positions, normals, UVs, vertex colors, indices, and PBR materials — using nothing but the Python standard library. No numpy. No dependencies. One small file.

```python
from glbforge import GLB, Mesh, Material

mesh = Mesh(
    positions=[(0, 0, 0), (1, 0, 0), (0, 1, 0)],
    indices=[0, 1, 2],
    normals=[(0, 0, 1)] * 3,
    uvs=[(0, 0), (1, 0), (0, 1)],
    material=Material(name="red", base_color=(0.9, 0.1, 0.1, 1.0), roughness=0.5),
)

GLB().add_mesh(mesh).save("triangle.glb")
```

That's it. The output is a valid glTF 2.0 binary that opens in Blender, three.js, Babylon.js, Windows 3D Viewer, or any glTF loader.

## Why

Most Python glTF tooling pulls in numpy and heavy dependencies, or is read-focused. `glbforge` is the opposite: a **write-only**, **zero-dependency**, **single-file** GLB writer you can drop into any project, pipeline, or serverless function where install weight matters.

- ✅ Pure standard library (`struct` + `json`)
- ✅ Multiple meshes per file
- ✅ PBR metallic-roughness materials
- ✅ Correct GLB chunk alignment + accessor min/max per spec
- ✅ Python 3.8+

## Install

```bash
pip install glbforge
```

Or just copy `glbforge/writer.py` into your project — it has no imports beyond the stdlib.

## API

| Class | Purpose |
|---|---|
| `GLB()` | Container. `.add_mesh(mesh)`, `.save(path)`, `.to_bytes()` |
| `Mesh(positions, indices, normals=, uvs=, colors=, material=, name=)` | A triangle mesh. Positions/normals/uvs/colors accept flat lists **or** tuples. |
| `Material(name=, base_color=, metallic=, roughness=)` | Minimal PBR metallic-roughness material. |

## Running the tests

```bash
python tests/test_writer.py     # or: pytest
```

## Contributing

PRs welcome — keep it dependency-free and spec-correct. Open an issue for format extensions (animations, skins, textures) and we'll scope them together.

## License

MIT © WCN Development Co, LLC
## Working with us

We're [WCN Development Co, LLC](https://github.com/WCN-DEV-CO) — we build large-scale systems and open-source the useful pieces. If you're building in this space and want to **partner, integrate, hire, or collaborate**, we'd genuinely like to hear from you. Open an issue tagged `partnership`, or reach out and let's find something mutually beneficial.
---

*Built and open-sourced by [WCN Development Co, LLC](https://github.com/WCN-DEV-CO) — we build AAA-grade tooling and ship the useful pieces back to the community.*
