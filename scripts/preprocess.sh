#!/bin/bash
SCRIPT_DIR="$(dirname "$0")"
PARENT_DIR="$SCRIPT_DIR/.."
CPL_PATH="$PARENT_DIR/preprocess/CPL_Processor/main.py"
E2E_PATH="$PARENT_DIR/preprocess/e2e_preprocessor.py"
Rotowire_PATH="$PARENT_DIR/preprocess/rotowire_preprocessor.py"


echo "Preprocessing CPL"
python3 "$CPL_PATH"

echo "Preprocessing E2E"
python3 "$E2E_PATH"

echo "Preprocessing Rotowire"
python3 "$Rotowire_PATH"