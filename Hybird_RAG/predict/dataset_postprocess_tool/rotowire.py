_DATA_NAME = "e2e"
_ROLE = 'Restaurant'

from tqdm import tqdm
import numpy as np
import pickle
import argparse
import os
import sys

IF_VS = False

_ROOT_PATH = os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) ))
#_ROOT_PATH = "/home/jiangpeiwen2/jiangpeiwen2/workspace/TKGT"
sys.path.insert(0, _ROOT_PATH )
from Hybird_RAG.config import rotowire_total_team_name

#file_name ="trytry"
predict_list_path = os.path.join( _ROOT_PATH, "Hybird_RAG/2predict/rotowire/temp/predict_list.pickle")


model_2_label = {
    1: "labels_2_text",
    2: "labels_2_context",
    3: "labels_3_text",
    4: "labels_3_context",
}

# labels_list_path = "/home/jiangpeiwen2/jiangpeiwen2/workspace/TKGT/Hybird_RAG/3evaluation/predict_results/rotowire_results/labels_3_context.pickle"
# labels_list_path = "/home/jiangpeiwen2/jiangpeiwen2/workspace/TKGT/Hybird_RAG/3evaluation/predict_results/rotowire_results/labels_3.pickle"

rotowire_total_team_name_lower = []
for item in rotowire_total_team_name:
    rotowire_total_team_name_lower.append( item.strip().lower() ) 

def bad_filter( _home, _visit ):
    ret_home_visit = [ None, None]
    for i in range(2):
        name = [_home, _visit][i]
        if name in rotowire_total_team_name_lower:
            ret_home_visit[i] = name
            continue
        else:
            flag = 0
            for item in rotowire_total_team_name_lower:
                if name==item:
                    ret_home_visit[i] = item
                    flag = 1
                    break
                elif name in item or item in name:
                    ret_home_visit[i] = item
                    flag = 1
                    break
            if flag==0:
                ret_home_visit[i] = "<not found>"
    return ret_home_visit[0], ret_home_visit[1]

def post_process( file_name ):
    with open( predict_list_path, 'rb') as f:  
        predict_list_2 = pickle.load(f)
    with open( labels_list_path, 'rb') as f:  
        labels_list = pickle.load(f)
    predict_list = []
    for i in tqdm( range(0, len(predict_list_2), 2), desc="Rotowire Processing"):
        temp_set= set()
        _home = predict_list_2[i].strip()
        _visit = predict_list_2[i+1].strip()

        _home, _visit = bad_filter( _home, _visit )
        if _home != "<not found>":
            temp_set.add( ("Home team", predict_list_2[i].strip()))
        if _visit != "<not found>":
            temp_set.add( ("Visit team", predict_list_2[i+1].strip()))

        predict_list.append( temp_set )

    output_file_path = os.path.join( _ROOT_PATH, f'Hybird_RAG/3evaluation/predict_results/rotowire_results/{file_name}.pickle')
    with open(output_file_path, 'wb') as f:  
        # 使用pickle.dump()保存列表  
        pickle.dump((labels_list, predict_list), f) 

def post_process_single( file_name, model_num ):
    if model_num in [1, 2]:
        IF_VS = True
    elif model_num in [3, 4]:
        IF_VS = False

    labels_list_path = f"/home/jiangpeiwen2/jiangpeiwen2/workspace/TKGT/Hybird_RAG/3evaluation/predict_results/rotowire_results/{model_2_label[model_num]}.pickle"
    with open( predict_list_path, 'rb') as f:  
        predict_list_orignal = pickle.load(f)
    with open( labels_list_path, 'rb') as f:  
        labels_list_orignal = pickle.load(f)
    predict_list = []
    labels_list = []
    for i in tqdm( range( len(predict_list_orignal)), desc="Rotowire Processing"):
        temp_set= set()
        predict_results = predict_list_orignal[i].strip().lower()
        if IF_VS:
            if "vs " in predict_results:
                _home, _visit = predict_results.split("vs ")[0].strip(), predict_results.split("vs ")[1].strip()
                _home, _visit = bad_filter( _home, _visit )
                if _home !="<not found>":
                    temp_set.add( _home )
                if _visit !="<not found>":
                    temp_set.add( _visit )
        else:
            if "<not found>" in predict_results:
                continue
            elif "," in predict_results:
                temp_set.add(  predict_results.split(",")[0].strip()  )
                temp_set.add(  predict_results.split(",")[1].strip()  )
            else:
                temp_set.add(  predict_results.strip()  )
        predict_list.append( temp_set )
            # 处理标签中的bad information
        label = labels_list_orignal[i]
        temp_label = set()
        if IF_VS:
            for item in label:
                if item[1] not in ["bad information", "<NOT FOUND>", "not found"]:
                    temp_label.add( item[1].strip().lower())
        else:
            for item in label:
                if item not in ["bad information", "<NOT FOUND>", "not found"]:
                    temp_label.add( item.strip().lower())
        labels_list.append( temp_label )

    output_file_path = os.path.join( _ROOT_PATH, f'Hybird_RAG/3evaluation/predict_results/rotowire_results/{file_name}.pickle')
    with open(output_file_path, 'wb') as f:  
        # 使用pickle.dump()保存列表  
        pickle.dump((labels_list, predict_list), f)


if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description="Run script with external arguments")
    # 添加一个名为 --gpu_id 的参数
    #parser.add_argument('--part_id', type=int, required=True, help='ID of the GPU to use')
    #parser.add_argument('--part_num', type=int, required=True, help='ID of the GPU to use')
    parser.add_argument('--file_name', type=str, required=True, help='保存的文件名')
    parser.add_argument('--model_num', type=int, required=True, help='使用几号模型')
    # 解析命令行参数
    args = parser.parse_args()
    # 获取参数值
    file_name = args.file_name
    model_num = args.model_num
    '''
    model_num = 2
    file_name = "微调模型2(Prompt2context)"
    '''
    post_process_single(file_name, model_num)