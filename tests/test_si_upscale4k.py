import struct
import tempfile
import unittest
from pathlib import Path
import si_texture_audit as m


def make_png_header(w: int, h: int, color_type: int = 6) -> bytes:
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, color_type, 0, 0, 0)
    return sig + struct.pack(">I", 13) + b"IHDR" + ihdr + b"\x00\x00\x00\x00"


def make_dds_header(w: int, h: int, fourcc: bytes = b"DXT5") -> bytes:
    buf = bytearray(128)
    buf[0:4] = b"DDS "
    struct.pack_into("<I", buf, 4, 124)
    struct.pack_into("<II", buf, 12, h, w)
    buf[84:88] = fourcc
    return bytes(buf)


class TestSiUpscale4K(unittest.TestCase):
    def test_png_rgba_small_routes_to_4x_rgba_split(self):
        info = m.inspect_png_bytes(make_png_header(256, 256, color_type=6))
        self.assertTrue(info["hasAlpha"])
        self.assertTrue(info["powerOfTwo"])
        self.assertEqual(info["recommendedBucket"], "4x_rgba_split")

    def test_png_rgb_opaque_routes_to_4x_opaque(self):
        info = m.inspect_png_bytes(make_png_header(512, 256, color_type=2))
        self.assertFalse(info["hasAlpha"])
        self.assertEqual(info["recommendedBucket"], "4x_opaque")

    def test_png_1024_routes_to_2x(self):
        info = m.inspect_png_bytes(make_png_header(1024, 1024, color_type=2))
        self.assertEqual(info["recommendedBucket"], "2x_opaque")

    def test_png_2048_routes_to_skip(self):
        info = m.inspect_png_bytes(make_png_header(2048, 2048, color_type=6))
        self.assertEqual(info["recommendedBucket"], "skip_already_hd")

    def test_truncated_png_raises_clean_error(self):
        with self.assertRaises(ValueError):
            m.inspect_png_bytes(b"\x89PNG\r\n\x1a\n\x00\x00")

    def test_dds_dxt5_inspection(self):
        info = m.inspect_dds_bytes(make_dds_header(256, 256, b"DXT5"))
        self.assertEqual(info["format"], "DDS")
        self.assertTrue(info["hasAlpha"])
        self.assertEqual(info["recommendedBucket"], "4x_rgba_split")

    def test_audit_directory_counts_buckets(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "hud.png").write_bytes(make_png_header(256, 256, 6))
            (p / "wall.png").write_bytes(make_png_header(256, 256, 2))
            (p / "sky.dds").write_bytes(make_dds_header(2048, 2048, b"DXT1"))
            rep = m.audit_directory(p)
            self.assertEqual(rep["totalTextures"], 3)
            self.assertEqual(rep["buckets"]["4x_rgba_split"], 1)
            self.assertEqual(rep["buckets"]["4x_opaque"], 1)
            self.assertEqual(rep["buckets"]["skip_already_hd"], 1)


if __name__ == "__main__":
    unittest.main()
