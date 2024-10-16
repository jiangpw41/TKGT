#!/bin/bash
cd /home/jiangpeiwen2/jiangpeiwen2/workspace/TKGT
export CUDA_VISIBLE_DEVICES=3

PARENT_DIR=$(pwd)

model_num=1
file_name="微调模型$model_num结果(Prompt2text)"
rotowire_name="Hybird_RAG/2predict/rotowire"
script_name="llm_api_parallel.py"
post_name="post_precoss.py"

# : <<'END'
echo "开始执行预测"
predict_file="$PARENT_DIR/$rotowire_name/$script_name"

source activate vllm

python $predict_file --model_num $model_num


echo "预测完成，开始后处理$file_name"
post_file="$PARENT_DIR/$rotowire_name/$post_name"
source activate tkgt2
python $post_file --file_name $file_name --model_num $model_num

echo "后处理完毕，开始评估"

export CUDA_VISIBLE_DEVICES=3


dataset_type="rotowire"
# 项目根目录
eval_name="Hybird_RAG/3evaluation/evaluate.py"
eval_file="$PARENT_DIR/$eval_name"

python $eval_file --file_name $file_name --dataset_type $dataset_type

