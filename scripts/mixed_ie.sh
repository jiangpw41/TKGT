#!/bin/bash
SCRIPT_DIR="$(dirname "$0")"
PARENT_DIR="$SCRIPT_DIR/.."
Regulation_PATH="$PARENT_DIR/Mixed_IE/regulation/main.py"
Statistics_CPL_PATH="$PARENT_DIR/Mixed_IE/statistic/zh/statistic.py"
Statistics_Four_PATH="$PARENT_DIR/Mixed_IE/statistic/en/text_statistic.py"

echo "Regulation Splitting of CPL"
python3 "$Regulation_PATH"

echo "Statistics of CPL"
python3 "$Statistics_CPL_PATH"

echo "Statistics of Four Previous Datasets"
python3 "$Statistics_Four_PATH"