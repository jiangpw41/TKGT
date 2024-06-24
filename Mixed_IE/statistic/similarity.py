'''
计算每个数据集的总词频表与其字段语义相似度之和的max-min归一化值
'''
# scipy Version: 1.13.1
# gensim Version: 4.3.2
import numpy as np
import json
import os
from collections import Counter, OrderedDict
from transformers import AutoModel, AutoTokenizer
import torch
from tqdm import tqdm
import gc
import pickle
import concurrent
from concurrent.futures import ProcessPoolExecutor

import sys
sys.path.insert(0, os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ))))
from kgs.dataset_kgs.e2e_rotowire_field import fields_list_rotowire, fields_list_e2e
from kgs.dataset_kgs.CPL_field import fields_list_CPL
from kgs.dataset_kgs.wiki_field import fields_list_wikitabletext, fields_list_wikibio


os.environ['TOKENIZERS_PARALLELISM'] = 'true'
model_name_or_path="/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/bce-embedding-base_v1"     # 中英双语https://github.com/netease-youdao/BCEmbedding/blob/master/README_zh.md
device = 'cpu'
root_path = "/home/jiangpeiwen2/jiangpeiwen2/text-kgs-table/components/mix_ie/further_processed/statistic/"
file_list = ["rotowire", "e2e", "wikitabletext", "CPL", "wikibio"]  # , 
file_name = "freq_all.json"
fields_list = [fields_list_rotowire, fields_list_e2e,  fields_list_wikitabletext, fields_list_CPL, fields_list_wikibio]


def field_parser( fields, index):
    if index==2 or index==4:    # wiki
        return fields
    else:   # e2e
        ret = []
        for para_key in fields:
            table_field = fields[para_key]
            for key in table_field["Row_Name"]:
                ret.append( key )
            for key in table_field["Fields"]:
                ret.append( key )
        return ret



def _embedding( word_list, model, tokenizer ):
    # 张量
    
    with torch.no_grad():
    # 输入若为字符串，返回shape=(1, 768)；如果为字符串列表（长度为n），返回shape=(n, 768)
        inputs = tokenizer(word_list, padding=True, truncation=True, max_length=512, return_tensors="pt")
        inputs_on_device = {k: v.to(device) for k, v in inputs.items()}
        # get embeddings
        outputs = model(**inputs_on_device, return_dict=True)
        embeddings = outputs.last_hidden_state[:, 0]  # cls pooler
        embeddings = embeddings / embeddings.norm(dim=1, keepdim=True)  # normalize
    return embeddings


def cos_similarity_torch(tensor1, tensor2):  
    # 确保tensor1和tensor2是PyTorch张量，并且数据类型是float  
    tensor1 = tensor1.float()  
    tensor2 = tensor2.float()  
  
    # 计算tensor1和tensor2的L2范数（即向量的长度）  
    norm_tensor1 = torch.norm(tensor1, dim=1, keepdim=True)  
    norm_tensor2 = torch.norm(tensor2, dim=1, keepdim=True)  
  
    # 转置tensor2，并计算其范数的转置
    norm_tensor2_t = norm_tensor2.t()
  
    # 扩展norm_tensor1的维度以匹配norm_tensor2_t
    norm_tensor1_expanded = norm_tensor1.expand(tensor1.shape[0], tensor2.shape[0])
    # 扩展norm_tensor2_t的维度以匹配norm_tensor1_expanded
    norm_tensor2_t_expanded = norm_tensor2_t.expand(tensor1.shape[0], tensor2.shape[0])
    
    # 计算tensor1和tensor2^T的点积（即矩阵乘法），得到一个(m, k)的矩阵  
    dot_product = torch.matmul(tensor1, tensor2.t())  
  
    # 避免除以零
    norm_product = norm_tensor1_expanded * norm_tensor2_t_expanded
    norm_product[norm_product == 0] = 1e-10
    
    # 计算余弦相似度矩阵  
    cosine_similarity_matrix = dot_product / norm_product  
    # 在 cos_similarity_torch 函数的最后
    return cosine_similarity_matrix

def processor(key, model, tokenizer, fields_emb_list):
    key = [key]
    embeded_list = _embedding(key, model, tokenizer)
    simi_matrix = cos_similarity_torch(embeded_list, fields_emb_list)[0]    #输出结果是batch_size, len(fields_emb_list)
    # 计算一个向量的7种指标
    metric = []
    lens = len(simi_matrix)
    metric.append( sum(simi_matrix).to('cpu') )               # 总和
    metric.append( metric[0]/lens )                # 平均数
    metric.append( max(simi_matrix).to('cpu') )              # 最大值
    metric.append( simi_matrix[ lens//2 ].to('cpu' ))   # 中位数

    sorted_ve = torch.sort(simi_matrix, descending=True).values[ lens//20:19*lens//20 ].to('cpu' )
    metric.append( sum(sorted_ve) )               # 去除最大最小总和
    metric.append( metric[-1]/len(sorted_ve)  )                # 去除最大最小平均数
    metric.append( max(sorted_ve))            # 去除最大最小最大值

    return [key[0], metric]

def multi_process( processor, task_list, task_description):
    # 所有使用多进程工具的函数，必须将迭代对象及其index作为函数参数的前两位
    splited_task_list = [None]*len(task_list)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    model = AutoModel.from_pretrained(model_name_or_path)
    model.to(device)
    fields = field_parser( fields_list[4], 4 )
    fields_emb_list = _embedding(fields, model, tokenizer)
    with ProcessPoolExecutor() as executor:
        future_to_item = {}
        for j, item in enumerate(task_list):
            future_to_item[executor.submit(processor, item, model, tokenizer, fields_emb_list)] = j 
        with tqdm(total=len(future_to_item), desc=f"Preprocess {task_description}") as pbar:
            for future in concurrent.futures.as_completed(future_to_item): 
                splited_task_list[ future_to_item[future]] = future.result()
                pbar.update(1)
    return splited_task_list

def cac_sim( ):
    dic_path = os.path.join(root_path, file_list[4] )
    with open( os.path.join(dic_path,file_name), "r" ) as file:
        freqs = json.load(file)
    task_list = []
    limitation = 400000
    send = 0
    for i, key in enumerate(freqs, start=0):
        if key!="_Overview":
            if send <= limitation:
                send += 1
                continue
            else:
                task_list.append(key)
    task_description = "400000后"
    splited_task_list = multi_process( processor, task_list, task_description)
    save_dict = OrderedDict()
    for i in range(len(splited_task_list)):
        save_dict[splited_task_list[0]] = splited_task_list[1]
    with open( os.path.join(dic_path, f"embedding_all_2.pkl"), 'wb') as f:  
        pickle.dump(save_dict, f)


if __name__=="__main__":
    cac_sim()
    #aa = processor("你好")