#!/bin/sh
# builds dist/founder.pyz, one file that carries the code and chromadb, numpy and onnxruntime with it.
# it runs wherever the same python minor version, os and cpu are (the wheels inside are native), and
# unpacks itself into ~/.shiv on the first run, which takes a few seconds. data, state and .env are looked
# for in FOUNDER_HOME, or in the current directory: they are not inside the file
set -e
cd "$(dirname "$0")/.."
python3 -m venv .build-venv
.build-venv/bin/pip install -q shiv
mkdir -p dist
.build-venv/bin/shiv -c founder -o dist/founder.pyz --python '/usr/bin/env python3' .
rm -rf .build-venv
ls -lh dist/founder.pyz
