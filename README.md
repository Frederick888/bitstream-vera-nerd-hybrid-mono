# Bitstream Vera Patching Script

## What

Merge additional glyphs into Bitstream Vera.

## How

```
Bitstream Vera Nerd Font Mono patching script

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
```

Base and merge file URIs support `http(s)://` and `file://` schemes. If the URI
points to a ZIP file, `<filename>::<URI>` can be used to specify a file in it.
Note that `file://` must be followed by an absolute path.

Absolute and relative paths to font files can also be used directly. ZIP is not
supported in this case.

## Example

Merge `Noto Emoji` and `Symbola` into `Bitstream Vera Sans Mono Nerd Font Complete Mono`:

```sh
./main.py \
    --base "BitstromWeraNerdFontMono-Regular.ttf::https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/BitstreamVeraSansMono.zip" \
    --output "./Bitstream Vera Sans Mono Nerd Hybrid Font Complete Mono.ttf" \
    --categories "Co,Cs,Sc,Sk,Sm,So" \
    --monospace \
    "NotoEmoji-Regular.ttf::https://noto-website-2.storage.googleapis.com/pkgs/NotoEmoji-unhinted.zip" \
    "Symbola.otf::https://dn-works.com/wp-content/uploads/2020/UFAS-Fonts/Symbola.zip"
```
