#!/bin/bash
# 一旦有命令返回非零状态，脚本就会退出
set -e

################################# 在此指定参数 ##############################################
dataset_name="rotowire"
prompt_list_name="data_cell_Team"    
#prompt_list_name="data_cell_Player"
#prompt_list_name="first_column_Team"    
#prompt_list_name="first_column_Player"
not_process=0                       # 0表示不进行非工程化处理not_process，即要进行后工程处理# 0代表False，court_name_rule=0, --not_process 1
subtable_name="Team"
sample_little=100
eval_type="multi_entity"           # e2e为"single_entity"

function getCurScriptFullPath {  
    local f=$(readlink -f "${BASH_SOURCE[0]}")  
    local d=$(dirname "$f")
    local hybird_path=$(dirname "$d")
    # export SCRIPT_FULL_PATH="$f"  
    export SCRIPT_DIR="$d"
}  

getCurScriptFullPath
cd $SCRIPT_DIR


echo "即将开始针对$dataset_info数据的$prompt_list_name部分进行后处理和评估"

source activate tkgt2
post_dir="$SCRIPT_DIR/predict/post_process.py"
python $post_dir --dataset_name $dataset_name \
                --prompt_list_name $prompt_list_name \
                --not_process $not_process \
                --subtable_name $subtable_name \
                # --sample_little $sample_little \

echo "后处理完成，进行评估"
eval_dir="$SCRIPT_DIR/evaluation/evaluate.py"
python $eval_dir --dataset $dataset_name \
                --part $prompt_list_name \
                --eval_type $eval_type

echo "评估完成"