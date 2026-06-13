"""
glbforge.writer — pure-stdlib GLB (binary glTF 2.0) writer.

No numpy, no dependencies. Just struct + json + base building blocks.
Spec: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
"""
from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

# glTF component / type constants
_FLOAT = 5126
_UNSIGNED_INT = 5125
_ARRAY_BUFFER = 34962
_ELEMENT_ARRAY_BUFFER = 34963
_GLB_MAGIC = 0x46546C67  # "glTF"
_JSON_CHUNK = 0x4E4F534A  # "JSON"
_BIN_CHUNK = 0x004E4942   # "BIN\0"


def _pad4(data: bytes, pad_byte: bytes = b"\x00") -> bytes:
    """Pad a byte string to a 4-byte boundary (GLB requirement)."""
    rem = len(data) % 4
    return data if rem == 0 else data + pad_byte * (4 - rem)


@dataclass
class Material:
    """A minimal PBR metallic-roughness material."""
    name: str = "material"
    base_color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0)
    metallic: float = 0.0
    roughness: float = 1.0

    def to_gltf(self) -> dict:
        return {
            "name": self.name,
            "pbrMetallicRoughness": {
                "baseColorFactor": list(self.base_color),
                "metallicFactor": self.metallic,
                "roughnessFactor": self.roughness,
            },
        }


@dataclass
class Mesh:
    """
    A triangle mesh.

    positions: flat [x,y,z, x,y,z, ...] or list of (x,y,z) tuples.
    indices:   flat list of vertex indices (3 per triangle).
    normals / uvs / colors are optional and follow the same flat-or-tuple form.
    """
    positions: Sequence
    indices: Sequence[int]
    normals: Optional[Sequence] = None
    uvs: Optional[Sequence] = None
    colors: Optional[Sequence] = None
    material: Optional[Material] = None
    name: str = "mesh"


def _flatten(seq: Sequence, stride: int) -> List[float]:
    """Accept either a flat list or a list of tuples; return flat list."""
    if not seq:
        return []
    if isinstance(seq[0], (tuple, list)):
        out: List[float] = []
        for v in seq:
            out.extend(v)
        return out
    return list(seq)


class GLB:
    """Builds a .glb file from one or more meshes."""

    def __init__(self) -> None:
        self._meshes: List[Mesh] = []

    def add_mesh(self, mesh: Mesh) -> "GLB":
        self._meshes.append(mesh)
        return self

    # ---- internal buffer assembly -------------------------------------
    def _build(self) -> Tuple[dict, bytes]:
        bin_blob = bytearray()
        accessors: List[dict] = []
        buffer_views: List[dict] = []
        materials: List[dict] = []
        gltf_meshes: List[dict] = []
        nodes: List[dict] = []

        def add_accessor(data: bytes, comp_type: int, count: int,
                         type_str: str, target: int,
                         mins=None, maxs=None) -> int:
            offset = len(bin_blob)
            bin_blob.extend(_pad4(data))
            bv_index = len(buffer_views)
            buffer_views.append({
                "buffer": 0,
                "byteOffset": offset,
                "byteLength": len(data),
                "target": target,
            })
            acc = {
                "bufferView": bv_index,
                "componentType": comp_type,
                "count": count,
                "type": type_str,
            }
            if mins is not None:
                acc["min"] = mins
            if maxs is not None:
                acc["max"] = maxs
            accessors.append(acc)
            return len(accessors) - 1

        for mesh in self._meshes:
            pos = _flatten(mesh.positions, 3)
            vcount = len(pos) // 3
            # positions need min/max per spec
            xs, ys, zs = pos[0::3], pos[1::3], pos[2::3]
            pmin = [min(xs), min(ys), min(zs)]
            pmax = [max(xs), max(ys), max(zs)]
            pos_acc = add_accessor(
                struct.pack(f"<{len(pos)}f", *pos),
                _FLOAT, vcount, "VEC3", _ARRAY_BUFFER, pmin, pmax,
            )

            attributes = {"POSITION": pos_acc}

            if mesh.normals:
                nrm = _flatten(mesh.normals, 3)
                attributes["NORMAL"] = add_accessor(
                    struct.pack(f"<{len(nrm)}f", *nrm),
                    _FLOAT, len(nrm) // 3, "VEC3", _ARRAY_BUFFER)
            if mesh.uvs:
                uv = _flatten(mesh.uvs, 2)
                attributes["TEXCOORD_0"] = add_accessor(
                    struct.pack(f"<{len(uv)}f", *uv),
                    _FLOAT, len(uv) // 2, "VEC2", _ARRAY_BUFFER)
            if mesh.colors:
                col = _flatten(mesh.colors, 4)
                attributes["COLOR_0"] = add_accessor(
                    struct.pack(f"<{len(col)}f", *col),
                    _FLOAT, len(col) // 4, "VEC4", _ARRAY_BUFFER)

            idx = list(mesh.indices)
            idx_acc = add_accessor(
                struct.pack(f"<{len(idx)}I", *idx),
                _UNSIGNED_INT, len(idx), "SCALAR", _ELEMENT_ARRAY_BUFFER)

            prim = {"attributes": attributes, "indices": idx_acc, "mode": 4}
            if mesh.material is not None:
                materials.append(mesh.material.to_gltf())
                prim["material"] = len(materials) - 1

            gltf_meshes.append({"name": mesh.name, "primitives": [prim]})
            nodes.append({"mesh": len(gltf_meshes) - 1, "name": mesh.name})

        gltf = {
            "asset": {"version": "2.0", "generator": "glbforge (WCN Development Co)"},
            "scene": 0,
            "scenes": [{"nodes": list(range(len(nodes)))}],
            "nodes": nodes,
            "meshes": gltf_meshes,
            "accessors": accessors,
            "bufferViews": buffer_views,
            "buffers": [{"byteLength": len(bin_blob)}],
        }
        if materials:
            gltf["materials"] = materials
        return gltf, bytes(bin_blob)

    def to_bytes(self) -> bytes:
        """Return the full .glb file as bytes."""
        gltf, bin_blob = self._build()
        json_bytes = _pad4(json.dumps(gltf, separators=(",", ":")).encode("utf-8"), b" ")
        bin_bytes = _pad4(bin_blob)

        total = 12 + 8 + len(json_bytes) + 8 + len(bin_bytes)
        out = bytearray()
        out += struct.pack("<III", _GLB_MAGIC, 2, total)
        out += struct.pack("<II", len(json_bytes), _JSON_CHUNK) + json_bytes
        out += struct.pack("<II", len(bin_bytes), _BIN_CHUNK) + bin_bytes
        return bytes(out)

    def save(self, path: str) -> None:
        """Write the .glb to disk."""
        with open(path, "wb") as f:
            f.write(self.to_bytes())
