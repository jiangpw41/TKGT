import sys
import os
import json
from typing import List
import re

_ROOT_PATH = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__) )) )
sys.path.insert(0, _ROOT_PATH)       # 将根加入工作目录
from utils import create_logger
from Mixed_IE.config import _ROOT_PATH, _POS_FILTER_zh
from Mixed_IE.functions import read_text_to_list
from Mixed_IE.regulation.regulation_lib import _SEPARATORS

logger = create_logger( "preprocess_log", os.path.join(_ROOT_PATH, "Mixed_IE/mixed_ie.log"))

def Firstlevel(original_string:str, separators:list = _SEPARATORS, index = None):  
    _SPECIAL_SEPARATOR = "<SJTU_IEEE_LAW>"
    ret = {}

    # 分割标题
    temp = list( filter(None, original_string.split("###") ))
    ret["标题"] = temp[0]
    original_string = temp[1]

    # 分隔正文与标题
    separator = separators[0][0]
    match = separator.search(original_string)
    if match:
        rep = match.group(0) + _SPECIAL_SEPARATOR
        original_string = original_string.replace(match.group(0) , rep, 1)
    else:
        print(f"{index} part {0} fail")
    
    # 插入附录分隔符
    separator = separators[0][3]
    match = separator.search(original_string)
    end_index = match.end()  # 获取匹配项结束索引（不包含）
    target_sep = "\\n"
    before = original_string[:end_index]
    rest =  original_string[end_index:]
    rest_lists = list( filter(None, rest.split( target_sep ) ))
    if len(rest_lists)==0:
        before = before
        rest_lists = []
    elif len( rest_lists ) == 1:
        line = rest_lists[0]
        flag = 0
        if len(line) > 10 or "附" in line or "本息" in line or "：" in line:
            flag = 1
        else:
            match_1 = _SEPARATORS[1][2].search(line)
            match_2 = _SEPARATORS[1][5].search(line)
            if match_1 and match_2:
                before = before+line
                rest_lists = []
            else:
                flag = 1
        if flag == 1:
            before = before
            rest_lists = rest_lists
    else:
        fis = 0
        for i in range(2):
            line = rest_lists[i]
            if len(line) > 10 or "附" in line or "本息" in line or "：" in line:
                break
            else:
                match_1 = _SEPARATORS[1][2].search(rest_lists[i])
                match_2 = _SEPARATORS[1][5].search(rest_lists[i])
                if match_1 and match_2:
                    fis += 1
                    continue
                else:
                    break
        before = before + "\\n".join(rest_lists[: fis])
        rest_lists = rest_lists[fis:]

    splited = list( filter(None, before.split(_SPECIAL_SEPARATOR) ))
    ret["开头"] = list( filter(None, splited[0].split("\\n") ))
    ret["正文"] = list( filter(None, splited[1].split("\\n") ))
    ret["附录"] = rest_lists
    return ret

def tails( lists ):
    lens = len(lists)
    sep = _SEPARATORS[1][5]
    divider = 0

    ret = []
    for i in range(lens):
        index = lens-i-1
        line = lists[index]
        match = sep.search(line)
        if match:
            if line!="\n":
                ret.append( line )
            continue
        else:
            divider = index
            break
    ret2 = []
    for i in range( len(ret)):
        index = len(ret)-i-1
        ret2.append(ret[index])
    return lists[0:divider+1], ret2

def Secondlevel( data, seps=_SEPARATORS ):
    sep_1 =  seps[1][0]
    _zero = []
    ret = {}

    # 正文初始程序信息
    for i in range(len(data)):
    #for i in range(187,188):
        texts = data[ str(i) ]["正文"]
        _target = None
        for j in range( len(texts) ):
            match = sep_1.search(texts[j])
            if match:
                _target = j
                break
        if _target == None:
            _zero.append(i)
        else:
            # re1, tailss = 
            if _target==0:
                # 说明正文全在一行了
                temp_string = texts[0]
                temp_string = temp_string.replace( "？", "")
                temp_string = temp_string.replace( "。", "。<IIII>")
                temp_list = temp_string.split("<IIII>")
                for k in range( len(temp_list) ):
                    sub_string = temp_list[k]
                    match = sep_1.search(sub_string)
                    if match:
                        procedures = temp_list[:k+1]
                        restsss = temp_list[k+1:]
                        restsss.extend( texts[1:] )
                        zhong, tailss = tails( restsss )
            else:
                procedures = texts[0:_target+1]
                zhong, tailss = tails( texts[_target+1:] )

            ret[i] = {
                "程序信息" : procedures,
                "申辩证" : zhong,
                "末尾信息": tailss
            }
            data[ str(i) ]["正文"] = ret[i]
    # 末尾信息
    no_dou = seps[1][2]
    only_end = seps[1][3]
    only_mao = seps[1][4]
    no_ju = seps[1][5]
    indexs = _zero
    error = 0
    for i in indexs:
        parts = data[str(i)]["正文"]
        for j in range(len(parts)):
            line = parts[j]
            num_ju = line.count("。")
            num_court = line.count("本院认为")
            match_1 = only_end.search(line)  # 只有末尾有句号
            match_2 = only_mao.search(line)  # 只有一个冒号
            match_3 = no_dou.search(line)  # 没有逗号
            match_4 = no_ju.search(line)  # 没有句号
            if match_2:      # 冒号开头不超过10个字符
                continue
            else:
                if match_3 and match_4:   # 没有逗号也没有句号
                    continue
                elif match_1 and num_court==0:     # 只有末尾句号也成立
                    continue
                elif j==0 and num_ju==26:
                    lists = line.split("。")
                    head = lists[:7]
                    restss = lists[7:]
                    tail = parts[1:]
                    ret[i] = {
                        "程序信息" : head,
                        "申辩证" : restss,
                        "末尾信息" : tail
                    }
                    data[ str(i) ]["正文"] = ret[i]
                    break
                else:
                    divider = j
                    re1, re2 = tails( parts[j:] )
                    ret[i] = {
                        "程序信息" : parts[:j],
                        "申辩证" : re1,
                        "末尾信息" : re2
                    }
                    data[ str(i) ]["正文"] = ret[i]
                    break
        if divider==0:
            print(f"error {i}")
    return data
            
def check( data, sep=_SEPARATORS[0][3]):
    _zero = 0
    _multi = 0
    for i in range(len(data)):
    #for i in range(540,541):
        count = 0
        matches = sep.finditer(data[i])  
        for match in matches:  
            count += 1
        if count == 0:
            _zero += 1
        if count > 1:
            _multi += 1
        print(f"Index {i} count {count}")
    print(f" _zero {_zero} _multi {_multi}")

def main( ):
    # 准备规则分割结果保存目录，读取文件
    dirs = os.path.join( _ROOT_PATH, "Mixed_IE/further_processed/regulation")
    if not os.path.exists(dirs):  
        # 如果目录不存在，则创建它  
        os.makedirs(dirs)
        logger.info( "Regulation: have created path of regulation results for further processing.")
    data_path = os.path.join(_ROOT_PATH, "data/CPL/text")
    if not os.path.exists(data_path):  
        # 如果目录不存在，则创建它  
        raise FileNotFoundError(f"Directory '{data_path}' does not exist.")
    texts = read_text_to_list( data_path )

    # （1）拆分标题、正文、附录等
    saves = {}
    for i in range(len(texts)):
        saves[i] = Firstlevel(texts[i], _SEPARATORS, i)

    with open( os.path.join( dirs, 'para_splited_A.json'), 'w', encoding='utf-8') as file:
        json.dump(saves, file, ensure_ascii=False, indent=4)
    logger.info( "Regulation: have splitted each document into four major parts.")

    # （2）拆分正文
    with open( os.path.join( dirs, 'para_splited_A.json'), 'r', encoding='utf-8') as file:
        data = json.load(file)
    ret = Secondlevel( data )
    with open( os.path.join( dirs, 'para_splited_B.json'), 'w', encoding='utf-8') as file:
        json.dump(ret, file, ensure_ascii=False, indent=4)
    logger.info( "Regulation: have splitted each document's main content into three parts.")

    #（3）提取申辩证
    with open( os.path.join( dirs, 'para_splited_B.json'), 'r', encoding='utf-8') as file:
        data = json.load(file)
    savess = {}
    for i in range( len(data) ):
        savess[i] = data[str(i)]["正文"]["申辩证"]
    with open( os.path.join( dirs, 'para_splited_C.json'), 'w', encoding='utf-8') as file:
        json.dump(savess, file, ensure_ascii=False, indent=4)
    logger.info( "Regulation: have extracted each document's main content's core part.")

if __name__ == "__main__":
    main( )