# 控制训练样本中not found的比例，减少训练时间

import argparse
import os
import sys
import subprocess
import tqdm as tqdm
import shutil

_ROOT_PATH = os.path.abspath(__file__)
for i in range(3):
    _ROOT_PATH = os.path.dirname( _ROOT_PATH )
sys.path.insert( 0, _ROOT_PATH)
from utils import load_data, get_shuffle_index, save_data
_NOT_FOUND_RATIO = 0.5

def ratio_control( dataset_name, part_name):
    ft_json_path = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_{part_name}_ft.json")
    jsons = load_data( ft_json_path, "json")
    not_found_list = []
    rest_list = []
    for i in range( len(jsons) ):
        temp = jsons[ i ]["output"]
        if temp == "<NOT FOUND>":
            not_found_list.append( i )
        else:
            rest_list.append( jsons[i] )
    len_rest, len_not_found = len(rest_list), len(not_found_list)
    if len_not_found <= _NOT_FOUND_RATIO * len_rest:         # 空样本如果本身就小于有效样本的一般，直接条狗
        return None
    else:
        indexs = get_shuffle_index( not_found_list )
        save_index = indexs[ : int(_NOT_FOUND_RATIO * len_rest) ]
        ret_list = []
        for i in range(len(save_index)):
            index = save_index[i]
            ret_list.append( jsons[not_found_list[index]] )
        rest_list.extend( ret_list )
        save_path = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_{part_name}_ft_normal.json")
        save_data( rest_list, save_path)
        return ret_list
        

    
def ratio_controller( dataset_name ):
    if dataset_name == "rotowire":
        for part in [ "first_column", "data_cell"]:
            for subtable_name in ["Team", "Player"]:
                part_name = f"{part}_{subtable_name}"
                ratio_control( dataset_name, part_name )
        # ratio_control( "rotowire", "first_column_Team")       # 235 / 3162
        # ratio_control( "rotowire", "first_column_Player")     # 14 / 3383
        # ratio_control( "rotowire", "data_cell_Team")          # 50302 / 22022
        # ratio_control( "rotowire", "data_cell_Player")        # 328609 / 76053
    elif dataset_name == "cpl":
        for part in [ "first_column", "data_cell"]:
            for subtable_name in ["all"]:
                part_name = f"{part}_{subtable_name}"
                ratio_control( dataset_name, part_name )
        # 1419
        # 265587 / 23232 === 34848


if __name__=="__main__":
    ratio_controller( "cpl" )