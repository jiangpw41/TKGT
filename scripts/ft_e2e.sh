cd /home/jiangpeiwen2/jiangpeiwen2/workspace/LLaMA-Factory
conda activate llama_factory

CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
accelerate launch \
    --config_file examples/accelerate/single_config.yaml \
    src/train_bash.py \
    --stage sft \
    --do_train \
    --model_name_or_path /home/jiangpeiwen2/.cache/modelscope/hub/ZhipuAI/chatglm3-6b \
    --dataset e2e_ft \
    --dataset_dir data \
    --template default \
    --finetuning_type lora \
    --lora_target query_key_value \
    --output_dir /home/jiangpeiwen2/jiangpeiwen2/workspace/TKGT/Hybird_RAG/ft_data_prep/ft_models/6 \
    --overwrite_cache \
    --overwrite_output_dir \
    --cutoff_len 1024 \
    --preprocessing_num_workers 16 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --lr_scheduler_type cosine \
    --logging_steps 1000 \
    --warmup_steps 200 \
    --save_steps 1000 \
    --eval_steps 1000 \
    --evaluation_strategy steps \
    --load_best_model_at_end \
    --learning_rate 5e-5 \
    --num_train_epochs 3.0 \
    --val_size 0.1 \
    --max_samples 200000 \
    --ddp_timeout 180000000 \
    --plot_loss \
    --fp16 \
    --resume_from_checkpoint  /home/jiangpeiwen2/jiangpeiwen2/workspace/TKGT/Hybird_RAG/ft_data_prep/ft_models/4/checkpoint-5500