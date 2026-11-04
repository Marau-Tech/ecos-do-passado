#!/bin/bash
# Instala Blender portátil, venv e ffmpeg em tools/. Os pacotes do sistema estão no GUIA.md, em "Outro PC".
set -e
cd "$(dirname "$(readlink -f "$0")")"
BLENDER=4.5.15
mkdir -p tools
if [ ! -x tools/blender/blender ]; then
  curl -L "https://download.blender.org/release/Blender${BLENDER%.*}/blender-$BLENDER-linux-x64.tar.xz" | tar xJ -C tools
  mv "tools/blender-$BLENDER-linux-x64" tools/blender
fi
[ -d tools/venv ] || python3 -m venv tools/venv
tools/venv/bin/pip install -q -r requirements.txt
ln -sf "$(tools/venv/bin/python -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')" tools/ffmpeg
echo ok
