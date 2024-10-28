#!/bin/bash
SCRIPT_DIR="$(dirname "$0")"
PARENT_DIR="$SCRIPT_DIR/.."

#（1）原始数据预处理，生成data/e2e/original下文件
E2E_PATH_Pre="$PARENT_DIR/preprocess/e2e_preprocessor.py"
echo "Preprocessing E2E original data"
python3 "$E2E_PATH_Pre"

#（2）对original数据进一步处理：shuffle、分割、并将table转换为后续通用的元组set形式，生成data/e2e下主文件
E2E_PATH_Further_Pre="$PARENT_DIR/data/data_manager.py"
echo "Preprocessing E2E data"
dataset_name="e2e"
resplit=1           # 是否忽略现有文件重新覆盖生成, 1时覆盖
python $E2E_PATH_Further_Pre --dataset_name $dataset_name \
                             --resplit $resplit

#（3）对生成data/e2e主文件根据KGs进行加工，形成ft和推理数据集，存放在Hybird/temp/e2e目录下
E2E_PATH_KGs="$PARENT_DIR/KGs/prompt_cores.py"
echo "Preprocessing E2E data"
if_static=1
python $E2E_PATH_KGs --dataset_name $dataset_name \
                     --if_static $if_static

echo "Preprocessing E2E finished, now you can ft or inference with data under Hybird/temp/e2e"

