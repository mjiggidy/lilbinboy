#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR"

for f in *.qrc; do
	pyside6-rcc "$f" -o "../../src/lilbinboy/res/${f%.qrc}.py";
done;