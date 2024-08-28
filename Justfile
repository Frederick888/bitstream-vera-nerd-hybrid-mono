default: build_local

download:
    [[ ! -f ./BitstreamVeraSansMono.zip ]] && wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/BitstreamVeraSansMono.zip || true
    [[ ! -f ./NotoEmoji-unhinted.zip ]] && wget https://noto-website-2.storage.googleapis.com/pkgs/NotoEmoji-unhinted.zip || true
    [[ ! -f ./Symbola.zip ]] && wget https://dn-works.com/wp-content/uploads/2020/UFAS-Fonts/Symbola.zip || true

build_local: download
    ./main.py \
        --base "BitstromWeraNerdFontMono-Regular.ttf::file://$PWD/BitstreamVeraSansMono.zip" \
        --output "./Bitstream Vera Sans Mono Nerd Hybrid Font Complete Mono.ttf" \
        --categories "Co,Cs,Sc,Sk,Sm,So" \
        --monospace \
        "NotoEmoji-Regular.ttf::file://$PWD/NotoEmoji-unhinted.zip" \
        "Symbola.otf::file://$PWD/Symbola.zip"

build:
    ./main.py \
        --base "BitstromWeraNerdFontMono-Regular.ttf::https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/BitstreamVeraSansMono.zip" \
        --output "./Bitstream Vera Sans Mono Nerd Hybrid Font Complete Mono.ttf" \
        --categories "Co,Cs,Sc,Sk,Sm,So" \
        --monospace \
        "NotoEmoji-Regular.ttf::https://noto-website-2.storage.googleapis.com/pkgs/NotoEmoji-unhinted.zip" \
        "Symbola.otf::https://dn-works.com/wp-content/uploads/2020/UFAS-Fonts/Symbola.zip"

# vim: set filetype=just:
