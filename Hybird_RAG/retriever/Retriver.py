
import os
import sys
from collections import OrderedDict

_ROOT_PATH = os.path.abspath(__file__)
for _ in range(3):
    _ROOT_PATH = os.path.dirname( _ROOT_PATH )
sys.path.insert(0, _ROOT_PATH)
from data.data_manager import data_split
from utils import load_data, save_data
from Hybird_RAG.retriever.HybirdRAG import HybirdRAG_v1

def get_ruled_context( entity, attr, **args ):
    ruled_text = args["ruled_text"]
    if args[ "dataset_name" ] == "cpl":
        if args["first_column"]:
            context = f"""标题: {ruled_text["标题"]} {str(ruled_text["开头"])}；
                        程序信息：{ruled_text["正文"]["程序信息"]}"""
        else:
            context = f"""原告申诉、被告辩称、法院裁定三方信息: 
                        {ruled_text["正文"]["申辩证"]}"""
        return context
    elif args[ "dataset_name" ] == "rotowire":
        return ruled_text
        


def HybirdRAG_for_Context( entity, attr, **args):
    text = args["text"]
    _RAG_MODE = args[ "rag_mode" ]               # RAG的模式，naive, rule_based
    dataset_name = args[ "dataset_name" ]

    if _RAG_MODE == "naive":
        return text
    elif _RAG_MODE == "rule_based":
        if dataset_name == "cpl":
            return get_ruled_context( entity, attr, **args )
        elif dataset_name == "rotowire":
            return get_ruled_context( entity, attr, **args )
        elif dataset_name == "e2e":              # print(f"e2e无需rule_based RAG，返回原text") 
            return text
    elif _RAG_MODE == "hybird":
        return text
            

            
