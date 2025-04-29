#!/usr/bin/env python3

"""Bitstream Vera Nerd Font Mono patching script

Usage:
    main.py --base=<base> --output=<output> [--categories=<categories>] [--monospace] <merge>...
    main.py (-h | --help)

Options:
    -h --help                   Show this screen
    --base=<base>               URI to base Bitstream Vera font file
    --output=<output>           Filename of generated font
    --categories=<categories>   Unicode categories to merge (comma-separated), e.g. Lt,Ll,So
    --monospace                 Merge only single-columned glyphs
    <merge>...                  URI to font file(s) to be merged
"""

import fontforge
import io
import os
import psMat
import requests
import sys
import tempfile
import unicodedata
import zipfile
from docopt import docopt
from wcwidth import wcwidth
from requests_file import FileAdapter


class Font:
    def __init__(self, uri: str):
        self.uri: str = uri
        self.forge: fontforge.font = None
        self.path = None
        self.local: bool = False

    def open(self) -> fontforge.font:
        if self.forge is not None:
            return self.forge

        if os.path.exists(self.uri):
            # file path given
            self.path = self.uri
            self.local = True
            return fontforge.open(self.uri, ("hidewindow",))
        uri_from = self.uri.find("::http")
        if uri_from < 0:
            uri_from = self.uri.find("::file://")
        if uri_from < 0:
            # direct file path
            filename = None
            uri = self.uri
        else:
            # zip file
            filename = self.uri[:uri_from]
            uri = self.uri[uri_from + 2 :]

        s = requests.Session()
        s.mount("file://", FileAdapter())

        response = s.get(uri)
        (handle, path) = tempfile.mkstemp(prefix="bitstream-vera-patch-")
        if uri_from < 0:
            handle.write(response.body)
        else:
            with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip_file:
                zip_info = zip_file.getinfo(filename)
                zip_info.filename = os.path.basename(path)
                zip_file.extract(zip_info, os.path.dirname(path))
        os.close(handle)
        self.forge = fontforge.open(path, ("hidewindow",))
        self.path = path
        return self.forge

    def width(self) -> float:
        # assume monospace
        glyph: fontforge.glyph
        for glyph in self.open().glyphs():
            if glyph.unicode > 0:
                return glyph.width / wcwidth(chr(glyph.unicode))
        raise "No valid glyph found in {}".format(self.uri)

    def vwidth(self) -> float:
        return next(self.open().glyphs()).vwidth

    def cleanup(self):
        if not self.local:
            os.remove(self.path)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def new_font_name(font_name: str) -> str:
    return (
        font_name.replace("Nerd Font", "Nerd Hybrid Font")
        .replace("NerdFont", "NerdHybridFont")
        .replace("NFM", "NFHM")
    )


if __name__ == "__main__":
    arguments = docopt(__doc__)
    print("Base Bitstream is {}".format(arguments["--base"].strip()))
    monospace = arguments["--monospace"]
    font_bitstream = Font(arguments["--base"].strip())
    forge_bitstream = font_bitstream.open()

    forge_bitstream.encoding = "UnicodeFull"

    # bitstream metrics
    vcentre_bitstream = (forge_bitstream.ascent - forge_bitstream.descent) / 2
    width_bitstream = font_bitstream.width()  # 1233
    vwidth_bitstream = font_bitstream.vwidth()  # 2048
    eprint(
        "Bitstream ascent: {}, descent: {}, width: {}, vwidth: {}, vcentre: {}".format(
            forge_bitstream.ascent,
            forge_bitstream.descent,
            width_bitstream,
            vwidth_bitstream,
            vcentre_bitstream,
        )
    )

    # categories
    categories = set((arguments["--categories"] or "").strip().split(","))

    # adjust and merge
    for font_merge_uri in arguments["<merge>"]:
        print("Processing {}".format(font_merge_uri))
        font_merge = Font(font_merge_uri.strip())
        forge_merge = font_merge.open()

        glyph: fontforge.glyph
        if len(categories) > 0 or monospace:
            # select glyphs to be removed by font_merge.clear()
            forge_merge.selection.all()
            for glyph in forge_merge.glyphs():
                if glyph.unicode <= 0:
                    continue

                category = unicodedata.category(chr(glyph.unicode))
                if category not in categories:
                    eprint(
                        "Glyph U+{:02x} in category {} skipped as it doesn't belong in {}".format(
                            glyph.unicode, category, ", ".join(categories)
                        )
                    )
                    continue

                column_width = wcwidth(chr(glyph.unicode))
                if monospace and column_width != 1:
                    eprint(
                        "Glyph U+{:02x} in category {} skipped as it has column width {}".format(
                            glyph.unicode, category, column_width
                        )
                    )
                    continue

                eprint(
                    "Glyph U+{:02x} in {} marked for merging".format(
                        glyph.unicode, unicodedata.category(chr(glyph.unicode))
                    )
                )
                # deselect the glyph so that it's not cleared below
                forge_merge.selection.select(("less",), glyph)
            forge_merge.clear()
            forge_merge.selection.none()

        for glyph in forge_merge.glyphs():
            if glyph.unicode <= 0:
                continue

            # adjust bearing
            glyph.left_side_bearing = 0
            glyph.right_side_bearing = 0
            if glyph.width == 0:
                continue

            # scale glyph
            bounding = glyph.boundingBox()  # xmin,ymin,xmax,ymax
            eprint("Glyph U+{:02x} width: {}".format(glyph.unicode, glyph.width))
            column_width = wcwidth(chr(glyph.unicode))
            eprint(
                "Glyph U+{:02x} column width: {}".format(glyph.unicode, column_width)
            )
            scale_factor_horizontal = width_bitstream / glyph.width * column_width
            scale_horizontal = psMat.scale(scale_factor_horizontal)
            scale_factor_vertical = forge_bitstream.ascent / (bounding[3] - bounding[1])
            scale_vertical = psMat.scale(scale_factor_vertical)
            glyph.transform(
                scale_horizontal
                if scale_factor_horizontal <= scale_factor_vertical
                else scale_vertical
            )

            bounding = glyph.boundingBox()  # xmin,ymin,xmax,ymax
            eprint("Glyph U+{:02x} bounding: {}".format(glyph.unicode, bounding))

            # move upwards
            vcentre_glyph = (bounding[3] - bounding[1]) / 2 + bounding[1]
            eprint("Glyph U+{:02x} vcentre: {}".format(glyph.unicode, vcentre_glyph))
            vshift = forge_bitstream.ascent / 2 - vcentre_glyph
            eprint("Glyph U+{:02x} vshift: {}".format(glyph.unicode, vshift))
            translate = psMat.translate(0, vshift)
            glyph.transform(translate)

            # move rightwards
            hcentre_glyph = (bounding[2] - bounding[0]) / 2 + bounding[0]
            eprint("Glyph U+{:02x} hcentre: {}".format(glyph.unicode, hcentre_glyph))
            hshift = width_bitstream * column_width / 2 - hcentre_glyph
            eprint("Glyph U+{:02x} vshift: {}".format(glyph.unicode, hshift))
            translate = psMat.translate(hshift, 0)
            glyph.transform(translate)

            glyph.width = int(width_bitstream * column_width)

        forge_bitstream.mergeFonts(forge_merge, True)
        font_merge.cleanup()

    # produce new font
    attrs = [
        "familyname",
        "fontname",
        "fullname",
    ]
    for attr in attrs:
        setattr(forge_bitstream, attr, new_font_name(getattr(forge_bitstream, attr)))
    names = forge_bitstream.sfnt_names
    new_names = []
    for name in names:
        name = [new_font_name(ele) for ele in name]
        new_names.append(tuple(name))
    forge_bitstream.sfnt_names = tuple(new_names)

    forge_bitstream.generate(arguments["--output"])
    font_bitstream.cleanup()
