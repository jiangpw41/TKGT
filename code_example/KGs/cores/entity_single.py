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

_RAG_MODE =  "naive"  #"naive"

def Prepare_Data_SingleEntity( dataset_name, mode, subtable_name=None):
    """
    mode = "train" or "test"
    """
    kg, datas, ruled_texts, configs = load_shared( dataset_name, mode )
    texts, tables = datas[0],  get_tables_list( datas[1], part_name = None, subtable_name=None )       # table是二元组或三元组
    configs[ "rag_mode" ] = _RAG_MODE
    configs[ "dataset_name" ] = dataset_name
    configs["prompt_temp"] = configs["prompt_temps"]["SingleEntity"]
    

    # 遍历每个文档
    total_list = []
    for i in tqdm( range( len(texts) ), desc=f"数据集{dataset_name}准备{mode}数据"):
        configs["text"] = texts[i]
        configs["ruled_text"] = ruled_texts[i] if ruled_texts!=None else None
        table = tables[i]
        # KG实例化：如果是训练，用真实标签实例化，否则空实例化所有实体类型
        temp_kg = deepcopy( kg )
        if mode == "train":
            temp_kg.add_from_tuple( table, False, True)
        else:
            temp_kg.add_from_no_tuple( False, False )

        # 根据任务类型实例化prompt构造机
        promptconstructor = PromptConstructor( temp_kg, "SingleEntity", mode )      
        configs["entity_type"] = list( temp_kg.entity_type_info.keys() )[0]
        entity_num = temp_kg.instance_num[ configs["entity_type"] ][0]
        iterator = temp_kg.get_attr_iter( entity_num, "all" )

        # 遍历每个文档中的single entity，while True迭代
        prompt_list = promptconstructor.get_prompt_list( HybirdRAG_for_Context, iterator, **configs)
        if mode == "train":
            total_list.extend( prompt_list )
        else:
            total_list.append( prompt_list )
    if mode == "train":
        return total_list
    else:
        return ( tables, total_list)

def single_entity_main( dataset_name ):
    # FT
    print(f"开始构建{dataset_name}数据集DataCell部分的Fine-Tuning数据")
    ft_data = Prepare_Data_SingleEntity( dataset_name, "train" )         # len = 251986， List[], 7*35998
    save_path = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_all_all_ft.json")
    save_data( ft_data, save_path)
    # Test
    print(f"开始构建{dataset_name}数据集DataCell部分的Test数据对")
    labels, prompts = Prepare_Data_SingleEntity( dataset_name, "test" )      # 15428, List[List[7]]
    save_path_prompts = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_all_all_prompt_list.pickle")
    save_path_labels = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_all_all_label_list.pickle")
    save_data( prompts, save_path_prompts)
    save_data( labels, save_path_labels)


if __name__=="__main__":
    single_entity_main( "e2e" )