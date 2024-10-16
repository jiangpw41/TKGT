"""
评估文件接口：
    将预测结果和标签列表以元组的形式存在测试目录下eval_results文件夹的dataset_type专属结果文件夹中
    元组中，label列表在第一个，predict在第二个，等长且列表中每个元素都为集合set()，有两种形式
    （1）二元组集合：字段名+值的元组{('area', 'city centre'), ('customer rating', 'bad information')}，单实体
    （2）三元组集合：实体名+字段名+值得元组{('name', 'field', 'value')}，多实体
    注意：全部小写，空值用bad information代替，每一次都要根据模型、Prompt给文件取一个特殊的名字
"""
from tqdm import tqdm
import pickle  
import numpy as np
import os
import sys
import json
import argparse
from datetime import datetime
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

# （2）将二、三元组准备为评估数据
def parse_table_to_data( table, col_header):
    row_set = set()
    col_set = set()
    for item in table:
        if col_header==False:
            if len( item )==2:
                row_set.add( item[0] )
            else:
                raise Exception(f"元组长度{len( item )}与任务类型col_header=False不匹配！")
        else:
            if len( item )==3:
                row_set.add( item[0] )
                col_set.add( item[1] )
            else:
                raise Exception(f"元组长度{len( item )}与任务类型col_header=True不匹配！")
    return row_set, col_set, table

# （1）路径和形式检查并加载
def path_check_and_load( dataset, hyp_tgt_pair_name, eval_type ):
    label_path = os.path.join( _Hybird_RAG_PATH, f"temp/{dataset}/{dataset}_labels.pickle")
    predict_path = os.path.join( _Hybird_RAG_PATH, f"temp/{dataset}/predicts/{hyp_tgt_pair_name}.pickle")
    if not os.path.exists( label_path ) or not os.path.exists( predict_path ):
        raise Exception(f"Labels或Predicts文件至少一个不存在，请检查{hyp_tgt_pair_name}！")
    with open(label_path, 'rb') as f:  
        labels = pickle.load(f)
    with open(predict_path, 'rb') as f:  
        predicts = pickle.load(f)
    if len(labels)!=len(predicts):
        raise Exception( "Label和Predict results列表长度不一致！" )
    for item in predicts[0]:
        _len = len(item)        # 获取预测列表中第一个集合中任意一个元组的长度
    if (_len==2 and eval_type=="multi_entity") or (_len==3 and eval_type=="single_entity"):
        raise Exception(f"元组长度{_len}与测试类型{eval_type}不匹配!")
    results_save_path = os.path.join( _Hybird_RAG_PATH, f'evaluation/eval_results/{dataset}_results.json')
    # # ( label_dict, predict_dict )
    return (labels, predicts), results_save_path


def main( dataset, unique_name, eval_type):
    loaded_pair_list, results_save_path = path_check_and_load( dataset, unique_name , eval_type)

    row_header_precision = []
    row_header_recall = []
    row_header_f1 = []
    col_header_precision = []
    col_header_recall = []
    col_header_f1 = []
    relation_precision = []
    relation_recall = []
    relation_f1 = []

    row_header = True
    col_header = False if eval_type=="single_entity" else True
    score_s = [ 'E', 'c', 'BS-scaled']
    resutls_total = {}
    global metric_cache
    for metric in score_s:
        resutls_total[f"Score_{metric}"]={
            "FirstColumn":[],
            "DataCell":[]
        }
        if col_header:
            resutls_total[f"Score_{metric}"]["TableHeader"]=[]
        for hyp_table, tgt_table in tqdm(loaded_pair_list, total=len(loaded_pair_list[0])):
            #两者都存在，则计算指标
            #返回两个表格的表头、列名和中间关系的set无序数据集
            hyp_row_headers, hyp_col_headers, hyp_relations = parse_table_to_data(hyp_table, col_header)
            tgt_row_headers, tgt_col_headers, tgt_relations = parse_table_to_data(tgt_table, col_header)

            if row_header:
                p, r, f = metrics_by_sim(tgt_row_headers, hyp_row_headers, metric)
                row_header_precision.append(p)
                row_header_recall.append(r)
                row_header_f1.append(f)
            if col_header:
                p, r, f = metrics_by_sim(tgt_col_headers, hyp_col_headers, metric)
                col_header_precision.append(p)
                col_header_recall.append(r)
                col_header_f1.append(f)
            if len(hyp_relations) == 0:
                relation_precision.append(0.0)
                relation_recall.append(0.0)
                relation_f1.append(0.0)
            else:
                p, r, f = metrics_by_sim(tgt_relations, hyp_relations, metric)
                relation_precision.append(p)
                relation_recall.append(r)
                relation_f1.append(f)

            if row_header:
                resutls_total[f"Score_{metric}"]["FirstColumn"] = [np.mean(row_header_precision) * 100,
                                                                   np.mean(row_header_recall) * 100,
                                                                   np.mean(row_header_f1) * 100]
                print("Row header: precision = %.2f; recall = %.2f; f1 = %.2f" % (
                    np.mean(row_header_precision) * 100, np.mean(row_header_recall) * 100, np.mean(row_header_f1) * 100))
            if col_header:
                resutls_total[f"Score_{metric}"]["TableHeader"] = [np.mean(col_header_precision) * 100,
                                                                   np.mean(col_header_recall) * 100,
                                                                   np.mean(col_header_f1) * 100]
                print("Col header: precision = %.2f; recall = %.2f; f1 = %.2f" % (
                    np.mean(col_header_precision) * 100, np.mean(col_header_recall) * 100, np.mean(col_header_f1) * 100))
            resutls_total[f"Score_{metric}"]["DataCell"] = [np.mean(relation_precision) * 100,
                                                            np.mean(relation_recall) * 100,
                                                            np.mean(relation_f1) * 100]
            print("Non-header cell: precision = %.2f; recall = %.2f; f1 = %.2f" % (
                np.mean(relation_precision) * 100, np.mean(relation_recall) * 100, np.mean(relation_f1) * 100))
    # 保存eval结果：每个数据集都有一个json结果文件，先读取，再追加，最后写入
    now = datetime.now()
    human_readable_time = now.strftime("%Y-%m-%d %H:%M:%S") 
    with open( results_save_path, encoding='utf-8-sig', mode='r') as f:  
        data = json.load(f)
    data[ hyp_tgt_pair_name+f"_{human_readable_time}" ] = resutls_total     # 以键值对保存结果
    with open( results_save_path, encoding='utf-8',mode='w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description="Run script with external arguments")
    parser.add_argument('--dataset', type=str, required=True, help='数据集名称')
    parser.add_argument('--eval_type', type=str, required=True, help='single_entity or multi_entity')
    parser.add_argument('--unique_name', type=str, required=True, help='表示独特性的字符串')
    args = parser.parse_args()
    # 获取参数值
    dataset = args.dataset
    eval_type = args.eval_type
    unique_name = args.unique_name
    
    """
    dataset = "prompt_list_rag"
    eval_type = args.eval_type
    unique_name = args.unique_name
    """
    main( dataset, unique_name, eval_type )
    
    
    

    
    
    


