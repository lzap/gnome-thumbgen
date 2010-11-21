#!/bin/bash
echo -e "Gnome thumbnail generator\n\nhttps://github.com/lzap/gnome-thumbgen\n" > README
python src/gnome-thumbgen.py --help >> README
