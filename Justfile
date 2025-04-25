default: build_local

download:
    [[ ! -f ./BitstreamVeraSansMono.zip ]] && wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/BitstreamVeraSansMono.zip || true
    [[ ! -f ./NotoEmoji-unhinted.zip ]] && wget https://noto-website-2.storage.googleapis.com/pkgs/NotoEmoji-unhinted.zip || true
    [[ ! -f ./Symbola.pdf ]] && wget https://web.archive.org/web/20240107144224/https://dn-works.com/wp-content/uploads/2021/UFAS121921/Symbola.pdf || true

build_local: download
    pdfdetach -saveall Symbola.pdf
    ./main.py \
        --base "BitstromWeraNerdFontMono-Regular.ttf::file://$PWD/BitstreamVeraSansMono.zip" \
        --output "./Bitstream Vera Sans Mono Nerd Hybrid Font Complete Mono.ttf" \
        --categories "Co,Cs,Sc,Sk,Sm,So" \
        --monospace \
        "NotoEmoji-Regular.ttf::file://$PWD/NotoEmoji-unhinted.zip" \
        "./Symbola.otf"

build:
    ./main.py \
        --base "BitstromWeraNerdFontMono-Regular.ttf::https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/BitstreamVeraSansMono.zip" \
        --output "./Bitstream Vera Sans Mono Nerd Hybrid Font Complete Mono.ttf" \
        --categories "Co,Cs,Sc,Sk,Sm,So" \
        --monospace \
        "NotoEmoji-Regular.ttf::https://noto-website-2.storage.googleapis.com/pkgs/NotoEmoji-unhinted.zip" \
        "./Symbola.otf"

# vim: set filetype=just:
