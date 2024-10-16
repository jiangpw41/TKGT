import os
import pandas as pd
import numpy as np
from tqdm import tqdm

################################################# e2e ###############################################################
def to_tuple_e2e( excel ):
    ret_list = []
    for i in tqdm( range( excel.shape[0]), desc="Changing E2E data cell into tuple"):
        temp = set()
        for j, filed_name in enumerate(list(excel.columns)):
            value = excel.iloc[i, j]
            if not pd.isna( value ):
                temp.add( (filed_name, value))
        ret_list.append( temp )
    return ret_list


def load_e2e( data_dir, load_data ):
    parts = [ "train", "test", "valid"]
    ret = [[], []]
    for part in parts:
        data = load_data( os.path.join( data_dir, f"original/{part}.xlsx"), "excel").drop( 'Unnamed: 0', axis = 1)
        text = load_data( os.path.join( data_dir, f"original/{part}.text"), "text")
        ret[0].extend( text )
        ret[1].append( data )
    temp = pd.concat([ret[1][0], ret[1][1], ret[1][2]], axis=0).reset_index(drop=True)
    text_len = len( ret[0] )
    table_len = temp.shape[0]
    if text_len != table_len:
        raise Exception( f"Text长度{text_len}与表格长度{table_len}不一致！")
    return ret[0], to_tuple_e2e( temp )


################################################# rotowire ###############################################################

def to_tuple_rotowire( excel ):
    ret = {}
    ret_list = {
        "Team":[],
        "Player" :[]
    }
    # 处理FirstColumn
    ret_first = {
        "Team":[],
        "Player" :[]
        }
    # 处理DataCell
    for i in tqdm( range( len(excel) ), desc="Changing Rotowire data cell into tuple"):
        team, player = excel[i]
        
        for sheet_name, sheet in zip(["Team", "Player"], [team, player]):
            temp = set()
            temp_first = set()
            for p in range( sheet.shape[0] ):
                name = sheet.iloc[p, 0]
                if not pd.isna(name):
                    temp_first.add( (sheet_name, name))
                    for j, filed_name in enumerate(list(sheet.columns)):
                        value = sheet.iloc[p, j]
                        if not pd.isna( value ):
                            if isinstance(value, (float, np.float64)):
                                value = int(value)
                            temp.add( (name, filed_name, value))
            
            ret_list[ sheet_name ].append( temp )
            ret_first[ sheet_name ].append( temp_first )
        
    ret["DataCell"] = ret_list
    ret["FirstColumn"] = ret_first
    return ret


def load_rotowire( data_dir, load_data ):
    parts = [ "train", "test", "valid"]
    ret = [[], []]
    for part in parts:
        table_dir = os.path.join( data_dir, f"original/tables/{part}")
        file_list = os.listdir( table_dir )
        data = []
        for i in tqdm( range(len(file_list)), desc=f"Rotowire processing {part}"):
            data.append( ( 
                load_data( os.path.join( table_dir, f"{i}.xlsx"), "excel", sheet_name="team").drop( 'Unnamed: 0', axis = 1),    # team表格
                load_data( os.path.join( table_dir, f"{i}.xlsx"), "excel", sheet_name="player").drop( 'Unnamed: 0', axis = 1)                                 # player
            ))
        text = load_data( os.path.join( data_dir, f"original/{part}.text"), "text")
        ret[0].extend( text )
        ret[1].extend( data )
    text_len = len( ret[0] )
    table_len = len( ret[1] )
    if text_len != table_len:
        raise Exception( f"Text长度{text_len}与表格长度{table_len}不一致！")
    return ret[0], to_tuple_rotowire(ret[1])

################################################# cpl ###############################################################

def parse_cpl_structure( data_cell, prefix ):
    ret = set()
    if "法院" in data_cell.keys():                              # 到最后一层了
        for entity_type in data_cell.keys():
            value = data_cell[entity_type]["取值"]
            if value != 'nan':
                if entity_type != "法院":
                    if '专题问题' not in prefix:
                        ret.add( ( entity_type, prefix, value ))
                else:
                    ret.add( ( entity_type, prefix, value ))


    else:
        for key in data_cell.keys():
            if key in ['【诉讼请求原文】【法院认为及判决结果原文】', '【事实与理由原文】【辩称原文】【法院认定事实原文】']:
                continue
            value = data_cell[key]
            if key in [ "1", "2", "3", "4", "5", "6", "7"]:     # 是可迭代的次数
                new_prefix = prefix+f"<SPLIT>{key}"
                sub_ret = parse_cpl_structure( value, new_prefix )
                ret.update( sub_ret )
            else:
                if key in ['【诉讼请求】【法院认为及判决结果】', '【事实与理由】【辩称】【法院认定事实】', '专题问题']:
                    new_prefix = prefix
                else:
                    new_prefix = prefix+ f"<SPLIT>{key}" if  prefix!="" else key       # 单纯的子字典
                sub_ret = parse_cpl_structure( value, new_prefix )
                ret.update( sub_ret )
    return ret

def to_tuple_cpl( excel ):
    ret_list = {
        "FirstColumn" : [],
        "DataCell" : [],
    }
    for i in tqdm( range( len(excel) ), desc="Changing CPL table into tuple"):
        table = excel[str(i)]
        first_column, data_cell  = table["first_column"], table["data_cell"]
        temp_first = set()
        temp_names = {}
        # 解决First Column，复制保存每个名字属于哪个实体类别，以及是否分开答辩（被告和被告_1分开答辩）
        for key in first_column.keys():
            names = first_column[key][0]
            if "、" in names:
                names_ = names.split("、")
            else:
                names_ = [ names ]
            temp_names[key] = names_
            for _name in names_:
                temp_first.add( (key, _name) )
        ret_list["FirstColumn"].append( temp_first )
        # 迭代解决Data Cell
        temp_cell = set()
        temp_dict = parse_cpl_structure( data_cell, "" )
        for item in temp_dict:
            real_names = temp_names[ item[0] ]
            for _name in real_names:
                temp_cell.add( (_name, item[1], item[2]) )
        ret_list["DataCell"].append( temp_cell )
    return ret_list

def load_cpl( data_dir, load_data ):
    table_dir = os.path.join( data_dir, f"original/tables_703.json")
    text_dir = os.path.join( data_dir, f"original/text_703")
    tables = load_data( table_dir, "json" )
    texts = load_data( text_dir, "text" )
    
    text_len = len( tables )
    table_len = len( texts )
    if text_len != table_len:
        raise Exception( f"Text长度{text_len}与表格长度{table_len}不一致！")
    return texts, to_tuple_cpl(tables)