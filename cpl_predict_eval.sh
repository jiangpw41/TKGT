#!/bin/bash
# 一旦有命令返回非零状态，脚本就会退出
set -e

dataset_name="cpl"
prompt_list_name="first_column_all"    
offline_online="offline"
local_api="local"
model_name="chatglm3-6b-cpl_firstcolumn_12"
gpu_list_str="0,1,2,3,4,5"
sample_little=300

not_process=0                       # 0表示不进行非工程化处理not_process，即要进行后工程处理# 0代表False，court_name_rule=0, --not_process 1
subtable_name=None


function getCurScriptFullPath {  
    local f=$(readlink -f "${BASH_SOURCE[0]}")  
    local d=$(dirname "$f")
    local hybird_path=$(dirname "$d")
    # export SCRIPT_FULL_PATH="$f"  
    export ROOT_PATH="$d"
}  



getCurScriptFullPath
echo "当前路径$ROOT_PATH"
cd $ROOT_PATH


#########################################评估datacell##############################################
#!/bin/bash
# 一旦有命令返回非零状态，脚本就会退出
set -e

dataset_name="cpl"
prompt_list_name="data_try_cell_all"    
offline_online="offline"
local_api="local"
model_name="chatglm3-6b-cpl_datacell_3"



: <<'END' 
echo "即将开始针对$dataset_info数据，使用$prompt_list_name提示词文件，使用$model_name模型在GPU$gpu_list_str上执行$sample_little样本任务"
vllm_server_dir="$ROOT_PATH/Hybird_RAG/predict/inference.py"
source activate vllm
          # cpl的datacell为"single_entity"
python $vllm_server_dir --dataset_name $dataset_name \
                        --prompt_list_name $prompt_list_name \
                        --offline_online $offline_online \
                        --local_api $local_api \
                        --model_name $model_name \
                        --gpu_list $gpu_list_str \
                        #--sample_little $sample_little \

echo "即将开始针对$dataset_info数据的$prompt_list_name部分进行后处理和评估"

source activate tkgt2
eval_type="multiple_entity" 
prompt_list_name="data_cell_all"  
post_dir="$ROOT_PATH/Hybird_RAG/predict/post_process.py"
python $post_dir --dataset_name $dataset_name \
                --prompt_list_name $prompt_list_name \
                --subtable_name $subtable_name \
                --not_process $not_process \
                #--sample_little $sample_little \
END
prompt_list_name="data_cell_all" 
echo "后处理完成，进行评估"
source activate tkgt2
eval_dir="$ROOT_PATH/Hybird_RAG/evaluation/evaluate.py"
python $eval_dir --dataset $dataset_name \
                --part $prompt_list_name \
                --eval_type $eval_type

echo "评估完成"
