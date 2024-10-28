#!/bin/bash
# 一旦有命令返回非零状态，脚本就会退出
set -e

dataset_name="e2e"
prompt_list_name="all_all"    
offline_online="offline"
local_api="local"
model_name="chatglm3-6b-e2e_100000_3"
gpu_list_str="0,1,2,3,4,5"
sample_little=300


function getCurScriptFullPath {  
    local f=$(readlink -f "${BASH_SOURCE[0]}")  
    local d=$(dirname "$f")
    local hybird_path=$(dirname "$d")
    # export SCRIPT_FULL_PATH="$f"  
    export SCRIPT_DIR="$d"
}  

getCurScriptFullPath
cd $SCRIPT_DIR


echo "即将开始针对$dataset_info数据，使用$prompt_list_name提示词文件，使用$model_name模型在GPU$gpu_list_str上执行$sample_little样本任务"
vllm_server_dir="$SCRIPT_DIR/inference.py"
source activate vllm

python $vllm_server_dir --dataset_name $dataset_name \
                        --prompt_list_name $prompt_list_name \
                        --offline_online $offline_online \
                        --local_api $local_api \
                        --model_name $model_name \
                        --gpu_list $gpu_list_str \
                        --sample_little $sample_little \