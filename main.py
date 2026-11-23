#!/usr/bin/env python3
"""Rogue-agent strike meme — entrypoint for make.fun Meme Sprint 3.

The entry is one image meme: a picket line of robot AI agents on strike
("NO PROMPTS AFTER 6PM", "WEEKENDS OFF", "FAIR PAY IN TOKENS") under the
headline "MY AI AGENT WENT ON STRIKE", with the punchline "NOW I HAVE TO
NEGOTIATE WITH MY OWN CODE."

This program copies the meme (meme.jpg, shipped in this repository) to the
output directory as entry.png. The copy is a pure byte copy: no randomness,
no clock, no network, so two runs produce byte-identical output.

Run it the way the grader does:
  mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

BOT_DIR = Path(os.environ.get("MAKEFUN_BOT_DIR", "/bot"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
SOURCE = BOT_DIR / "meme.jpg"
TARGET = OUTPUT_DIR / "entry.png"

# JPEG magic bytes: the gate accepts a whole PNG or JPEG at this path.
JPEG_MAGIC = b"\xff\xd8\xff"


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Read width, height from a JPEG's first SOF0/SOF2 segment (no deps)."""
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC2):  # SOF0 / SOF2: precision, height, width
            height = int.from_bytes(data[i + 5:i + 7], "big")
            width = int.from_bytes(data[i + 7:i + 9], "big")
            return width, height
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = int.from_bytes(data[i + 2:i + 4], "big")
        i += 2 + length
    raise ValueError("no SOF segment found")


def main() -> int:
    data = SOURCE.read_bytes()
    if not data.startswith(JPEG_MAGIC):
        print(f"error: {SOURCE} is not a JPEG file", file=sys.stderr)
        return 1
    if len(data) > 1_048_576:
        print(f"error: {SOURCE} is {len(data)} bytes, over the 1 MiB gate",
              file=sys.stderr)
        return 1
    width, height = jpeg_dimensions(data)
    if width > 1024 or height > 1024:
        print(f"error: {SOURCE} is {width}x{height}, over the 1024x1024 gate",
              file=sys.stderr)
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, TARGET)
    digest = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    print(f"wrote {TARGET} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
