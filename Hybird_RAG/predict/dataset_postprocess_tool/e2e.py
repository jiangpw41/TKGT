_DATA_NAME = "e2e"
_ROLE = 'Restaurant'

from tqdm import tqdm
import numpy as np
import pickle
import argparse
import os
import sys


_ROOT_PATH = os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) ))
#_ROOT_PATH = "/home/jiangpeiwen2/jiangpeiwen2/workspace/TKGT"
sys.path.insert(0, _ROOT_PATH )
from Hybird_RAG.functions import Get_Fields, Label_Process, replace_bad_info
from KGs.dataset_kgs.e2e_rotowire_field import fields_list_e2e


input_file_path = os.path.join( _ROOT_PATH,  f'Hybird_RAG/2predict/temp')


def post_process( file_name, dataset_type, part_num, option):
    #（1）处理标签数据：(字段名、值)，已小写、考虑option、bad info
    if dataset_type=='e2e':
        kg_field_dict = fields_list_e2e['Table1']["Fields"]
    elif dataset_type=='cpl':
        kg_field_dict = []
    label_dict = Label_Process(dataset_type, kg_field_dict, option )

    #（2）处理预测数据：合并分开处理的部分
    predict_dict = {}
    for i in range(part_num):                       # 预测值
        with open( os.path.join( input_file_path, str(i)), 'rb') as f:  
            part_data = pickle.load(f)
        for key, value in part_data.items():
            predict_dict[key] = value

    if len( label_dict )!=len( predict_dict ):
        raise Exception(f"Length of table {len( label_dict )} and text {len( predict_dict )} not equal")
    else:
        print( f"Text length: {len( predict_dict )}, table length {len( label_dict )}" )

    #（3）处理预测数据：不处理bad information
    fields_list = Get_Fields( dataset_type )                # 字段整体
    option_fields_list = Get_Fields( dataset_type, True )   # 为选项的字段部分
    for i in tqdm(range(len(predict_dict)), desc='Predict Results Processing'):
        single_sample_predict = predict_dict[i]             # 单个样本的预测结果（字符串列表）
        temp_dict = set()
        for j in range(len(fields_list)):
            #并行处理的结果是每个sample一个列表返回
            _field = fields_list[j]                         # 当前字符串对应的字段
            _value = single_sample_predict[j]               # 字符串（未小写）
            _scope = kg_field_dict[ _field ]                # 取值范围
            if option:
                # 在选项模式下，如果字段是选项型的，但回答却不是abcd，则舍弃
                if _field in option_fields_list and len(_value)>1:
                    continue
            _value = replace_bad_info( _value.strip().lower(), dataset_type)
            temp_dict.add( (_field.strip().lower(), _value) )
        predict_dict[i] = temp_dict

    output_file_path = os.path.join( _ROOT_PATH,  f'Hybird_RAG/3evaluation/predict_results/{_DATA_NAME}_results/{file_name}.pickle')
    with open(output_file_path, 'wb') as f:  
        # 使用pickle.dump()保存列表  
        pickle.dump((label_dict, predict_dict), f) 

def post_process_name( file_name, dataset_type, part_num, option):
    #（1）处理标签数据：(字段名、值)，已小写、考虑option、bad info
    if dataset_type=='e2e':
        kg_field_dict = fields_list_e2e['Table1']["Fields"]
    elif dataset_type=='cpl':
        kg_field_dict = []
    label_dict = Label_Process(dataset_type, kg_field_dict, option )

    #（2）处理预测数据：合并分开处理的部分
    name_path = "/home/jiangpeiwen2/jiangpeiwen2/workspace/TKGT/Hybird_RAG/3evaluation/predict_results/e2e_results/name_predict.pickle"
    with open(name_path, 'rb') as f:  
        # 使用pickle.load()加载列表  
        name_list = pickle.load(f)

    predict_dict = {}
    index = 0
    for i in range(part_num):                       # 预测值
        with open( os.path.join( input_file_path, str(i)), 'rb') as f:  
            part_data = pickle.load(f)
        
        for key, value in part_data.items():
            if False:
                if len(value)==12:
                    predict_dict[index] = value[:6]
                    index+=1
                    predict_dict[index] = value[6:]
                    index+=1
                elif len(value)==6:
                    predict_dict[index] = value
                    index+=1
                elif len(value)==0:
                    continue
            else:
                predict_dict[key] = value
            


    if len( label_dict )!=len( predict_dict ):
        raise Exception(f"Length of table {len( label_dict )} and text {len( predict_dict )} not equal")
    else:
        print( f"Text length: {len( predict_dict )}, table length {len( label_dict )}" )

    #（3）处理预测数据：不处理bad information
    fields_list = Get_Fields( dataset_type )                # 字段整体
    option_fields_list = Get_Fields( dataset_type, True )   # 为选项的字段部分
    for i in tqdm(range(len(predict_dict)), desc='Predict Results Processing'):
        pre_name = None
        for item in name_list[i]:
            pre_name = item[1]
            break
        single_sample_predict = predict_dict[i]             # 单个样本的预测结果（字符串列表）
        temp_dict = set()
        temp_dict.add( ("name", pre_name) )
        for j in range(len(fields_list[1:])):
            #并行处理的结果是每个sample一个列表返回
            _field = fields_list[1:][j]                         # 当前字符串对应的字段
            _value = single_sample_predict[j]               # 字符串（未小写）
            if option:
                # 在选项模式下，如果字段是选项型的，但回答却不是abcd，则舍弃
                if _field in option_fields_list and len(_value)>1:
                    continue
            _value = replace_bad_info( _value.strip().lower(), dataset_type)
            temp_dict.add( (_field.strip().lower(), _value) )
        predict_dict[i] = temp_dict

    output_file_path = os.path.join( _ROOT_PATH,  f'Hybird_RAG/3evaluation/predict_results/{_DATA_NAME}_results/{file_name}.pickle')
    with open(output_file_path, 'wb') as f:  
        # 使用pickle.dump()保存列表  
        pickle.dump((label_dict, predict_dict), f) 

if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description="Run script with external arguments")
    # 添加一个名为 --gpu_id 的参数
    parser.add_argument('--file_name', type=str, required=True, help='Description of data')
    parser.add_argument('--dataset_type', type=str, required=True, help='Dataset Type')
    parser.add_argument('--part_num', type=int, required=True, help='Number of predict parts to merge')
    parser.add_argument('--option', type=int, required=True, help='是否以选项标签的形式')
    # 解析命令行参数
    args = parser.parse_args()
    # 获取参数值
    file_name = args.file_name
    dataset_type = args.dataset_type
    part_num = args.part_num
    option = args.option
    """
    file_name = "数据集e2e模型号7提示词模板2单独name选项0"
    part_num = 5
    dataset_type ="e2e"
    option = 0
    """
    post_process(file_name, dataset_type, part_num, option)