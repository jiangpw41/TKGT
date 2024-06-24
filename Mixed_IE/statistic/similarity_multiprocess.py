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
import torch.multiprocessing as mp
from queue import Empty
import threading 

import sys
sys.path.insert(0, os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ))))
from kgs.dataset_kgs.e2e_rotowire_field import fields_list_rotowire, fields_list_e2e
from kgs.dataset_kgs.CPL_field import fields_list_CPL
from kgs.dataset_kgs.wiki_field import fields_list_wikitabletext, fields_list_wikibio

model_name_or_path="/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/bce-embedding-base_v1"     # 中英双语https://github.com/netease-youdao/BCEmbedding/blob/master/README_zh.md
device_list = [f'cuda:{i}' for i in range(8)]
root_path = "/home/jiangpeiwen2/jiangpeiwen2/text-kgs-table/components/mix_ie/further_processed/statistic/"
file_list = ["rotowire", "e2e", "wikitabletext", "CPL", "wikibio"]  # , 
file_name = "freq_all.json"
batch_size = 1
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

def _embedding( word_list, model, tokenizer, device ):
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

def descend_list_sim( task_list, ret_list, index, fields ):
    num = index
    index = index%8
    device = device_list[index]
    model = AutoModel.from_pretrained(model_name_or_path).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    fields_emb_list = _embedding(fields, model, tokenizer, device)
    print(f"Process {num} Start")
    while True:
        key = task_list.get()
        if key=="<STOP>":
            ret_list.put( ("<STOP>",None, None) )
            break
        key = [key]
        embeded_list = _embedding(key, model, tokenizer, device)
        simi_matrix = cos_similarity_torch(embeded_list, fields_emb_list)[0]    #输出结果是batch_size, len(fields_emb_list)
        # 计算一个向量的7种指标
        metric = []
        #lens = len(simi_matrix)
        metric.append( sum(simi_matrix).to('cpu').item() )               # 总和
        #metric.append( metric[0]/lens )                # 平均数
        metric.append( max(simi_matrix).to('cpu').item() )              # 最大值
        #metric.append( simi_matrix[ lens//2 ].to('cpu' ))   # 中位数

        #sorted_ve = torch.sort(simi_matrix, descending=True).values[ lens//20:19*lens//20 ].to('cpu' )
        #metric.append( sum(sorted_ve) )               # 去除最大最小总和
        #metric.append( metric[-1]/len(sorted_ve)  )                # 去除最大最小平均数
        #metric.append( max(sorted_ve))            # 去除最大最小最大值

        #save_dict = 
        ret_list.put((key[0], metric[0], metric[1]), block = True)
    print(f"Process {num} quit")


def norm(save_dict):
    ret_dict = {}
    max_min = [[0, float('inf')] for _ in range(2)]
    for i in range(len(max_min)):
        for key, value in tqdm(save_dict.items(), desc="Find Max"):
            current_value = value[i]
            max_min[i][0] = max(max_min[i][0], current_value)
            max_min[i][1] = min(max_min[i][1], current_value)
        
        spans = max_min[i][0]-max_min[i][1]
        mins = max_min[i][1]
        for key, value in tqdm(save_dict.items(), desc="Norm"):
            if i==0:
                ret_dict[key] = []
            ret_dict[key].append( (value[i] - mins)/(spans+1e-10) )
    return ret_dict

def main():
    dataset_index = 4
    dic_path = os.path.join(root_path, file_list[dataset_index] )
    fields = field_parser( fields_list[dataset_index], dataset_index )
    with open( os.path.join(dic_path,file_name), "r" ) as file:
        freqs = json.load(file)
    # embedding字段列表
    _basename = os.path.basename(dic_path)
    if _basename=="CPL":
        freqs = freqs["TT_freq"]
    
    save_dict = OrderedDict()
    send = 0

    with mp.Manager() as manager:
        work_num = 40
        task_list_start = [ mp.Queue() for i in range(work_num)]
        task_end = mp.Queue()
        Process_Pool = [ mp.Process(target=descend_list_sim, args=(task_list_start[i], task_end, i , fields )) for i in range(work_num)]
        for process in Process_Pool:
            process.start()

        for i, key in enumerate(freqs, start=0):
            if key!="_Overview":
                save_dict[key] = None
                task_list_start[ i % work_num].put( key )
                send += 1
                #if send==10:
                #    break
        for j in range( work_num ):
            task_list_start[ j ].put( "<STOP>" )

        quit_num = 0
        
        pbar = tqdm(total=send)
        while True:
            if quit_num==work_num:
                print("QQQQ")
                break
            key, sums, maxs = task_end.get()
            if key== "<STOP>":
                print(f"{quit_num} quit")
                quit_num += 1
                continue
            save_dict[key] = (sums, maxs)
            pbar.update(1)
        with open( os.path.join(dic_path, f"embedding_all_1.pkl"), 'wb') as f:  
            pickle.dump(save_dict, f)
        
        
        ret_dict = norm(save_dict)
        with open( os.path.join(dic_path, f"embedding_all.pkl"), 'wb') as f:  
            pickle.dump(ret_dict, f)
        
        
        for process in Process_Pool:
            process.join()
def normsss():
    dataset_index = 4
    dic_path = os.path.join(root_path, file_list[dataset_index] )
    with open( os.path.join(dic_path, f"embedding_all_1.pkl"), 'rb') as f:  
        save_dict = pickle.load(f)
    ret_dict = norm(save_dict)
        
    with open( os.path.join(dic_path, f"embedding_all.pkl"), 'wb') as f:  
        pickle.dump(ret_dict, f)

if __name__=="__main__":
    current_start_method = mp.get_start_method(allow_none=True)
    if current_start_method != 'spawn':
        mp.set_start_method('spawn', force=True)
    main()
    #normsss()