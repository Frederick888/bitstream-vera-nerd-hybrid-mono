# Bitstream Vera Patching Script

## What

Merge additional glyphs into Bitstream Vera.

## How

```
Bitstream Vera Nerd Font Mono patching script

Usage:
    main.py --base=<base> --output=<output> <merge>...
    main.py (-h | --help)

Options:
    -h --help           Show this screen
    --base=<base>       URI to base Bitstream Vera font file
    --output=<output>   Filename of generated font
    <merge>...          URI to font file(s) to be merged
```

Base and merge file URIs can be either local file paths or HTTP(S) URLs. If the
HTTP(S) URL points to a ZIP file, filename of the font file inside the ZIP can
be specified via `<filename>::<URL>`.

## Example

Merge `Noto Emoji` into `Bitstream Vera Sans Mono Nerd Font Complete Mono`:

```sh
./main.py \
    --base "Bitstream Vera Sans Mono Nerd Font Complete Mono.ttf::https://github.com/ryanoasis/nerd-fonts/releases/download/v2.1.0/BitstreamVeraSansMono.zip" \
    --output "./Bitstream Vera Sans Mono Nerd Hybrid Font Complete Mono.ttf" \
    "NotoEmoji-Regular.ttf::https://noto-website-2.storage.googleapis.com/pkgs/NotoEmoji-unhinted.zip"
```
