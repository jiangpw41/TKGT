import pandas as pd
import os
from tqdm import tqdm
from Hybird_RAG.config import VALUE_NAN
import numpy as np

def load_text_data( test_text_path ):
    # 测试文本和数据路径
    texts = []
    with open(test_text_path, 'r', encoding='utf-8') as file:
        for line in file:
            texts.append(line.strip())
    return texts

def Get_Answer( value, scope):
    """
    处理表格的标签，变为ABC。将预测传入单个表格、字段名、取值范围
    table：单个Sample的表格
    key：字段名
    scope：key字段对应的取值范围
    """
    option_labels = [ 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    if pd.isna(  value ):
        # 空值
        _ANSWER =  VALUE_NAN
    else:
        if scope==str:
            # 类型为字符串则不变
            _ANSWER = value
        else:
            # 否则换为ABC
            flag = 0
            for j in range(len(scope)):
                if scope[j]==value:
                    _ANSWER = option_labels[j]
                    flag=1
            if flag==0:
                raise Exception("给出的Label没有匹配的选项")
    return _ANSWER

def Get_Scope( dataset_type, field_dict, key, _OPTION=False):
    """
    处理取值范围，如果是字符串类型，返回<No Options>，否则返回（带标签的）选项
    dataset_type：数据集类型
    field_dict: 知识图谱中带取值范围的字典
    key: 字段名
    _OPTION：是否为选项标签
    """
    if dataset_type=="e2e":
        option_labels = [ 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        if field_dict[key]==str:
            # 如果知识图谱字典中字段的取值范围为字符串，则返回无范围
            _SCOPE = "<No Options>" if _OPTION else "<No Scope>"
        else:
            # 否则，根据是否为Option进行返回
            value_list = field_dict[key]
            if _OPTION:
                modified_list = []
                for i in range( len(value_list) ):
                    # 遍历这个字段对应的所有取值可能
                    value = value_list[i]
                    modified_list.append( option_labels[i]+ ": "+ value )
                _SCOPE = modified_list
            else:
                _SCOPE = value_list
        return _SCOPE

def Get_Fields( dataset_type, option=False):
    if dataset_type == "e2e":
        if option:
            return ['Price range', 'Customer rating', 'Food', 'Area', 'Family friendly']
        else:
            return ['Name', 'Price range', 'Customer rating', 'Food', 'Area', 'Family friendly', 'Near']
    else:
        return []

def process_na(value):
    "处理nan和<NOT FOUND>"
    if pd.isna(value):
        return 'Bad Information'
    elif value.strip() == '':
        return 'Bad Information'
    elif value == 'nan':
        return 'Bad Information'
    elif value == VALUE_NAN:
        return 'Bad Information'
    else:
        return value

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
    

def Context_Collision( prompt_list, context, field_dict, llm, sampling_params):
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
    ret = llm.generate(new_prompt_list, sampling_params, use_tqdm=False)
    ret_list = []
    for i in range( len(map_dict)):
        line = map_dict[i]
        if isinstance(line, str):
            ret_list.append( line )
        else:
            ret_list.append( ret[ line[0] ] )
    return ret_list

    