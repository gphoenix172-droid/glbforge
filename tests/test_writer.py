import struct
from glbforge import GLB, Mesh, Material


def _make():
    return Mesh(
        positions=[(0, 0, 0), (1, 0, 0), (0, 1, 0)],
        indices=[0, 1, 2],
        normals=[(0, 0, 1)] * 3,
        uvs=[(0, 0), (1, 0), (0, 1)],
        material=Material(),
        name="tri",
    )


def test_valid_glb_header():
    data = GLB().add_mesh(_make()).to_bytes()
    magic, version, length = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67  # "glTF"
    assert version == 2
    assert length == len(data)


def test_chunks_present_and_aligned():
    data = GLB().add_mesh(_make()).to_bytes()
    assert len(data) % 4 == 0
    json_len, json_type = struct.unpack("<II", data[12:20])
    assert json_type == 0x4E4F534A  # JSON
    assert json_len % 4 == 0


def test_multiple_meshes():
    g = GLB().add_mesh(_make()).add_mesh(_make())
    data = g.to_bytes()
    assert len(data) > 0
    assert b"glTF" in data[:4]


if __name__ == "__main__":
    test_valid_glb_header()
    test_chunks_present_and_aligned()
    test_multiple_meshes()
    print("all tests passed")
