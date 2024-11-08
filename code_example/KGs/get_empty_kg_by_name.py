import os
import sys
import importlib
from copy import deepcopy
from .KG_class import DomainKnowledgeGraph

_ROOT_PATH = os.path.abspath(__file__)
for i in range(2):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert( 0, _ROOT_PATH )
from config_loader import config_data, prompt_templates

def get_schema( dataset_name ):
    KGs_file_list = os.listdir( os.path.join(_ROOT_PATH, "KGs/dataset_KGs"))
    if dataset_name+".py" not in KGs_file_list:
        raise Exception(f"数据集{dataset_name}在{KGs_file_list}下不存在知识图谱结构文件！")
    else:
        sys.path.insert(0, os.path.join(_ROOT_PATH, "KGs/dataset_KGs"))
        module = importlib.import_module(dataset_name)
        kg_schema = getattr(module, 'kg_schema', None) 
        if kg_schema is not None and isinstance(kg_schema, dict):  
            return kg_schema  
        else:  
            raise ImportError(f"No valid 'kg_schema' dictionary found in module '{dataset_name}'") 
    
def return_kg( dataset_name, subtable_name=None):
    kg_schema = get_schema( dataset_name )
    if subtable_name==None:
        kg = DomainKnowledgeGraph( kg_schema, config_data["DATASET_MANAGE"][dataset_name]["language"] )
    else:
        new_kg_schema = deepcopy( kg_schema )
        new_kg_schema["entity"] = {
            subtable_name: kg_schema["entity"][subtable_name]
        }
        kg = DomainKnowledgeGraph( new_kg_schema, config_data["DATASET_MANAGE"][dataset_name]["language"] )
    return kg

