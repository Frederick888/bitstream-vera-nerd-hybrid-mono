#!/usr/bin/env python3

import fontforge
import re
import requests
import sys
import unicodedata

BLOCK_INFO_URL = "https://unicode.org/Public/UNIDATA/Blocks.txt"
BLOCK_LINE_RE = re.compile(r"^([0-9A-Z]+)\.\.([0-9A-Z]+); (.+)")


class UnicodeBlock:
    def __init__(self, info: str):
        match = BLOCK_LINE_RE.match(info)
        if match is None:
            raise RuntimeError(f"Invalid block {info}")
        self.start: int = int(match.group(1), 16)
        self.end: int = int(match.group(2), 16)
        self.name: str = match.group(3)


block_info = requests.get(BLOCK_INFO_URL)

blocks = []
for block in block_info.iter_lines():
    try:
        blocks.append(UnicodeBlock(block.decode("utf-8")))
    except:
        pass

path = sys.argv[1]
font: fontforge.font = fontforge.open(path, ("hidewindow",))
covered = set()
for glyph in font.glyphs():
    covered.add(glyph.unicode)

print("Coverage\tStart\tEnd\tTotal\tNum. Covered\tName")
for block in blocks:
    total = block.end - block.start + 1
    existing = sum(1 if c in covered else 0 for c in range(block.start, block.end + 1))
    print(
        "\t".join(
            map(
                str,
                [
                    "{:.1f}".format(existing / total * 100),
                    hex(block.start),
                    hex(block.end),
                    block.end - block.start + 1,
                    existing,
                    block.name,
                ],
            )
        )
    )
