#!/bin/bash
SCRIPT_DIR="$(dirname "$0")"
PARENT_DIR="$SCRIPT_DIR/.."

# 先安装微调框架LLaMA-Factory，并准备chatglm3-6b或其他模型文件，替换下面两个路径
cd /home/jiangpeiwen2/jiangpeiwen2/workspace/LLaMA-Factory
echo "Current directory is: $(pwd)"
source activate llama_factory

number=3        # 多次微调的版本号
model_name_or_path="/home/jiangpeiwen2/.cache/modelscope/hub/ZhipuAI/chatglm3-6b"
output_dir="$PARENT_DIR/Hybird_RAG/ft_model/e2e/$number"
export_dir="$PARENT_DIR/Hybird_RAG/ft_model/e2e/merged/$number"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5
accelerate launch \
    --config_file examples/accelerate/single_config.yaml \
    src/train_bash.py \
    --stage sft \
    --do_train \
    --model_name_or_path $model_name_or_path \
    --dataset e2e_all_all_ft \
    --dataset_dir data \
    --template default \
    --finetuning_type lora \
    --lora_target query_key_value \
    --output_dir $output_dir \
    --overwrite_cache \
    --overwrite_output_dir \
    --cutoff_len 1024 \
    --preprocessing_num_workers 12 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --lr_scheduler_type cosine \
    --logging_steps 500 \
    --warmup_steps 500 \
    --save_steps 500 \
    --eval_steps 500 \
    --evaluation_strategy steps \
    --load_best_model_at_end \
    --learning_rate 5e-5 \
    --num_train_epochs 3.0 \
    --val_size 0.1 \
    --max_samples 100000 \
    --ddp_timeout 180000000 \
    --plot_loss \
    --fp16 \
    #--resume_from_checkpoint /home/jiangpeiwen2/jiangpeiwen2/workspace/TKGT/Hybird_RAG/0ft_data_prep/ft_models/8/checkpoint-12000 \

# wait:没有用&后台运行

echo "微调完成，开始merge"

export CUDA_VISIBLE_DEVICES=6

python src/export_model.py \
    --model_name_or_path $model_name_or_path \
    --adapter_name_or_path $output_dir \
    --template default \
    --finetuning_type lora \
    --export_dir $export_dir \
    --export_size 2 \
    --export_device cpu \
    --export_legacy_format False \

cp "$model_name_or_path/tokenizer_config.json" "$export_dir/tokenizer_config.json"
echo "merge完成"
