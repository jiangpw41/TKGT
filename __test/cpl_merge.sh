cd /home/jiangpeiwen2/jiangpeiwen2/workspace/LLaMA-Factory
echo "Current directory is: $(pwd)"
source activate llama_factory

number=1
model_name_or_path="/home/jiangpeiwen2/.cache/modelscope/hub/ZhipuAI/chatglm3-6b"
output_dir="/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/ft_model/cpl/data_cell/$number/checkpoint-13200"
export_dir="/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/ft_model/cpl/data_cell/merged/$number"
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

