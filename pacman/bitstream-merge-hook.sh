#!/usr/bin/env bash

while read -r trg; do
    case $trg in
    nerd-fonts-bitstream-vera-mono | ttf-bitstream-vera-mono-nerd)
        /usr/local/bin/bitstream-merge.py \
            --base '/usr/share/fonts/TTF/BitstromWeraNerdFontMono-Regular.ttf' \
            --output '/usr/local/share/fonts/Bitstream Vera Sans Mono Nerd Hybrid Font Complete Mono.ttf' \
            --categories 'Co,Cs,Sc,Sk,Sm,So' \
            'NotoEmoji-Regular.ttf::https://noto-website-2.storage.googleapis.com/pkgs/NotoEmoji-unhinted.zip' \
            'Symbola.otf::https://dn-works.com/wp-content/uploads/2020/UFAS-Fonts/Symbola.zip' 2>/dev/null
        ;;
    esac
done
