import os
import sys
import re
from collections import OrderedDict
"""
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
"""
_ROOT_PATH = "/home/jiangpeiwen2/jiangpeiwen2/TKGT"
sys.path.insert(0, _ROOT_PATH)
from utils import load_data, save_data, _PUNCATUATION_ZH, _PUNCATUATION_EN
from KGs.dataset_KGs.cpl import Plaintiff_claim_attributes
from Hybird_RAG.retriever.retrieve_hybrid import CPL_Hybrid_Retriever


def eval_simple( predict_lists, label_lists ):
    predict_num = 0
    label_num = 0
    same_num = 0
    
    for i in range(len(predict_lists)):
        predict_set = predict_lists[i]
        label_set = label_lists[i]
        predict_num += len(predict_set)
        label_num += len(label_set)
        for item in predict_set:
            if item in label_set:
                same_num +=1
    print(f"预测{predict_num}个，标签实际{label_num}个，一样的{same_num}个")


def find_context_from_prompt( prompt_list, role, attr):
    for i in range( len(prompt_list)):
        question = prompt_list[i].split("\n\n问题：")[1].split("\n主体角色：")[0]
        if role in question and attr in question:
            ans = prompt_list[i].split("\n相关上下文：")[1].split("\n答案：\n")[0]
            list_ = ans.split("', '")
            return list_

# 比较
def compare( ret_label_set, ret_predict_set ):
    # 对预测值建立字典
    map_dict = {}
    for item in ret_predict_set:
        map_dict[ item[1]] = item
    # 比较
    same = []
    not_same = []
    # 遍历每个标签
    for item in ret_label_set:
        # 如果标签的属性在预测值中，且两者相等
        if item[1] in map_dict and  item == map_dict[ item[1]]:
            same.append( item )
            del map_dict[ item[1] ]
        # 否则
        else:
            # 如果属性在但不相等，获取预测情况并从表中删除
            if item[1] in map_dict:
                predict = map_dict[item[1]]
                del map_dict[ item[1] ]
            else:
                predict = ()
            not_same.append( (item, predict))
    # 剩下就是预测中有但实际不存在
    for key in map_dict:
        not_same.append( ((), map_dict[key]))
    print("两者一样")
    for item in same:
        print(item)
    print("两者不一样")
    for item in not_same:
        field = f"{item[0][0]}, {item[0][1]}" if len(item[0])!=0 else f"{item[1][0]}, {item[1][1]}"
        label = item[0][2] if len(item[0])!=0 else ""
        predict = item[1][2] if len(item[1])!=0 else ""
        print(f"字段：{field}             预测：{predict}                标签：{label}")

def load_mat( _MODE ):
    if _MODE == "test":
        predict_lists = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_try_cell_all_predict_list.pickle", "pickle")
        prompt_lists = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_cell_all_prompt_list.pickle", "pickle") # 203
        label_lists = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_cell_all_label_list.pickle", "pickle")
        context_lists = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_try_cell_all_prompt_list.pickle", "pickle")
        texts = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/data/cpl/test.text" , "text")
        core_ruled_text = CPL_Hybrid_Retriever.cpl_batch_process( "test")
        entity_lists = []
        for index in range(len(prompt_lists)):
            entity_lists.append( get_entity_list( prompt_lists[index]  ))
        return predict_lists, prompt_lists, label_lists, texts, core_ruled_text, entity_lists, context_lists
    elif _MODE == "train":
        # 获取entity_lists
        entity_name_703 = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/data/cpl/original/entity_name_703.json", "json")
        over_3_time = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/data/cpl/original/over_3_time.json", "json")
        index_shuffle = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/data/cpl/index.pickle", "pickle")
        entity_name_676 = []
        for i in range(len(entity_name_703)):
            if i not in over_3_time["over_list"]:
                entity_name_676.append( entity_name_703[str(i)])
        entity_lists = []
        for i in range( 0, 473):
            temp = []
            index = index_shuffle[i]
            entity_dict = entity_name_676[index]
            for _name in entity_dict.keys():
                type_ = entity_dict[_name]['角色类型']
                if "_" in type_:
                    type_ = type_.split("_")[0].strip()
                temp.append( f"{type_} ({_name})")
            entity_lists.append(temp)
        # 获取labels
        old_label_lists = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/data/cpl/train.pickle", "pickle")["DataCell"]
        label_lists = []
        for i in range(len(old_label_lists)):
            temp = set()
            for item in old_label_lists[i]:
                if item[1] in Plaintiff_claim_attributes:
                    temp.add( item )
            label_lists.append( temp )
        texts = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/data/cpl/train.text" , "text")
        core_ruled_text = CPL_Hybrid_Retriever.cpl_batch_process( "train")
        return core_ruled_text, texts, label_lists, entity_lists
    
# 从提示词获取本文档所有实体：服务于test
def get_entity_list( prompt_list ):
    entity_list = []
    for i in range(len(prompt_list)):
        prompt = prompt_list[i].split("现在到你实践了：\n    ")[1]
        pattern_role = r"目标角色：(.*?)\n"
        match_role = re.search(pattern_role, prompt)  
        if match_role:  
            prompt_name = match_role.group(1)
        else:
            raise Exception(f"匹配实体名称失败：{i}，{prompt}")
        if prompt_name not in entity_list:
            entity_list.append( prompt_name )
    return entity_list

#########################后处理##############################
# 后处理
def extract_datetime( context ):
    date_str = context.replace("日", "").replace("年", "-").replace("月", "-")  
    try:
        year, month, day = date_str.split("-") 
        month = month.zfill(2)  # 确保月份是两位数
        if len(day)==1:
            day = "0"+day
        if len(month)==1:
            month = "0"+month
        return f"{year}-{month}-{day}" 
    except:
        #print( f"{date_str}无法分成三份" ) 
        return None
     
def extract_number( context ):
    match = re.search(r'\d+', context)  
    if match:  
        num_str = match.group()  
        return num_str
    else:  
        return None

def process_cpl_triplet( index, name, attr, value):
    #（1）过滤停用词
    if attr in ["是否变更诉讼请求"]:
        return None
    
    #（2）处理标签：暂时原样返回
    #if index == 0:
    #    return ( name, attr, value)
    #（3）处理预测
    # 处理非汉字符号（不含-）并处理空值
    ban = [ "`", "\n", '>', ',', ';', '?', '!', '…', ":", '"', '"', "'", "'", "(", ")", '，', '；', '？', '！', '......', "：",  '“', '”', '‘', '’', '（', '）', '《', '》', '【', '】', '[', ']', '、', "\\n"]
    for ban_word in ban:
        value = value.replace( ban_word, "")
    value = value.strip()
     #（4）处理特殊字符串：率数值
    if "率数值" in attr:
        if "。" in attr:
            attr = attr.replace("。", ".")
    if "not found" in value.lower() or "notfound" in value.lower() or value=="":
        return None
    # 非空，则先获得value的取值范围
    scope = Plaintiff_claim_attributes[attr]
    if isinstance( scope, list):
        # 如果是表格
        if value in scope:
            return ( name, attr, value)
        else:
            for value_scope in scope:
                if value in value_scope:
                    return ( name, attr, value)
            return None
    elif scope == str:
        # 如果是字符串：
        if "日期" in attr or "时间" in attr or "表示日" in attr or "哪一日" in attr:
            _value = extract_datetime(value)
            if _value==None:
                return None
            else:
                return ( name, attr, _value)
        else:
            return ( name, attr, value)
    elif scope == int:
        # 如果是整数
        _value = extract_number( value )
        if _value == None:
            return None
        else:
            return ( name, attr, _value)

def cpl_post_process_simple( predict_set, label_set):
    ret_predict_set = set()
    ret_label_set = set()
    set_two = [ ret_label_set, ret_predict_set ]
    for j, list_set in enumerate([ label_set,  predict_set]):
        for item in list_set:
            ret = process_cpl_triplet( j, item[0], item[1], item[2])
            if ret !=None:
                set_two[j].add(ret)
    return ret_label_set, ret_predict_set


def index_after_shuffle( index ):
    index_pikle = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/data/cpl/index.pickle", "pickle")
    return index_pikle[index]