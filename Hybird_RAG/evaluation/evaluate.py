"""
评估文件接口：
    将预测结果和标签列表以元组的形式存在测试目录下predict_results文件夹的dataset_type专属结果文件夹中
    元组中，label列表在第一个，predict在第二个，等长且列表中每个元素都为集合set()，有两种形式
    （1）元组集合：字段名+值的元组{('area', 'city centre'), ('customer rating', 'bad information')}
    （2）字符串集合：适用于first column这种不需要字段名的，如{'浙江省温州市瓯海区人民法院', '潘建眉', '郑恩明'},
    注意：全部小写，空值用bad information代替，每一次都要根据模型、Prompt给文件取一个特殊的名字
"""
from tqdm import tqdm
import pickle  
import numpy as np
import os
import sys
import json
import argparse

from sacrebleu import sentence_chrf
import bert_score

_Hybird_RAG_PATH = os.path.abspath(__file__)
for i in range(2):
    _Hybird_RAG_PATH = os.path.dirname( _Hybird_RAG_PATH )
sys.path.insert( 0, _Hybird_RAG_PATH)

metric_cache = dict()
bert_scorer = None

# （4）计算m*n相似度矩阵
def calc_similarity_matrix(tgt_data, pred_data, metric):
    def calc_data_similarity(tgt, pred):
        if isinstance(tgt, tuple):
            # 如果传入的是字段名+值的元组，两字段名和值分别组队传入，然后递归用乘积的方式获取元组的相似度
            # 即，如果字段名完全一样就是1，然后乘以值的相似度作为整体相似度
            ret = 1.0
            for tt, pp in zip(tgt, pred):
                ret *= calc_data_similarity(tt, pp)
            return ret

        if (tgt, pred) in metric_cache:
            return metric_cache[(tgt, pred)]

        if metric == 'E':
            ret = int(tgt == pred)
        elif metric == 'c':
            ret = sentence_chrf(pred, [tgt, ]).score / 100
        elif metric == 'BS-scaled':
            global bert_scorer
            if bert_scorer is None:
                bert_scorer = bert_score.BERTScorer( model_type="roberta-large", lang="en", rescale_with_baseline=True)
            ret = bert_scorer.score([pred, ], [tgt, ])[2].item()
            ret = max(ret, 0)
            ret = min(ret, 1)
        else:
            raise ValueError(f"Metric cannot be {metric}")

        metric_cache[(tgt, pred)] = ret
        return ret
    
    ret_table = []
    for tgt in tgt_data:
        temp = []
        for pred in pred_data:
            "对label和Predict进行全组合求相似度，即如果label集合中有m个元组，predict中有n个元素，则返回m*n的值矩阵，同时metric_cache避免重复运算"
            temp.append( calc_data_similarity(tgt, pred) )
        ret_table.append( temp )

    return np.array(ret_table, dtype=np.float64)

# （3）根据相似度矩阵求Precision、recall、f1
def metrics_by_sim(tgt_data, pred_data, metric):
    sim = calc_similarity_matrix(tgt_data, pred_data, metric)
    """
    对sim这个m*n的值矩阵的行、列求最大值，然后求平均
    每行的字段数=预测的字段数，即所有预测的字段中与label标签的最大值的序列，再平均
    """
    prec = np.mean(np.max(sim, axis=0))     
    recall = np.mean(np.max(sim, axis=1))
    if prec + recall == 0.0:
        f1 = 0.0
    else:
        f1 = 2 * prec * recall / (prec + recall)
    return prec, recall, f1

# （2）对处理完毕的data_pair求三个指标的相似度值
def three_level_eval( data_pair ):
    """
    data_pair：[ 标签（first cloumn, data cell）、预测（first cloumn, data cell）]
    """
    parts_names = ["First Column", "Data Cell"]
    score_s = [ 'E', 'c', 'BS-scaled']
    resutls_total = {}
    global metric_cache
    for part_index in range(2):
        "对first column和data cell两个部分"
        part_name = parts_names[part_index]
        resutls_total[part_name] = {}
        print( f"Evaluate {part_name}")
        _labels = data_pair[0][part_index]
        _preds = data_pair[1][part_index]
        
        for metric in score_s:
            relation_precision = []
            relation_recall = []
            relation_f1 = []
            # 清空全局的字典，对两个计算过的不重复计算
            metric_cache = dict()
            resutls_total[part_name][metric] = {}
            for hyp_table, tgt_table in tqdm(zip(_preds, _labels), total=len(_labels)):
                if len(tgt_table)==0:
                    if len(tgt_table)==len(hyp_table):
                        p, r, f = 1, 1, 1               # 对只有first column的查询，data cell部分计为1
                    else:
                        p, r, f = 0, 0, 0               # 目标为空，但预测值了
                elif len(hyp_table)==0:
                    p, r, f = 0, 0, 0                   # 预测为空，但目标不空
                else:
                    p, r, f = metrics_by_sim(tgt_table, hyp_table, metric)
                relation_precision.append(p)
                relation_recall.append(r)
                relation_f1.append(f)
            resutls_total[part_name][metric]['Precision'] = np.mean(relation_precision) * 100
            resutls_total[part_name][metric]['Recall'] =  np.mean(relation_recall) * 100
            resutls_total[part_name][metric]['F1-Score'] =  np.mean(relation_f1) * 100
    return resutls_total


def path_check( dataset_info, prompt_model_name ):
    data_info = dataset_info.split("/")
    eval_pair_path = os.path.join( _Hybird_RAG_PATH, f"temp/{data_info[0]}/{data_info[1]}/{data_info[2]}/eval_pair_list/{prompt_model_name}.pickle")
    results_save_path = os.path.join( _Hybird_RAG_PATH, f'evaluation/predict_results/{data_info[0]}_results/eval_results.json')
    return data_info, eval_pair_path, results_save_path

# （1）加载并准备data_pair，求完三个相似度值后进行打印和保存
def main( prompt_list_name, model_name, dataset_info):
    special_dataset = {
        "e2e":["name"]
    }
    unique_name = prompt_list_name+"_"+model_name
    data_info, eval_pair_path, results_save_path = path_check( dataset_info, unique_name )
    dataset_type = data_info[0]
    with open(eval_pair_path, 'rb') as f:  
        loaded_list = pickle.load(f)            # ( label_dict, predict_dict )
    test_sample_length = len(loaded_list[1])

    #（2）移除bad information，划分first_column和data cell
    data_pair = [ [ [], [] ],  [ [], [] ] ]         # [ 标签（first cloumn, data cell）、预测（first cloumn, data cell）]
    for i in range( test_sample_length ):
        # 对每个测试样本
        for j in range(2):
            # 分别处理标签值和预测值
            data_set = loaded_list[j]
            temp_first_column = set()
            temp_data_cell = set()
            for item in data_set[i]:
                # 移除bad information并分为first column和data cell
                if isinstance( item, str):
                    # 字符串集合一定为first colum，
                    if item not in ['bad information', "not found"]:
                        temp_first_column.add( item )
                elif isinstance( item, tuple):
                    # 元组集合在特殊数据集中为存在first colum，但大部分为data cell
                    if dataset_type in special_dataset and item[0] in special_dataset[dataset_type]:
                        temp_first_column.add( item[1] )
                    temp_data_cell.add( item )
            data_pair[j][0].append(temp_first_column )
            data_pair[j][1].append(temp_data_cell )
    
    #（3）对三个指标进行测试
    resutls_total = three_level_eval( data_pair )
    #（4）打印eval结果
    parts_names = ["First Column", "Data Cell"]
    score_s = [ 'E', 'c', 'BS-scaled']
    for part in parts_names:
        print( f"Results of {part}:")
        for i in range(3):
            print(f"Method {score_s[i]}: precision = %.2f; recall = %.2f; f1 = %.2f" % (
                resutls_total[part][score_s[i]]['Precision'], resutls_total[part][score_s[i]]['Recall'], resutls_total[part][score_s[i]]['F1-Score'] ))
    
    #（6）保存eval结果：每个数据集都有一个json结果文件，先读取，再追加，最后写入
    with open( results_save_path, encoding='utf-8-sig', mode='r') as f:  
        data = json.load(f)
    data[f"{data_info[0]}_{data_info[1]}_{data_info[2]}_{unique_name}"] = resutls_total     # 以键值对保存结果
    with open( results_save_path, encoding='utf-8',mode='w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description="Run script with external arguments")
    parser.add_argument('--prompt_list_name', type=str, required=True, help='提示词文件名')
    parser.add_argument('--model_name', type=str, required=True, help='模型路径')
    parser.add_argument('--dataset_info', type=str, required=True, help='表示独特性的字符串')
    args = parser.parse_args()
    # 获取参数值
    
    prompt_list_name = args.prompt_list_name
    model_name = args.model_name
    dataset_info = args.dataset_info
    """
    prompt_list_name = "prompt_list_rag"
    dataset_info = "cpl/table1/first_column"
    model_name = "chatglm3-6b"
    """
    main( prompt_list_name, model_name, dataset_info )
    
    
    

    
    
    


