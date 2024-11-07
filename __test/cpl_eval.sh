#!/bin/bash
# 一旦有命令返回非零状态，脚本就会退出
set -e

dataset_name="cpl"
prompt_list_name="data_cell_all"    
eval_type="multi_entity"

function getCurScriptFullPath {  
    local f=$(readlink -f "${BASH_SOURCE[0]}")  
    local d=$(dirname "$f")
    local hybird_path=$(dirname "$d")
    # export SCRIPT_FULL_PATH="$f"  
    export ROOT_PATH="$hybird_path"
}  



getCurScriptFullPath
echo "当前路径$ROOT_PATH"
cd $ROOT_PATH

source activate tkgt2
eval_dir="$ROOT_PATH/Hybird_RAG/evaluation/evaluate.py"
python $eval_dir --dataset $dataset_name \
                --part $prompt_list_name \
                --eval_type $eval_type

echo "评估完成"
