
"""
对于任意函数
（1）处理预测结果，清理预测结果中的bad outputs（用外挂函数解决）
（2）组成(label, predict)列表对保存到eval_pair中
"""
import argparse
import os
import sys
import pickle
import re 

_ROOT_PATH = os.path.abspath(__file__)
for i in range(3):
    _ROOT_PATH = os.path.dirname( _ROOT_PATH )
sys.path.insert( 0, _ROOT_PATH)
from utils import load_data, save_data, _PUNCATUATION_EN, _PUNCATUATION_ZH
from Hybird_RAG.predict.post_utils import Chinese_text_Cleaner, English_text_Cleaner, split_name


_Hybird_RAG_PATH = os.path.join( _ROOT_PATH, "Hybird_RAG")



def post_process_cpl_single( part, predict_list, prompt_list, subtable_name=None ):
    ret_set = set()
    if part == "first_column":
        field_list = ["法院", '出借人（原告）', '借款人（被告）']
        for i in range(len(predict_list)):
            field = field_list[i]
            text = predict_list[i]
            text_list = Chinese_text_Cleaner( text, part )
            for j in range(len(text_list)):
                ret_set.add( (field, text_list[j]))
    else:
        for i in range(len(prompt_list)):
            prompt = prompt_list[i].split("现在到你实践了：\n    ")[1]
            text = predict_list[i]
            # 匹配名称
            pattern_role = r"目标角色：(.*?)\n"
            match_role = re.search(pattern_role, prompt)  
            if match_role:  
                prompt_name = match_role.group(1)
            else:
                raise Exception(f"匹配实体名称失败：{i}，{prompt}")
            prompt_name = split_name( prompt_name )
            # 匹配字段
            pattern_field = r'目标字段：(.*?)\n'  
            match_field = re.search(pattern_field, prompt)  
            if match_field:  
                prompt_field = match_field.group(1)
            else:
                raise Exception(f"匹配实体属性失败：{i}，{prompt}")
            # 清洗输出
            
            text = Chinese_text_Cleaner( text, part )
            
            ret_set.add( (prompt_name, prompt_field, text))
    
    return ret_set

def judge_not_found( text ):
    if text.strip() == "":
        return True
    elif "not found" in text:
        return True

def remove_the( text ):
    if "the" in text:
        return text.replace( "the", "" ).strip().lower()
    else:
        return text.strip().lower()

def post_process_e2e_single( predict_set, prompt_list, label_set):
    ret_label = set()
    ret_predict = set()
    # 处理标签
    for item in label_set:
        attr = item[0].strip().lower()
        value = item[1].strip().lower()
        value = remove_the( value )
        ret_label.add( (attr, value) )
    # 处理预测值
    for i in range(len(prompt_list)):
        prompt = prompt_list[i]     # .split("Your Turn:\n    ")[1]
        text = predict_set[i].strip().lower()
        if not judge_not_found( text ):
            # 匹配属性名
            pattern_role = r"Target Attribute: (.*?)\n"
            match_role = re.search(pattern_role, prompt)  
            if match_role:  
                attr = match_role.group(1)
            else:
                raise Exception(f"匹配属性失败：{i}，{prompt}")

            text = remove_the( text )
            
            ret_predict.add( (attr.strip().lower(), text))
    return ret_predict, ret_label

def post_process_rotowire_single( part, predict_list, prompt_list, subtable_name):
    ret_set = set()
    if subtable_name==None:
        raise Exception(f"Rotowire需要指定subtable_name")
    if part == "first_column":
        for i in range(len(predict_list)):
            field = subtable_name
            text = predict_list[i]
            text_list = English_text_Cleaner( text, part )
            for j in range(len(text_list)):
                ret_set.add( (field, text_list[j]))
    else:
        for i in range(len(prompt_list)):
            prompt = prompt_list[i].split("Your Turn:\n    ")[1]
            text = predict_list[i]
            # 匹配名称
            pattern_role = r"Target Entity: (.*?)\n"
            match_role = re.search(pattern_role, prompt)  
            if match_role:  
                prompt_name = match_role.group(1)
            else:
                raise Exception(f"匹配实体名称失败：{i}，{prompt}")
            
            prompt_name = split_name( prompt_name )
            # 匹配字段
            pattern_field = r'Attribute: (.*?)\n'  
            match_field = re.search(pattern_field, prompt)  
            if match_field:  
                prompt_field = match_field.group(1)
            else:
                raise Exception(f"匹配实体属性失败：{i}，{prompt}")
            # 清洗输出
            
            text = English_text_Cleaner( text, part )
            if "not found" not in text.lower():
                ret_set.add( (prompt_name, prompt_field, text))
    
    return ret_set

def post_process( dataset_type, part, _predict, _prompt, _label, not_process, subtable_name ):
    if not_process:                                                         # 不进行工程处理则直接返回
        return _predict
    if dataset_type=="cpl":
        return post_process_cpl_single( part, _predict, _prompt  ), _label
    elif dataset_type=="e2e":
        return post_process_e2e_single(  _predict, _prompt, _label  )
    elif dataset_type=="rotowire":
        return post_process_rotowire_single( part, _predict, _prompt,  subtable_name ), _label
    else:
        raise Exception("Not Post-Porcessed")

def pre_label_load( prompt_list_name, dataset_name ):
    predict_path = os.path.join( _Hybird_RAG_PATH, f"temp/{dataset_name}/{dataset_name}_{prompt_list_name}_predict_list.pickle")            # Predict list路径
    label_path = os.path.join( _Hybird_RAG_PATH, f"temp/{dataset_name}/{dataset_name}_{prompt_list_name}_label_list.pickle")                # Label list路径
    prompt_path = os.path.join( _Hybird_RAG_PATH, f"temp/{dataset_name}/{dataset_name}_{prompt_list_name}_prompt_list.pickle")              # Prompt list路径
    eval_pair_path = os.path.join( _Hybird_RAG_PATH, f"evaluation/eval_results/{dataset_name}_{prompt_list_name}_eval_pair_list.pickle")    # 保存输出结果路径,label, prompt对
    return load_data(predict_path, "pickle"), load_data(label_path, "pickle"), load_data(prompt_path, "pickle"), eval_pair_path

def main( prompt_list_name, dataset_name, not_process, subtable_name, sample_little):
    predict_list, label_list, prompt_list, eval_pair_path = pre_label_load( prompt_list_name, dataset_name )              # 加载数据
    if len(predict_list)!=len(label_list):
        if sample_little == None:
            raise Exception(f"预测结果{len(predict_list)}和标签长度{len(label_list)}不一致")
        else:
            if sample_little!=len(predict_list):
                raise Exception(f"sample_little预测长度{sample_little}和预测长度{len(predict_list)}不一致")
    if sample_little!=None:
        label_list = label_list[:sample_little]
    ret_predict_list = []
    ret_label_list = []
    if not_process:
        print("not_process为True，不进行工程后处理")
    else:
        print("not_process为False，进行工程后处理")
    length = sample_little if sample_little!=None else len(predict_list)
    for i in range(  length ):                                                                             # 遍历处理
        ret_predict, ret_label = post_process( dataset_name, prompt_list_name, predict_list[i], prompt_list[i], label_list[i],  not_process, subtable_name)
        ret_predict_list.append(ret_predict )
        ret_label_list.append(ret_label )

    save_data( (ret_label_list, ret_predict_list), eval_pair_path)
    # 后规则处理
    if dataset_name=="e2e":
        from Hybird_RAG.retriever.e2e_rule import re_process_e2e_pari
        text_path = os.path.join( _ROOT_PATH, "data/e2e/test.text")
        re_process_e2e_pari(text_path, eval_pair_path)
    elif dataset_name=="rotowire":
        from Hybird_RAG.retriever.rotowire_rule import re_process_rotowire_pari
        text_path = os.path.join( _ROOT_PATH, "data/rotowire/test.text")
        re_process_rotowire_pari(text_path, eval_pair_path)
    elif dataset_name == "cpl":
        from Hybird_RAG.retriever.cpl_rule import re_process_cpl_pari
        text_path = os.path.join( _ROOT_PATH, "data/cpl/test.text")
        re_process_cpl_pari(text_path, eval_pair_path)
    
    



if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description="Run script with external arguments")
    parser.add_argument('--prompt_list_name', type=str, required=True, help='提示词文件路径')
    parser.add_argument('--dataset_name', type=str, required=True, help='数据集文件名')
    parser.add_argument('--not_process', type=int, required=True, help='是否使用工程方法后处理')
    parser.add_argument('--subtable_name', type=str, required=False, help='子表名称')
    parser.add_argument('--sample_little', type=int, required=False, help='小样本数量')
    args = parser.parse_args()
    # 获取参数值
    prompt_list_name = args.prompt_list_name
    dataset_name = args.dataset_name
    not_process = False if args.not_process==0 else True
    subtable_name = args.subtable_name if args.subtable_name else None
    sample_little = args.sample_little if args.sample_little else None
    """
    prompt_list_name = "all_all"   # "all_all"      # "first_column"
    dataset_name = "e2e"
    not_process = False
    subtable_name = None
    sample_little = 300
    """
    main( prompt_list_name, dataset_name, not_process, subtable_name, sample_little )