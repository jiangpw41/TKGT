#!/bin/bash
# 一旦有命令返回非零状态，脚本就会退出
set -e

################################# 在此指定参数 ##############################################
dataset_name="e2e"
prompt_list_name="all_all"    
eval_type="single_entity"           # e2e为"single_entity"

export CUDA_VISIBLE_DEVICES=6

function getCurScriptFullPath {  
    local f=$(readlink -f "${BASH_SOURCE[0]}")  
    local d=$(dirname "$f")
    local hybird_path=$(dirname "$d")
    # export SCRIPT_FULL_PATH="$f"  
    export SCRIPT_DIR="$d"
}  

getCurScriptFullPath
cd $SCRIPT_DIR
source activate tkgt2
eval_dir="$SCRIPT_DIR/evaluate.py"
python $eval_dir --dataset $dataset_name \
                --part $prompt_list_name \
                --eval_type $eval_type

echo "评估完成"