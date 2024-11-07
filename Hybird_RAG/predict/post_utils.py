import pandas as pd
import os
import sys
from tqdm import tqdm
import numpy as np
_ROOT_PATH = os.path.abspath(__file__)
for i in range(3):
    _ROOT_PATH = os.path.dirname( _ROOT_PATH )
sys.path.insert( 0, _ROOT_PATH)
from utils import _PUNCATUATION_EN, _PUNCATUATION_ZH


def Chinese_text_Cleaner( text, part ):
    bad_characters = [" ", "\n", "\\n" ]
    #（1）将文本中的英文字符替换为中文
    for i in range( len(_PUNCATUATION_EN) ):
        if _PUNCATUATION_EN[i] in text:
            text = text.replace( _PUNCATUATION_EN[i], _PUNCATUATION_ZH[i])
    #（2）去除所有非法字符
    # bad_characters.extend( _PUNCATUATION_ZH )
    if part == "first_column_all":
        for character in bad_characters:
            text = text.replace( character, "")
        
        if "、" in text:
            ret = text.split("、")
        elif "，" in text:
            ret = text.split("，")
        else:
            ret = text
        return ret
    else:
        text = text.replace( " ", "")
        return text

def English_text_Cleaner( text, part ):
    bad_characters = ["\n", "\\n" ]
    #（1）将文本中的中文字符替换为英文
    for i in range( len(_PUNCATUATION_EN) ):
        if _PUNCATUATION_ZH[i] in text:
            text = text.replace( _PUNCATUATION_ZH[i], _PUNCATUATION_EN[i])
    #（2）去除所有非法字符
    # bad_characters.extend( _PUNCATUATION_ZH )
    if part == "first_column":
        for character in bad_characters:
            text = text.replace( character, "")
        return text.split("、")
    else:
        return text.strip()

def split_name( prompt_name ):
    ret = prompt_name
    if "法院" in prompt_name:
        return prompt_name[2:].replace("(", "").replace("（", "").replace(")", "").replace("）", "").strip()
    elif "原告" in prompt_name or "被告" in prompt_name:
        return prompt_name[7:].replace("(", "").replace("（", "").replace(")", "").replace("）", "").strip()
    else:
        de = {
            "(": ")",
            "（": "）"
        }
        for left in de.keys():
            if left in prompt_name:
                temp = prompt_name.split( left )[1]
                if de[left] in temp:
                    return temp.split( de[left] )[0].strip()
                else:
                    raise Exception(f"括号{left}不匹配！")

def Get_Fields( dataset_type, option=False):
    if dataset_type == "e2e":
        if option:
            return ['Price range', 'Customer rating', 'Food', 'Area', 'Family friendly']
        else:
            return ['Name', 'Price range', 'Customer rating', 'Food', 'Area', 'Family friendly', 'Near']
    else:
        return []

def Label_Process( dataset_type, kg_field_dict, _OPTION=False):
    """
    获取一个表格，返回一个字典，每个文档一个key，value则是所有（字段名，值）的二元组集合，其中值要变为小写，且考虑option、bad information
    dataset_type: 数据集类型，e2e或cpl
    _OPTION：答案是选项标签ABC还是选项本身
    kg_field_dict：数据集的知识图谱字典
    """
    if dataset_type == "e2e":
        # 加载表格并预处理
        from Hybird_RAG.config import _ROOT_PATH
        test_table_path = os.path.join( _ROOT_PATH, 'data/e2e/test.xlsx')
        tables = pd.read_excel(test_table_path)
        tables = tables.applymap( lambda x: x.strip() if isinstance(x, str) else x)
        fields_list = Get_Fields( dataset_type )
        # 整理为集合的字典
        label_dict = {}
        for line_num in tqdm(range(len(tables)), desc='Label Data Procossing'):
            '逐个文档处理'
            single_table_set = set()
            single_table = tables.iloc[line_num, :]
            for key in fields_list:
                "对每个标签字段"
                if _OPTION:
                    value = process_na( Get_Answer( single_table[key], scope=kg_field_dict[key] ) )
                else:
                    value = process_na( single_table[key])
                single_table_set.add( (key.lower(), value.lower()) )

            label_dict[line_num] = single_table_set
        return label_dict
    elif dataset_type == "cpl":
        return []

def replace_bad_info( item, dataset_type ):
    if dataset_type=="e2e":
        "接受小写化后的值"
        replaced_word = [ '\n', '\\n', '\'', '\"', '(' , ')' , '[' , ']', '<' , '>']
        for word in replaced_word:
            if word in item:
                item = item.replace(word, '' )
        
        if item in [ '<not found>', '', ' ', 'nan', np.nan]:
            return 'bad information'
        
        not_express = [ 'sorry', 'do not', 'not found']
        for word in not_express:
            if word in item:
                return 'bad information'


        _prefix = [ 'extraction:', 'yes:', 'answer:', 'result:', 'solution:', ':']
        for prefix in _prefix:
            if prefix in item:
                item = item.split(prefix)[-1].strip()
        return item
    elif dataset_type=="cpl":
        return item
    
def check_exsit( list, context):
    flag = 0
    for word in list:
        if word.lower() in context.lower():
            flag =1
            break
    if flag == 1:
        return True
    else:
        return False
    
def Context_Collision( prompt_list, context, field_dict):
    map_dict = {}
    new_prompt_list = []
    field_list = list( field_dict.keys() )
    for i in range(len(prompt_list)):  
        key  = field_list[ i % len(field_list) ]
        prompt = prompt_list[i]
        value_scope = field_dict[key]
        if key == "Name":
            new_prompt_list.append( prompt )
            map_dict[i] = (len(new_prompt_list)-1, )
        elif key=="Near":
            new_prompt_list.append( prompt )
            map_dict[i] = (len(new_prompt_list)-1, )
        elif key=='Price range' or key=='Customer rating':
            for value in value_scope:
                if value!='High':               
                    # 如果当前值不是High，那么要是在context中就直接取值并退出，否则看后面的
                    if value=="Low":
                        value='Low '
                    if value.lower() in context.lower():
                        map_dict[i] = value
                        flag = 1
                        break
            new_prompt_list.append( prompt )
            map_dict[i] = (len(new_prompt_list)-1, )
        elif key=='Family friendly':
            flag = 0
            band_list = ["for adults", "unfriendly"]
            for word in band_list:
                if word in context.lower():
                    map_dict[i] = "No"
                    flag = 1
            if flag==1:
                continue
            else:
                new_prompt_list.append( prompt )
                map_dict[i] = (len(new_prompt_list)-1, )
        elif key=='Food':
            food_list = ["Chine ", "fast"]
            food_list.extend(value_scope)
            if not check_exsit( food_list, context):
                map_dict[i] = VALUE_NAN
            else:
                new_prompt_list.append( prompt )
                map_dict[i] = (len(new_prompt_list)-1, )
        elif key=='Area':
            if value=="Riverside":
                if check_exsit( [value, "river"], context):
                    map_dict[i] = value
                    flag = 1
                    break
            else:
                new_prompt_list.append( prompt )
                map_dict[i] = (len(new_prompt_list)-1, )
