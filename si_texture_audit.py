#!/usr/bin/env python3
"""
SI-Upscale4K (by SI NEWS) — Zero-dependency PNG & DDS Binary Header Inspector & Batch Router.
100% Python 3 standard library (struct, os, json).
"""
from __future__ import annotations
import argparse
import json
import os
import struct
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def inspect_png_bytes(data: bytes) -> Dict[str, Any]:
    if len(data) < 29 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("Invalid PNG header or truncated IHDR chunk.")
    width, height, bit_depth, color_type = struct.unpack_from(">IIBB", data, 16)
    if width == 0 or height == 0:
        raise ValueError("Invalid zero-dimension PNG.")
    has_alpha = color_type in (4, 6) or (b"tRNS" in data[:256])
    return {
        "format": "PNG",
        "width": width,
        "height": height,
        "bitDepth": bit_depth,
        "hasAlpha": has_alpha,
        "powerOfTwo": is_power_of_two(width) and is_power_of_two(height),
        "recommendedBucket": recommend_bucket(width, height, has_alpha),
    }


def inspect_dds_bytes(data: bytes) -> Dict[str, Any]:
    if len(data) < 128 or data[:4] != b"DDS ":
        raise ValueError("Invalid DDS magic header.")
    height, width = struct.unpack_from("<II", data, 12)
    ddspf_flags = struct.unpack_from("<I", data, 80)[0]
    fourcc = data[84:88].decode("ascii", errors="ignore")
    has_alpha = bool(ddspf_flags & 0x1) or fourcc in ("DXT3", "DXT5", "DX10")
    return {
        "format": "DDS",
        "width": width,
        "height": height,
        "fourCC": fourcc.strip() or "UNCOMPRESSED",
        "hasAlpha": has_alpha,
        "powerOfTwo": is_power_of_two(width) and is_power_of_two(height),
        "recommendedBucket": recommend_bucket(width, height, has_alpha),
    }


def recommend_bucket(width: int, height: int, has_alpha: bool) -> str:
    max_dim = max(width, height)
    if max_dim >= 2048:
        return "skip_already_hd"
    if max_dim > 512:
        return "2x_rgba_split" if has_alpha else "2x_opaque"
    return "4x_rgba_split" if has_alpha else "4x_opaque"


def audit_directory(root_dir: Path) -> Dict[str, Any]:
    counts: Dict[str, int] = {
        "4x_rgba_split": 0,
        "4x_opaque": 0,
        "2x_rgba_split": 0,
        "2x_opaque": 0,
        "skip_already_hd": 0,
        "errors": 0,
    }
    total = 0
    for dirpath, _, filenames in os.walk(root_dir):
        for fn in filenames:
            fp = Path(dirpath) / fn
            ext = fp.suffix.lower()
            if ext not in (".png", ".dds"):
                continue
            total += 1
            try:
                head = fp.open("rb").read(256)
                info = inspect_png_bytes(head) if ext == ".png" else inspect_dds_bytes(head)
                counts[info["recommendedBucket"]] += 1
            except Exception:
                counts["errors"] += 1
    return {"totalTextures": total, "buckets": counts}


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SI-Upscale4K Texture Dump Auditor (by SI NEWS)")
    parser.add_argument("--scan", type=str, help="Directory of dumped PNG/DDS textures to audit")
    args = parser.parse_args(argv)
    if args.scan:
        rep = audit_directory(Path(args.scan))
        print(json.dumps(rep, indent=2))
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
