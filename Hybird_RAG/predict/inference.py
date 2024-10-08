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



def path_check( dataset_info, prompt_list_model_name ):
    # 检查推理服务项目地址
    server_path = os.path.join( _Hybird_RAG_PATH, "predict/LLMInferenceServer")
    if not os.path.exists( server_path ):
        command = f'cd {_Hybird_RAG_PATH} && git clone git@github.com:jiangpw41/LLMInferenceServer.git'
        status = subprocess.run(command, shell=True, check=True)
        print("LLMInferenceServer下载完毕")
    else:
        print("LLMInferenceServer已存在")
    
    # 检查模型名称是否存在
    model_list_path = os.path.join( _Hybird_RAG_PATH, "model_list.json")
    with open( model_list_path, "r", encoding="utf-8") as f:
        model_list = json.load(f)
    # 将cpl/table1/data_cell形式的指示信息拆分
    data_info = dataset_info.split("/")

    # 输入输出路径
    prompt_list_from_path = os.path.join( _Hybird_RAG_PATH, f"temp/{data_info[0]}/{data_info[1]}/{data_info[2]}/prompt_list/{prompt_list_model_name}.pickle")
    if not os.path.exists(prompt_list_from_path):
        raise Exception(f"输入prompt文件{prompt_list_from_path}不存在，请检查传入参数！")
    prompt_list_to_path = os.path.join( _Hybird_RAG_PATH, 'temp/prompt_list.pickle')
    predict_from_path = os.path.join( _Hybird_RAG_PATH, 'temp/predict_list.pickle')
    predict_to_path = os.path.join( _Hybird_RAG_PATH, f"temp/{data_info[0]}/{data_info[1]}/{data_info[2]}/predict_list/{prompt_list_model_name}.pickle")
    # 构建预测结果
    return model_list, data_info, prompt_list_from_path, prompt_list_to_path, predict_from_path, predict_to_path


def main(
        prompt_list_name, 
        model_name, 
        gpu_list_str, 
        dataset_info, 
        offline_online="offline", 
        local_api = "local", 
):
    model_list, data_info, prompt_list_from_path, prompt_list_to_path, predict_from_path, predict_to_path = path_check( dataset_info, prompt_list_name+"_"+model_name)
    shutil.copy2( prompt_list_from_path, prompt_list_to_path)                           # 准备推理：覆盖prompt_list
    
    model_dict = model_list[ offline_online ][local_api]
    if model_name not in model_dict:
        model_path = ""
        raise Exception(f"Model {model_name} not exist, please check model list")
    else:
        model_path = model_dict[model_name]                                             # 获取模型路径
    
    config_str = f"{model_name}_{offline_online}_{local_api}_{data_info}"
    print( f"使用{config_str}在GPU{gpu_list_str}上推理{prompt_list_name}：")
    inferencer( offline_online, local_api, model_path, gpu_list_str)                    # 进行推理
    
    shutil.copy2(predict_from_path, predict_to_path)                                    # 推理完毕：覆盖predict_list

if __name__=="__main__":
    """
    parser = argparse.ArgumentParser(description="Run script with external arguments")
    parser.add_argument('--prompt_list_name', type=str, required=True, help='提示词文件名')
    parser.add_argument('--offline_online', type=str, required=True, help='offline or online')
    parser.add_argument('--local_api', type=str, required=True, help='local model or api')
    parser.add_argument('--model_name', type=str, required=True, help='模型路径')
    parser.add_argument('--gpu_list', type=str, required=False, help='可用GPU列表')
    parser.add_argument('--dataset_info', type=str, required=False, help='表示独特性的字符串')
    args = parser.parse_args()
    # 获取参数值
    
    prompt_list_name = args.prompt_list_name
    offline_online = args.offline_online
    local_api = args.local_api
    model_name = args.model_name
    gpu_list_str = args.gpu_list
    dataset_info = args.dataset_info
    """
    prompt_list_name = "prompt_list_rag"
    offline_online = "offline"
    local_api = "local"
    dataset_info = "cpl/table1/first_column"
    model_name = "chatglm3-6b"
    gpu_list_str = "0,1,2,3,4,5,6,7"

    main(  prompt_list_name, model_name, gpu_list_str, dataset_info, offline_online, local_api)