#!/usr/bin/env python3

"""Bitstream Vera Nerd Font Mono patching script

Usage:
    main.py --base=<base> --output=<output> <merge>...
    main.py (-h | --help)

Options:
    -h --help           Show this screen
    --base=<base>       URI to base Bitstream Vera font file
    --output=<output>   Filename of generated font
    <merge>...          URI to font file(s) to be merged
"""

import fontforge
import io
import os
import psMat
import requests
import sys
import tempfile
import zipfile
from docopt import docopt
from urllib.parse import urlparse
from wcwidth import wcwidth


class Font:
    def __init__(self, uri: str):
        self.uri: str = uri
        self.forge: fontforge.font = None
        self.path = None

    def open(self) -> fontforge.font:
        if self.forge is not None:
            return self.forge

        if os.path.exists(self.uri):
            # file path given
            self.path = self.uri
            return fontforge.open(self.uri)
        uri_from = self.uri.find("::http")
        if uri_from < 0:
            # direct URI to font file
            parsed_uri = urlparse(self.uri)
            filename = None
            uri = self.uri
        else:
            # zip file
            filename = self.uri[:uri_from]
            uri = self.uri[uri_from + 2 :]
        response = requests.get(uri)
        (handle, path) = tempfile.mkstemp(prefix="bitstream-vera-patch-")
        if uri_from < 0:
            handle.write(response.body)
        else:
            with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip_file:
                zip_info = zip_file.getinfo(filename)
                zip_info.filename = os.path.basename(path)
                zip_file.extract(zip_info, os.path.dirname(path))
        os.close(handle)
        self.forge = fontforge.open(path)
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


def new_font_name(font_name: str) -> str:
    return font_name.replace("Nerd Font", "Nerd Hybrid Font").replace(
        "NerdFont", "NerdHybridFont"
    )


if __name__ == "__main__":
    arguments = docopt(__doc__)
    font_bitstream = Font(arguments["--base"].strip())
    forge_bitstream = font_bitstream.open()

    # bitstream metrics
    vcentre_bitstream = (forge_bitstream.ascent - forge_bitstream.descent) / 2
    width_bitstream = font_bitstream.width()  # 1233
    vwidth_bitstream = font_bitstream.vwidth()  # 2048
    print(
        "Bitstream ascent: {}, descent: {}, width: {}, vwidth: {}, vcentre: {}".format(
            forge_bitstream.ascent,
            forge_bitstream.descent,
            width_bitstream,
            vwidth_bitstream,
            vcentre_bitstream,
        )
    )

    # adjust and merge
    for font_merge_uri in arguments["<merge>"]:
        print("Processing {}".format(font_merge_uri))
        font_merge = Font(font_merge_uri.strip())
        forge_merge = font_merge.open()

        glyph: fontforge.glyph
        for glyph in forge_merge.glyphs():
            if glyph.unicode <= 0:
                continue

            # adjust bearing
            glyph.left_side_bearing = 0
            glyph.right_side_bearing = 0
            if glyph.width == 0:
                continue

            # scale glyph
            print("Glyph U+{:02x} width: {}".format(glyph.unicode, glyph.width))
            column_width = wcwidth(chr(glyph.unicode))
            print("Glyph U+{:02x} column width: {}".format(glyph.unicode, column_width))
            scale_factor = width_bitstream / glyph.width * column_width
            scale = psMat.scale(scale_factor, scale_factor)
            glyph.transform(scale)

            # move upwards
            bounding = glyph.boundingBox()  # xmin,ymin,xmax,ymax
            print("Glyph U+{:02x} bounding: {}".format(glyph.unicode, bounding))
            vcentre_glyph = (bounding[3] - bounding[1]) / 2 + bounding[1]
            print("Glyph U+{:02x} vcentre: {}".format(glyph.unicode, vcentre_glyph))
            vshift = forge_bitstream.ascent / 2 - vcentre_glyph
            print("Glyph U+{:02x} vshift: {}".format(glyph.unicode, vshift))
            translate = psMat.translate(0, vshift)
            glyph.transform(translate)

            glyph.width = int(width_bitstream * column_width)

        forge_bitstream.mergeFonts(forge_merge, True)
        os.remove(font_merge.path)

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
    os.remove(font_bitstream.path)
