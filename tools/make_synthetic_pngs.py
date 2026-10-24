#!/usr/bin/env python3
"""Generate tiny ORIGINAL RGBA PNG fixtures without third-party dependencies.

Not pre-processed Cricut Print Then Cut sheets: printer registration marks must
be produced by Cricut Design Space, never synthesized by this script.
"""
from __future__ import annotations

import argparse
import math
import struct
import zlib
from pathlib import Path
from typing import Callable

RGBA = tuple[int, int, int, int]


def png_chunk(name: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + name + payload + struct.pack(">I", zlib.crc32(name + payload) & 0xFFFFFFFF)


def png_bytes(width: int, height: int, pixel: Callable[[int, int], RGBA]) -> bytes:
    if width < 1 or height < 1 or width * height > 1_000_000:
        raise ValueError("IMAGE_SIZE_LIMIT")
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # PNG filter: None
        for x in range(width):
            rgba = pixel(x, y)
            if len(rgba) != 4 or any(not isinstance(c, int) or not 0 <= c <= 255 for c in rgba):
                raise ValueError("INVALID_RGBA")
            raw.extend(rgba)
    return (b"\x89PNG\r\n\x1a\n"
            + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + png_chunk(b"IDAT", zlib.compress(bytes(raw), level=6))
            + png_chunk(b"IEND", b""))


def synthesize(output: Path) -> list[Path]:
    if not output.is_dir():
        raise ValueError("DESTINATION_FOLDER_MUST_EXIST")
    size = (144, 144)
    circle = lambda x, y, cx, cy, r: (x - cx)**2 + (y - cy)**2 <= r*r

    def sticker(x: int, y: int) -> RGBA:
        if circle(x, y, 72, 72, 62):
            return (252, 155, 90, 255) if not circle(x, y, 72, 72, 28) else (255, 225, 104, 255)
        return (0, 0, 0, 0)

    def sheet(x: int, y: int) -> RGBA:
        for k in range(12):
            cx, cy = 21 + (k % 4) * 34, 25 + (k // 4) * 40
            if circle(x, y, cx, cy, 12):
                return (40 + k * 14, 80 + k * 8, 130 + k * 5, 255)
        return (255, 255, 255, 255)

    def clipped(x: int, y: int) -> RGBA:
        return (35, 116, 170, 255) if circle(x, y, -6, 72, 80) else (0, 0, 0, 0)

    def opaque(x: int, y: int) -> RGBA:
        return (55 + int(x * 160 / 143), 70 + int(y * 130 / 143), 165, 255)

    recipes = {
        "sticker_alpha.png": sticker,
        "planche_12_sur_fond_blanc.png": sheet,
        "masque_touche_bord.png": clipped,
        "photo_factice_opaque.png": opaque,
    }
    expected = [output / name for name in recipes]
    if any(p.exists() for p in expected):
        raise FileExistsError("WILL_NOT_OVERWRITE_EXISTING_FIXTURE")
    data = {name: png_bytes(*size, pixel) for name, pixel in recipes.items()}
    created = []
    try:
        for name, blob in data.items():
            p = output / name
            with p.open("xb") as dst:
                dst.write(blob)
            created.append(p)
    except Exception:
        for p in created:
            p.unlink(missing_ok=True)
        raise
    return created


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True, help="Existing destination directory")
    args = p.parse_args()
    for file in synthesize(args.out):
        print(file.name)


if __name__ == "__main__":
    main()
