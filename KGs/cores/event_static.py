"""
处理datacell，基于获得entity信息这一前提，遍历所有实体对象获得其属性
（1）train: 实体信息来自于标签
（2）text：实体信息来自于预测结果，但如果将两部分分开，则也可以使用标签
使用方法为，用tuple集合初始化知识图谱
"""
import os
import sys
from tqdm import tqdm

_ROOT_PATH = os.path.abspath(__file__)
for i in range(3):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert(0, _ROOT_PATH)
from KGs.cores.utils_kg_cores import load_shared, PromptConstructor, get_tables_list
from KGs.dataset_KGs.cpl import Plaintiff_claim_attributes
from Hybird_RAG.retriever.Retriver import HybirdRAG_for_Context
from Hybird_RAG.retriever.cpl_utils import get_ruled_core_cpl

from Hybird_RAG.retriever.vector_retriever import get_ready_vector_index_list
from Hybird_RAG.retriever.keyword_retriever import Keyword_Retriever
from utils import load_data, save_data
from copy import deepcopy

_RAG_MODE =  "rule_based"  #"naive" rule_based, hybird

def filter_ban( tables ):
    new_table_list = []
    for i in range(len(tables)):
        temp = set()
        for item in tables[i]:
            if item[1] in Plaintiff_claim_attributes:
                temp.add( item )
        new_table_list.append( temp )
    return new_table_list

def load_hybird( ):
    retriever_list, ret_index = Keyword_Retriever.get_ready_keyword_index_list()
    vector_retriever_list = get_ready_vector_index_list( "test")
    return (retriever_list, vector_retriever_list)

def Prepare_DataCell_Static_For_Objects( dataset_name, mode, subtable_name, entity_list=None):
    """
    mode："train" or "test"
    subtable_name可以为None，非None时表示子表的名称
    entity_list：如果非None，则说明两部分接续获得结果使用预测获得的entity信息，为None则DataCell使用标签中的entity信息
    """
    kg, datas, ruled_texts, configs = load_shared( dataset_name, mode, subtable_name )      # type: ignore
    texts, tables = datas[0],  get_tables_list( datas[1], part_name = "DataCell", subtable_name= subtable_name )      # 两者为等长的列表，text-table pair
    
    if dataset_name == "cpl":
        tables = filter_ban( tables )
    # 如果没有传入的entity_list，说明First和Cell两部分预测是独立的，需要从标签加载先验的entity_list；否则entity_list代表预测结果
    if entity_list == None:
        temp = load_shared( dataset_name, mode, subtable_name, only_data=True )[1]      # type: ignore
        entity_list = get_tables_list( temp, part_name = "FirstColumn", subtable_name= subtable_name )
    configs["entity_list"] = entity_list
    configs[ "rag_mode" ] = _RAG_MODE
    configs[ "dataset_name" ] = dataset_name
    configs["first_column"] = False
    configs["prompt_temp"] = configs["prompt_temps"]["DataCell"]
    _name_ = "Name" if kg.language == "EN" else "姓名名称"
    if _RAG_MODE == "hybird":
        hybird_retriever = load_hybird()
    elif _RAG_MODE == "rule_based":
        ruled_texts = get_ruled_core_cpl( mode)
    # 遍历每个文档
    total_list = []
    for i in tqdm( range( len(texts) ), desc=f"数据集{dataset_name}准备{mode}数据"):
        configs["text"] = texts[i]
        if _RAG_MODE == "rule_based":
            configs["ruled_text"] = ruled_texts[i] if ruled_texts!=None else None
        elif _RAG_MODE == "hybird":
            configs["hybird"] = (hybird_retriever[0][i], hybird_retriever[1][i])
        configs["index"] = i
        entities = entity_list[i]
        temp_kg = deepcopy( kg )
        if mode == "train":                                 # KG实例化：如果是训练，用两部分真实标签实例化
            entities.update( tables[i] )                        # 向entity标签加入当前datacell标签
            if_train = True
        else:
            if_train = False
        temp_list = []
        if len(entities)!=0:
            temp_kg.add_from_tuple( entities, True, if_train)
            promptconstructor = PromptConstructor( temp_kg, "DataCell", mode ) 
            # 遍历所有实例对象
            
            for entity_type in temp_kg.entity_type_info.keys():
                configs["entity_type"] = entity_type
                configs["predicate"] = temp_kg.entity_type_info[entity_type]["predicate"]
                for instance_num in temp_kg.instance_num[ entity_type ]:
                    iterator = temp_kg.get_attr_iter( instance_num, "cell" )
                    entity_name = temp_kg.get_info( instance_num, single=True, node=True )[_name_]["value"]
                    configs["entity_type_with_name"] = entity_type + f" ({entity_name})"
                    prompt_list = promptconstructor.get_prompt_list( HybirdRAG_for_Context, iterator, **configs)
                    temp_list.extend( prompt_list)
        if mode == "train":
            total_list.extend( temp_list )
        else:
            total_list.append( temp_list )
    if mode == "train":
        return total_list
    else:
        return ( tables, total_list)


def static_event_main( dataset_name ):
    # Rotowire
    if dataset_name == "rotowire":
        for subtable_name in ["Team", "Player"]:
            print(f"开始构建{dataset_name}数据集FirstColumn部分的子表{subtable_name}的Fine-Tuning数据")
            ft_data = Prepare_DataCell_Static_For_Objects( dataset_name, "train", subtable_name )         # len = 251986， List[], 7*35998
            save_path = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_data_cell_{subtable_name}_ft.json")
            save_data( ft_data, save_path)
            # Test
            print(f"开始构建{dataset_name}数据集FirstColumn部分的子表{subtable_name}的Test数据对")
            labels, prompts = Prepare_DataCell_Static_For_Objects( dataset_name, "test", subtable_name  )      # 15428, List[List[7]]
            save_path_prompts = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_data_cell_{subtable_name}_prompt_list.pickle")
            save_path_labels = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_data_cell_{subtable_name}_label_list.pickle")
            save_data( prompts, save_path_prompts)
            save_data( labels, save_path_labels)
    elif dataset_name == "cpl":
        subtable_name = None
        """"""
        print(f"开始构建{dataset_name}数据集FirstColumn部分的子表{subtable_name}的Fine-Tuning数据")
        ft_data = Prepare_DataCell_Static_For_Objects( dataset_name, "train", subtable_name )         # len = 251986， List[], 7*35998
        save_path = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_data_cell_all_ft.json")
        save_data( ft_data, save_path)
        
        # Test
        print(f"开始构建{dataset_name}数据集FirstColumn部分的子表{subtable_name}的Test数据对")
        labels, prompts = Prepare_DataCell_Static_For_Objects( dataset_name, "test", subtable_name  )      # 15428, List[List[7]]
        save_path_prompts = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_data_cell_all_prompt_list.pickle")
        save_path_labels = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_data_cell_all_label_list.pickle")
        save_data( prompts, save_path_prompts)
        save_data( labels, save_path_labels)


if __name__=="__main__":
    static_event_main( "cpl" )