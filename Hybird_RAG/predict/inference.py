"""
本文件为推理引擎的启动文件，唯一性标识为prompt_list_name，这个需要在准备时指定
"""
import argparse
import os
import sys
import subprocess
import json
import shutil

_Hybird_RAG_PATH = os.path.abspath(__file__)
for i in range(2):
    _Hybird_RAG_PATH = os.path.dirname( _Hybird_RAG_PATH )
sys.path.insert( 0, _Hybird_RAG_PATH)
from predict.LLMInferenceServer.server_gateway import inferencer



def path_check( dataset_name, prompt_list_name, model_name, offline_online):
    
    # 检查推理服务项目地址
    server_path = os.path.join( _Hybird_RAG_PATH, "predict/LLMInferenceServer")
    if not os.path.exists( server_path ):
        command = f'cd {_Hybird_RAG_PATH} && git clone git@github.com:jiangpw41/LLMInferenceServer.git'
        status = subprocess.run(command, shell=True, check=True)
        print("LLMInferenceServer下载完毕")
    else:
        print("LLMInferenceServer已存在")
    
    # 检查模型名称是否存在
    model_list_path = os.path.join( _Hybird_RAG_PATH, "ft_model/model_list.json")
    with open( model_list_path, "r", encoding="utf-8") as f:
        model_dicts = json.load(f)
    model_dict = model_dicts[ offline_online ][local_api]
    if model_name not in model_dict:
        model_path = ""
        raise Exception(f"Model {model_name} not exist, please check model list")
    else:
        model_path = model_dict[model_name]                                             # 获取模型路径

    if offline_online=="offline":
        # 提示词路径
        prompt_list_from_path = os.path.join( _Hybird_RAG_PATH, f"temp/{dataset_name}/{dataset_name}_{prompt_list_name}_prompt_list.pickle")
        if not os.path.exists(prompt_list_from_path):
            raise Exception(f"输入prompt文件{prompt_list_from_path}不存在，请检查传入参数！")
        
        predict_from_path = os.path.join( server_path, 'temp/predict_list.pickle')
        predict_to_path = os.path.join( _Hybird_RAG_PATH, f'temp/{dataset_name}/{dataset_name}_{prompt_list_name}_predict_list.pickle')
        return model_path, prompt_list_from_path, predict_from_path, predict_to_path
    else:
        return model_path, None, None, None


def main(
        dataset_name, 
        prompt_list_name, 
        model_name, 
        gpu_list_str, 
        offline_online="offline", 
        local_api = "local", 
        sample_little = None
):
    
    model_path, prompt_list_from_path, predict_from_path, predict_to_path = path_check( dataset_name, prompt_list_name, model_name, offline_online)
    
    config_str = f"{model_name}_{offline_online}_{local_api}"
    print( f"使用{config_str}在GPU{gpu_list_str}上推理{prompt_list_name}：")
    inferencer( offline_online, local_api, model_path, prompt_list_from_path, gpu_list_str, sample_little)                    # 进行推理
    if offline_online=="offline":
        shutil.copy2(predict_from_path, predict_to_path)                                    # 推理完毕：覆盖predict_list
    print("全部执行完毕")

if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description="Run script with external arguments")
    parser.add_argument('--dataset_name', type=str, required=False, help='提示词文件名')
    parser.add_argument('--prompt_list_name', type=str, required=False, help='提示词文件名')
    parser.add_argument('--offline_online', type=str, required=True, help='offline or online')
    parser.add_argument('--local_api', type=str, required=True, help='local model or api')
    parser.add_argument('--model_name', type=str, required=True, help='模型路径')
    parser.add_argument('--gpu_list', type=str, required=True, help='可用GPU列表')
    parser.add_argument('--sample_little', type=int, required=False, help='小样本快速获得结果')
    args = parser.parse_args()
    # 获取参数值
    dataset_name = args.dataset_name if args.dataset_name else None
    prompt_list_name = args.prompt_list_name if args.prompt_list_name else None
    offline_online = args.offline_online
    local_api = args.local_api
    model_name = args.model_name
    gpu_list_str = args.gpu_list
    sample_little = args.sample_little if args.sample_little else None
    """
    dataset_name = "cpl"         # "e2e"
    prompt_list_name = "data_cell_all"  # ""all_all
    offline_online = "offline"
    local_api = "local"
    model_name = "chatglm3-6b"
    gpu_list_str = "0,1,2,3,4,5"
    sample_little = 6
    """
    main(  dataset_name, prompt_list_name, model_name, gpu_list_str, offline_online, local_api, sample_little)