#!/bin/bash
# 一旦有命令返回非零状态，脚本就会退出
set -e

prompt_list_name="prompt_list_rag"
offline_online="offline"
local_api="local"
dataset_info="cpl/table1/first_column"
model_name="chatglm3-6b"
gpu_list_str="0,1,2,3,4,5,6,7"

function getCurScriptFullPath {  
    local f=$(readlink -f "${BASH_SOURCE[0]}")  
    local d=$(dirname "$f")
    local hybird_path=$(dirname "$d")
    # export SCRIPT_FULL_PATH="$f"  
    export SCRIPT_DIR="$d"
}  

getCurScriptFullPath
cd $SCRIPT_DIR


echo "即将开始针对$dataset_info数据，使用$prompt_list_name提示词文件，在$model_name模型上执行分治多GPU推理"

# << 'Comment' Comment

################################并行推理###########################################


################################并行推理###########################################

echo "所有预测任务已完成，进行后处理"
source activate tkgt2
post_dir="$SCRIPT_DIR/predict/post_process.py"
not_process=0
# 0代表False，court_name_rule=0, --not_process 1
python $post_dir --prompt_list_name $prompt_list_name \
                --dataset_info $dataset_info \
                --model_name $model_name \
                --not_process $not_process \

source activate tkgt2
echo "后处理完成，进行评估"
eval_dir="$SCRIPT_DIR/evaluation/evaluate.py"
python $eval_dir --prompt_list_name $prompt_list_name \
                --dataset_info $dataset_info \
                --model_name $model_name \

echo "评估完成"