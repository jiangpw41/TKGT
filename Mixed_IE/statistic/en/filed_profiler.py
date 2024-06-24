'''
{
    'rotowire':{
        'train': {'fields_num': 2*13, m*20 'lines_num': 3398},    # 总体信息9个字段，其中一个summmary为原文字符串列表，三个为展开列表名(主队得分1*15, 客队得分1*15, 球员得分25*24)，剩余五个为总体信息
        'valid': {'fields_num': 2*13, m*20, 'lines_num': 727}, 
        'test': {'fields_num': 2*13, m*20, 'lines_num': 728}, 
        'Total': {'fields_num': 2*13, m*20 'lines_num': 4853}},
    },
    rotowire: total words=1637820, total lens=4853, total filtered words=490729, average words=337.4860910776839,
    前874/6942

    'e2e': {['Name', 'Price range', 'Customer rating', 'Near', 'Food', 'Area', 'Family friendly']
        'train': {'fields_num': 7, 'lines_num': 42061}, 
        'valid': {'fields_num': 7, 'lines_num': 4672}, 
        'test': {'fields_num': 7, 'lines_num': 4693}, 
        'Total': {'fields_num': 7, 'lines_num': 51426}},
    e2e: total words=1152364, total lens=51426, total filtered words=471202, average words=22.408198187687162
    词性标注、停用词过滤、词性过滤后的词频统计，前27/2107的高频词涵盖所有对象
    'wikibio': {
        'train': {'fields_num': 2771, 'lines_num': 582659}, 
        'valid': {'fields_num': 1400, 'lines_num': 72831}, 
        'test': {'fields_num': 1406, 'lines_num': 72731}, 
        'Total': {'fields_num': 2996, 'lines_num': 728221}}, 
    wikibio: total words=70257683, total lens=728221, total filtered words=24192630, average words=96.47851819708578
    
    'wikitabletext': {
        'train': {'fields_num': 2262, 'lines_num': 10000}, 
        'valid': {'fields_num': 791, 'lines_num': 1318}, 
        'test': {'fields_num': 1022, 'lines_num': 2000}, 
        'Total': {'fields_num': 2443, 'lines_num': 13318}}}
    wikitabletext: total words=185111, total lens=13318, total filtered words=57862, average words=13.899309205586425
    
    
    
    
'''

import pickle
import os
import sys

_IE_PATH = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
sys.path.insert(0, _IE_PATH)
from functions import read_text_to_list

_ROOT_PATH = os.path.dirname( _IE_PATH )
_DATASET = ["e2e", "wikibio", "wikitabletext"]
_TYPE = ["train", "valid", "test"]

def get_fields( ):
    profile = {}
    saves = {}
    _ROOT_PATH_Data = os.path.join( _ROOT_PATH, "raw")
    for _dataset in _DATASET:
        attributes_tt = []
        sub_path = os.path.join( _ROOT_PATH_Data, _dataset)
        saves[_dataset] = {}
        profile[_dataset] = {}
        lines_num = 0
        for _type in _TYPE:
            attributes = []
            total_path = os.path.join( sub_path, _type+".data")
            texts = read_text_to_list( total_path )
            for i in range( len(texts) ):
                text = texts[i][1:-1]
                text = text.split("| <NEWLINE> |")
                for slot in text:
                    temp = slot.split(" | ")[0].strip()
                    if temp not in attributes:
                        attributes.append(temp)
                    if temp not in attributes_tt:
                        attributes_tt.append(temp)
            saves[_dataset][ _type ] = attributes
            profile[_dataset][ _type ] = {}
            profile[_dataset][ _type ]["fields_num"] = len(attributes)
            profile[_dataset][ _type ]["lines_num"] = len(texts)
            lines_num+=len(texts)
        profile[_dataset]["Total"] = {}
        profile[_dataset]["Total"]["fields_num"] = len(attributes_tt)
        profile[_dataset]["Total"]["lines_num"] = lines_num
    saves["profile"] = profile
    with open('saves.pkl', 'wb') as f:  
        # 使用pickle.dump()将列表写入文件  
        pickle.dump(saves, f) 
    print( profile ) # 2262

def _merge():
    with open('saves.pkl', 'rb') as f:  
        # 使用pickle.dump()将列表写入文件  
        data = pickle.load(f)
    for _dataset in _DATASET:
        _all = []
        for _type in _TYPE:
            attrs = data[_dataset][_type]
            if len(_all)==0:
                _all.extend( attrs )
            else:
                for attr in attrs:
                    if attr not in _all:
                        _all.append(attr)
        data[_dataset]["All_attr"] = _all
        print(_dataset)
        print(_all)
    with open('saves.pkl', 'wb') as f:  
        # 使用pickle.dump()将列表写入文件  
        pickle.dump(data, f) 

if __name__=="__main__":
    get_fields()
    _merge()