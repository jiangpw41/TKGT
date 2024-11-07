import os
import sys
import re
from tqdm import tqdm
from collections import OrderedDict

_ROOT_PATH = "/home/jiangpeiwen2/jiangpeiwen2/TKGT"
sys.path.insert(0, _ROOT_PATH)
from KGs.dataset_KGs.cpl import Plaintiff_claim_attributes, cpl_keyword
from utils import load_data, save_data,online_local_chat
from date_capture import CplDocumentRatioTextCapture, CplDocumentMoneyTextCapture, CplDocumentDateTextCapture
from test_utils import load_mat, compare, find_context_from_prompt, cpl_post_process_simple, index_after_shuffle, eval_simple
from Hybird_RAG.retriever.retrieve_hybrid import CPL_Hybrid_Retriever

_MODE = "test"

if _MODE == "test":
    predict_lists, prompt_lists, label_lists, texts, core_ruled_text, entity_lists, context_lists = load_mat( _MODE )
    
elif _MODE == "train":
    core_ruled_text, texts, label_lists, entity_lists = load_mat( _MODE )
elif _MODE == "debug":
    pair = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/evaluation/eval_results/history/cpl_data_cell_all_eval_pair_list.pickle", "pickle")
    label_lists, predict_lists = pair[0], pair[1]   # 1456个测试样本，每个样本的prompt为0或12或24
    prompt_lists = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_try_cell_all_prompt_list.pickle", "pickle")
    texts = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/data/cpl/test.text" , "text")
    core_ruled_text = CPL_Hybrid_Retriever.cpl_batch_process( "test")
    # 比较预测结果
    """
    def compare_predict( predict_lists, label_lists ):
        prompt_count = 0
        label_count = 0
        label_not = []
        same_count_pre = []
        for i in range( len(predict_lists)):
            prompt_count += len( predict_lists[i] )
            label_count += len( label_lists[i] )
            for item in label_lists[i]:
                if item in predict_lists[i]:
                    same_count.append( item )
                else:   
                    label_not.append( item )
            for item in predict_lists[i]:
                if item not in same_count:
                    same_count_pre.append( item )
        print(f"label有{label_count}个，提示词有{prompt_count}个，一样的有{len(same_count)}个")
        return same_count, label_not, same_count_pre
    same_count, label_not, same_count_pre = compare_predict( predict_lists, label_lists )
    """
elif _MODE == "post_process":
    predict_lists = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_try_cell_all_predict_list.pickle", "pickle")
    column_lists = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_try_cell_all_column_list.pickle", "pickle")
    label_lists = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_try_cell_all_label_list.pickle", "pickle")
    new_predicts_list = []
    new_labels_list = []
    for i in range(len(predict_lists)):
        temp = set()
        for j in range(len( predict_lists[i])):
            temp.add( (column_lists[i][j][0], column_lists[i][j][1], predict_lists[i][j]))
        ret_label_set, ret_predict_set = cpl_post_process_simple( temp, label_lists[i])
        new_predicts_list.append( ret_predict_set )
        new_labels_list.append( ret_label_set )
    save_data( (new_labels_list, new_predicts_list),"/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/evaluation/eval_results/cpl_data_cell_all_eval_pair_list.pickle")


# 获取提示词和label：return ret_list, new_label, first_column, contexts
prompt_temp_instruction = """
你是一名信息抽取专家，请你从法院判决文书上下文中抽取问题中要求的日期、金额或利率。请注意区分法院、原告、被告三者对同一事实的不同主张，不要张冠李戴。
（1）首先，你需要判断上下文中的信息是否包含问题要求的特定对象对某个案件事实的陈述，如果没有（很有可能是无效的上下文），请大胆回答<NOT FOUND>。
（2）其次，你要判断该数值是否是问题中 主体角色 的主张。例如，上下文中若只有原告主张归还500元，而问题是被告主张归还多少元时，不应该回答500。
"""
prompt_temp_input = """
相关上下文：{CONTEXT}
问题：{ROLE} {PREDICATE} {ATTRIBUTE}？
注意：{ATTENTION}
答案：
"""

PREDICATEs = {
    "法院": "判定",
    "原告": "诉称",
    "被告": "辩称",
}

def get_ruled_context_( predicate, entity, attr, hybrid_retriever):
    # 获取当前角色类型和名称
    entity_name = None
    entity_type = None
    for word in ["法院", "原告", "被告"]:
        if word in entity:
            entity_type = word
            entity_name = entity.split(" ")[1].replace("(", "").replace(")", "").strip()
            break
    # 获取ruled_text中对应的部分
    query = entity_type + predicate + attr + "？"
    context = hybrid_retriever.hybrid_retrieve( query, entity, attr)
    if entity_type == "被告":
        filter_context = []
        for line in context:
            if entity_name in line:
                filter_context.append( line )
        context = filter_context
    return context, cpl_keyword[attr]["warning"]


# 从label集合中获取答案，服务于ft
def get_ans_from_label( label, entity, attr ):
    entity_name = None
    entity_type = None
    for word in ["法院", "原告", "被告"]:
        if word in entity:
            entity_type = word
            entity_name = entity.split(" ")[1].replace("(", "").replace(")", "").strip()
            break
    if entity_name != None:
        for item in label:
            if item[0]==entity_name and item[1]==attr:
                return item[2]
    return "<NOT FOUND>"

def get_ready_context( contexts_ready, attr, entity_name ):
    attr_clean = attr if "1" not in attr else attr.replace("1", "")
    flag = 0
    for line in contexts_ready:
        clear_line = line.split("\n\n问题：")[1].split("\n主体角色")[0]
        if attr_clean in line and entity_name in line:
            flag = 1
            context = line
            break
    if flag == 0:
        context = []
    return context, cpl_keyword[attr]["warning"]


# 对单个文档，更新prompt和对应的label，返回可以直接评估的集合格式
def get_prompts_labels( entity_list, index, Plaintiff_claim_attributes, label, core_ruled_text, _entity_type=None, contexts_ready = None):
    ret_list = []
    first_column = []
    contexts = []

    # 处理标签
    new_label = set()
    for item in label:
        for ent in entity_list:
            try:
                if item[0] in ent:
                    item_type = ent
                    break
            except:
                raise Exception( f"{item}, {ent}")
        if _entity_type == None or _entity_type in item_type:
            new_label.add( item )

    attr_list = list(Plaintiff_claim_attributes.keys())
    # 遍历所有属性
    for i in tqdm(range(len(attr_list)), desc=f"正在处理第{index}个文档的属性"):
        attr = attr_list[i]
        if attr != "姓名名称":
            if "（元）" in attr:
                attr_typ = "money"
            elif "日期" in attr or "时间" in attr:
                attr_typ = "date"
            elif "（百分比或元）" in attr:
                attr_typ = "ratio"
            

            for j, entity in enumerate(entity_list):
                # 遍历形式['法院 (上海市闵行区人民法院)', '出借人（原告） (陈达奋)', '借款人（被告） (陈银森)', '借款人（被告） (郑丽珍)']
                if _entity_type==None or _entity_type in entity:
                    # entity_type为两个字
                    for word in ["法院", "原告", "被告"]:
                        if word in entity:
                            entity_type = word
                            entity_name = entity.split(" ")[1].replace("(", "").replace(")", "").strip()
                            break
                    if contexts_ready == None:
                        hybrid_retriever = CPL_Hybrid_Retriever( core_ruled_text[index], attr_typ, entity_type )
                    if contexts_ready != None:
                        context, attention = get_ready_context( contexts_ready, attr, entity_name )
                    else:
                        context, attention = get_ruled_context_( PREDICATEs[entity_type], entity, attr, hybrid_retriever)
                    # context, attention = get_ruled_context(  entity, attr, label)
                    if len(context)!=0:
                        contexts.append( context )
                        real_name = entity.split("(")[1].replace(")", "").strip()
                        first_column.append( [real_name, attr])
                        if "1" in attr:
                            _attr = attr.replace("1", "")
                        else:
                            _attr = attr
                        if _MODE == "test":
                            prompt = prompt_temp_instruction + prompt_temp_input.format( ROLE = entity, PREDICATE=PREDICATEs[entity_type], 
                                                                                        ATTRIBUTE=_attr, CONTEXT=context, ATTENTION=attention)
                        else:
                            prompt = {
                                "instruction" : prompt_temp_instruction,
                                "input" : prompt_temp_input.format( ROLE = entity, PREDICATE=PREDICATEs[entity_type], ATTRIBUTE=_attr, CONTEXT=context, ATTENTION=attention ),
                                "output": get_ans_from_label( label, entity, attr )     # 从label获取答案
                            }
                        ret_list.append( prompt )
    if contexts_ready!=None:
        contexts = contexts_ready
    return ret_list, new_label, first_column, contexts

new_prompt_lists = []
new_label_lists = []
first_column_lists = []
contexts_lists = []
# for i in range(len(label_lists)):
i = 0
ret_list, new_label, first_column, contexts = get_prompts_labels( entity_lists[i], i, Plaintiff_claim_attributes, 
                                                                label_lists[i], core_ruled_text, entity_type=None )
                                                                #, contexts_ready=context_lists[i])
new_prompt_lists.append( ret_list )
new_label_lists.append( new_label )
first_column_lists.append( first_column )
contexts_lists.append( contexts )

def compare_prompt( first_column_lists, new_label_lists ):
    prompt_count = 0
    label_count = 0
    same_count = 0
    role_dict = {}
    not_label = []
    for i in range( len(first_column_lists)):
        prompt_count += len( first_column_lists[i] )
        label_count += len( new_label_lists[i] )
        # 遍历标签
        for item in new_label_lists[i]:
            role = item[0]
            attr = item[1]
            if role not in role_dict:
                role_dict[role] = set()
            role_dict[role].add( attr )
        # 遍历提示词
        for item in first_column_lists[i]:
            role = item[0]
            attr = item[1]
            if role in role_dict and attr in role_dict[role]:
                same_count +=1                                  # 提示词中和标签一致的结构
            else:
                not_label.append( item )
    print(f"label有{label_count}个，提示词有{prompt_count}个，一样的有{same_count}个")
    return not_label


# not_label  = compare_prompt( first_column_lists, new_label_lists )      # label有2309个，提示词有3153个，一样的有2084个