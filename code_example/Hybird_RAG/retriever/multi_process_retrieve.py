import logging
import json
import pickle
import time
import pandas as pd
import random

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

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from modelscope.models import Model
from modelscope.pipelines import pipeline
# Version less than 1.1 please use TextRankingPreprocessor
from modelscope.preprocessors import TextRankingTransformersPreprocessor
from modelscope.utils.constant import Tasks

from tqdm import tqdm
import concurrent
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
import torch




PREDICATEs = {
    "法院": "判定",
    "原告": "诉称",
    "被告": "辩称",
}

"""
model_dict = []
for gpu in range( 8 ):
    #for time_ in range(7):
    temp = []
    for i in range(7):
        # os.environ["CUDA_VISIBLE_DEVICES"]  = str(gpu)
        torch.cuda.set_device(gpu)
        embed_model = HuggingFaceEmbedding(
            model_name="/home/jiangpeiwen2/jiangpeiwen2/LlamaIndex/model/sentence-transformer"
        )
        rerank_pipeline = pipeline(task=Tasks.text_ranking, model='damo/nlp_rom_passage-ranking_chinese-base', model_revision='v1.1.0', device=f"cuda:{gpu}")
        #model_dict.append( embed_model )
        temp.append( (embed_model, rerank_pipeline) )
    model_dict.append( temp )
"""

def retrieve_class( core_ruled_text, entity, attr, ids):
    if "（元）" in attr:
        attr_typ = "money"
    elif "日期" in attr or "时间" in attr:
        attr_typ = "date"
    elif "（百分比或元）" in attr:
        attr_typ = "ratio"
    
    for word in ["法院", "原告", "被告"]:
        if word in entity:
            entity_type = word
            entity_name = entity.split(" ")[1].replace("(", "").replace(")", "").strip()
            break
    predicate = PREDICATEs[entity_type]

    gpu_id = ids%8
    num_id = ids//8
    # embed_model, rerank_model = model_dict[gpu_id ][num_id][0], model_dict[gpu_id ][num_id][1]
    hybrid_retriever = CPL_Hybrid_Retriever( core_ruled_text, attr_typ, entity_type, gpu_id = gpu_id )

    # 获取ruled_text中对应的部分
    query = entity_type + predicate + attr + "？"
    if "1" in attr:
        _attr = attr.replace("1", "")
    else:
        _attr = attr
    context = hybrid_retriever.hybrid_retrieve( query, entity, _attr)
    if entity_type == "被告":
        filter_context = []
        for line in context:
            if entity_name in line:
                filter_context.append( line )
        context = filter_context
    return context, cpl_keyword[attr]["warning"]


def multi_process_retrieve( processor, task_list, core_ruled_text, task_description ):
    # 所有使用多进程工具的函数，必须将迭代对象及其index作为函数参数的前两位
    retrieved_task_list = [None]*len(task_list)
    with ProcessPoolExecutor() as executor:
        future_to_item = {}
        for j, item in enumerate(task_list):
            entity, attr = item[0], item[1]
            future_to_item[executor.submit( processor, core_ruled_text, entity, attr, j % 8)] = j 
        with tqdm(total=len(future_to_item), desc=f"Preprocess {task_description}") as pbar:
            for future in concurrent.futures.as_completed(future_to_item): 
                context, attention = future.result()
                retrieved_task_list[ future_to_item[future]] = (context, attention)
                pbar.update(1)
    return retrieved_task_list


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


# 从label集合中获取答案，服务于ft
def get_ans_from_label( label, entity_name, attr ):
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
def get_prompts_labels( entity_list, index, Plaintiff_claim_attributes, label, core_ruled_text, _MODE, _entity_type=None, contexts_ready = None, prepare_context = [], times = 0):
    ret_list = []
    first_column = []
    contexts = []
    # 处理标签
    if len(prepare_context)!=0 :
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

    attr_list = list( Plaintiff_claim_attributes.keys() )
    # 遍历所有属性
    count = 0
    for i in tqdm(range(len(attr_list)), desc=f"正在处理第{index}个文档的属性"):
        raw_attr = attr_list[i]
        if "1" in raw_attr:
            attr = raw_attr.replace("1", "")
        else:
            attr = raw_attr
        if attr != "姓名名称":
            ranges = [0, 3] if times == 0 else [3, len( entity_list)]
            for j in range( ranges[0], ranges[1]  ):
                entity = entity_list[j]
                # 遍历形式['法院 (上海市闵行区人民法院)', '出借人（原告） (陈达奋)', '借款人（被告） (陈银森)', '借款人（被告） (郑丽珍)']
                if _entity_type==None or _entity_type in entity:
                    # entity_type为两个字
                    for word in ["法院", "原告", "被告"]:
                        if word in entity:
                            entity_type = word
                            entity_name = entity.split(" ")[1].replace("(", "").replace(")", "").strip()
                            break
                    # 如果准备好列表为空，说明处于构建阶段
                    if len(prepare_context)==0:
                        ret_list.append( (entity, raw_attr))
                    # 否则，处于收获阶段
                    else:
                        context, attention = prepare_context[ count ]
                        count += 1
                        contexts.append( context )
                        if len(context)!=0:
                            first_column.append( [entity_name, raw_attr])
                            if _MODE == "test":
                                prompt = prompt_temp_instruction + prompt_temp_input.format( ROLE = entity, PREDICATE=PREDICATEs[entity_type], 
                                                                                            ATTRIBUTE=attr, CONTEXT=context, ATTENTION=attention)
                            else:
                                prompt = {
                                    "instruction" : prompt_temp_instruction,
                                    "input" : prompt_temp_input.format( ROLE = entity, PREDICATE=PREDICATEs[entity_type], ATTRIBUTE=attr, CONTEXT=context, ATTENTION=attention ),
                                    "output": get_ans_from_label( label, entity_name, attr )     # 从label获取答案
                                }
                            ret_list.append( prompt )
    if contexts_ready!=None:
        contexts = contexts_ready
    if len(prepare_context)==0:
        return ret_list
    else:
        return ret_list, new_label, first_column, contexts
    

def main_main(  _MODE ):
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
    #################################################################################
    new_prompt_lists = []
    new_label_lists = []
    first_column_lists = []
    contexts_lists = []
    for i in range( len(label_lists)):
        struct_list = get_prompts_labels( entity_lists[i], i, Plaintiff_claim_attributes, label_lists[i], core_ruled_text[i], _MODE, 
                                         _entity_type=None, contexts_ready = None, prepare_context = [])
        time_list = []
        if len(struct_list) > 80:
            time_list.append( struct_list[: 80])
            time_list.append( struct_list[ 80: ])
        else:
            time_list.append( struct_list )
        
        new_prompt_lists_part = []
        new_label_lists_part = []
        first_column_lists_part = []
        contexts_lists_part = []
        for t, part_list in enumerate(time_list):
            task_description = f"第{i}个文档处理中"
            part_context_list = multi_process_retrieve( retrieve_class, part_list, core_ruled_text[i], task_description )
            ret_list, new_label, first_column, contexts = get_prompts_labels( entity_lists[i], i, Plaintiff_claim_attributes, label_lists[i], core_ruled_text[i], _MODE, 
                                            _entity_type=None, contexts_ready = None, prepare_context = part_context_list, times = t)
            new_prompt_lists_part.extend( ret_list )
            new_label_lists_part.extend( new_label )
            first_column_lists_part.extend( first_column )
            contexts_lists_part.extend( contexts )
        new_prompt_lists.append( new_prompt_lists_part )
        new_label_lists.append( new_label_lists_part )
        first_column_lists.append( first_column_lists_part )
        contexts_lists.append( contexts_lists_part )
    if _MODE == "test":
        save_data( new_prompt_lists, "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_try_cell_all_prompt_list.pickle")
        save_data( new_label_lists, "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_try_cell_all_label_list.pickle")
        save_data( first_column_lists, "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_try_cell_all_column_list.pickle")
        save_data( contexts_lists, "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_try_cell_all_context_list.pickle")
    else:
        save_data( new_prompt_lists, "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_cell_all_ft_normal.json")
        save_data( contexts_lists, "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/cpl/cpl_data_try_cell_all_ft_context_list.pickle")

def main():
    for _MODE in [ "test", "train"]:
        main_main(  _MODE )

if __name__ == "__main__":
    mp.set_start_method('spawn', force=True)
    main( )
        
        