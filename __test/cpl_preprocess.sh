#!/bin/bash
SCRIPT_DIR="$(dirname "$0")"
PARENT_DIR="$SCRIPT_DIR/.."


dataset_name="cpl"
resplit=1           # 是否忽略现有文件重新覆盖生成, 1时覆盖
source activate tkgt
: <<'END' 


#（1）原始数据预处理，生成data/e2e/original下文件
PATH_Pre="$PARENT_DIR/preprocess/cpl_preprocessor_3_times.py"
echo "Preprocessing Cpl original data"
python "$PATH_Pre"
END

#（2）对original数据进一步处理：shuffle、分割、并将table转换为后续通用的元组set形式，生成data/cpl下主文件
PATH_Further_Pre="$PARENT_DIR/data/data_manager.py"
echo "Preprocessing CPL data"


python $PATH_Further_Pre --dataset_name $dataset_name \
                        --resplit $resplit

#（3）在data/rotowire下生成规则分割文本
PATH_rule="$PARENT_DIR/data/load_ruled_texts.py"
echo "Preprocessing Cpl ruled text"
python $PATH_rule --dataset_name $dataset_name \


#（4）对生成data/e2e主文件根据KGs进行加工，形成ft和推理数据集，存放在Hybird/temp/e2e目录下
PATH_KGs="$PARENT_DIR/KGs/prompt_cores.py"
echo "Preprocessing CPL ft data and prompt"
if_static=1
python $PATH_KGs --dataset_name $dataset_name \
                --if_static $if_static

echo "Preprocessing CPL finished, now you can ft or inference with data under Hybird/temp/rotowire"

