"""
处理最简单的数据集结构，如E2E，单个文档只涉及一个实体和多个静态属性，没有多级嵌套的动作等
"""
import os
import sys
from tqdm import tqdm

_ROOT_PATH = os.path.abspath(__file__)
for i in range(3):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert(0, _ROOT_PATH)
from KGs.cores.utils_kg_cores import load_shared, PromptConstructor, get_tables_list
from Hybird_RAG.retriever.Retriver import HybirdRAG_for_Context
from utils import load_data, save_data
from copy import deepcopy

_RAG_MODE =  "rule_based"  #"naive"


        

def Prepare_Data_FirstColumn( dataset_name, mode, subtable_name):
    """
    mode = "train" or "test"
    """
    kg, datas, ruled_texts, configs = load_shared( dataset_name, mode, subtable_name )
    texts, tables = datas[0],  get_tables_list( datas[1], part_name = "FirstColumn", subtable_name= subtable_name )      # table是二元组或三元组
    configs[ "rag_mode" ] = _RAG_MODE
    configs[ "dataset_name" ] = dataset_name
    configs["first_column"] = True
    configs["prompt_temp"] = configs["prompt_temps"]["FirstColumn"]
    configs["entity_list"] = list( kg.entity_type_info.keys() )
    # 根据任务类型实例化prompt构造机
    
    # 遍历每个文档
    total_list = []
    for i in tqdm( range( len(texts) ), desc=f"数据集{dataset_name}准备{mode}数据"):
        configs["text"] = texts[i]
        configs["ruled_text"] = ruled_texts[i] if ruled_texts!=None else None
        table = tables[i]
        # KG实例化：如果是训练，用真实标签实例化，否则空实例化所有实体类型
        temp_kg = deepcopy( kg )
        if mode == "train" and len(table)!=0:
            temp_kg.add_from_tuple( table, True, True)
        else:
            temp_kg.add_from_no_tuple( True, False )
        promptconstructor = PromptConstructor( temp_kg, "FirstColumn", mode ) 
        
        # 遍历每个文档中的single entity，while True迭代
        prompt_list = promptconstructor.get_prompt_list( HybirdRAG_for_Context, None, **configs)
        if mode == "train":
            total_list.extend( prompt_list )
        else:
            total_list.append( prompt_list )
    if mode == "train":
        return total_list
    else:
        return ( tables, total_list)


def multiple_entity_main( dataset_name ):
    # Rotowire
    if dataset_name == "rotowire":
        for subtable_name in ["Team", "Player"]:
            print(f"开始构建{dataset_name}数据集FirstColumn部分的子表{subtable_name}的Fine-Tuning数据")
            ft_data = Prepare_Data_FirstColumn( dataset_name, "train", subtable_name )         # len = 251986， List[], 7*35998
            save_path = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_first_column_{subtable_name}_ft.json")
            save_data( ft_data, save_path)
            # Test
            print(f"开始构建{dataset_name}数据集FirstColumn部分的子表{subtable_name}的Test数据对")
            labels, prompts = Prepare_Data_FirstColumn( dataset_name, "test", subtable_name  )      # 15428, List[List[7]]
            save_path_prompts = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_first_column_{subtable_name}_prompt_list.pickle")
            save_path_labels = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_first_column_{subtable_name}_label_list.pickle")
            save_data( prompts, save_path_prompts)
            save_data( labels, save_path_labels)
    elif dataset_name == "cpl":
        subtable_name = None
        print(f"开始构建{dataset_name}数据集FirstColumn部分的子表{subtable_name}的Fine-Tuning数据")
        ft_data = Prepare_Data_FirstColumn( dataset_name, "train", subtable_name )         # len = 251986， List[], 7*35998
        save_path = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_first_column_all_ft.json")
        save_data( ft_data, save_path)
        # Test
        print(f"开始构建{dataset_name}数据集FirstColumn部分的子表{subtable_name}的Test数据对")
        labels, prompts = Prepare_Data_FirstColumn( dataset_name, "test", subtable_name  )      # 15428, List[List[7]]
        save_path_prompts = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_first_column_all_prompt_list.pickle")
        save_path_labels = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_first_column_all_label_list.pickle")
        save_data( prompts, save_path_prompts)
        save_data( labels, save_path_labels)


if __name__=="__main__":
    multiple_entity_main( "rotowire" )