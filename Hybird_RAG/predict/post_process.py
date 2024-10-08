
"""
对于任意函数
（1）处理预测结果，清理预测结果中的bad outputs（用外挂函数解决）
（2）组成(label, predict)列表对保存到eval_pair中
"""
import argparse
import os
import sys
import pickle


_Hybird_RAG_PATH = os.path.abspath(__file__)
for i in range(2):
    _Hybird_RAG_PATH = os.path.dirname( _Hybird_RAG_PATH )
sys.path.insert( 0, _Hybird_RAG_PATH)
from predict.dataset_postprocess_tool.cpl import post_process_cpl


def post_process( dataset_type, index, _predict, _label, not_process  ):
    if not_process:                                                         # 不进行工程处理则直接返回
        return _label, _predict
    if dataset_type=="cpl":
        court_name_rule = True
        return post_process_cpl( index, _predict, _label, court_name_rule )
    else:
        raise Exception("Not Post-Porcessed")

def path_check( dataset_info, prompt_model_name ):
    data_info = dataset_info.split("/")
    predict_path = os.path.join( _Hybird_RAG_PATH, f"temp/{data_info[0]}/{data_info[1]}/{data_info[2]}/predict_list/{prompt_model_name}.pickle")
    label_path = os.path.join( _Hybird_RAG_PATH, f"temp/{data_info[0]}/{data_info[1]}/{data_info[2]}/label_list/{prompt_model_name}.pickle")
    eval_pair_path = os.path.join( _Hybird_RAG_PATH, f"temp/{data_info[0]}/{data_info[1]}/{data_info[2]}/eval_pair_list/{prompt_model_name}.pickle")

    return predict_path, label_path, eval_pair_path, data_info

def main( prompt_list_name, model_name, dataset_info, not_process ):
    predict_path, label_path, eval_pair_path, data_info = path_check( dataset_info, prompt_list_name+"_"+model_name )              # 加载数据
    dataset_type = data_info[0]
    table_num = data_info[1]
    data_part = data_info[2]
    with open( predict_path, 'rb') as f: 
        total_predict = pickle.load(f)
    with open( label_path, 'rb') as f: 
        total_label = pickle.load(f)
    if len(total_label)!=len(total_predict):
        raise Exception(f"预测结果{len(total_predict)}和标签长度{len(total_label)}不一致")
    
    ret_label_list = []
    ret_predict_list = []
    if not_process:
        print("not_process为True，不进行工程后处理")
    else:
        print("not_process为False，进行工程后处理")
    for i in range( len(total_label) ):                                                                             # 遍历处理
        _predict = total_predict[i]
        _label = total_label[i]
        ret_label, ret_predict = post_process( dataset_type, i, _predict, _label, not_process )
        ret_label_list.append(ret_label)
        ret_predict_list.append(ret_predict )

    with open( eval_pair_path, 'wb') as f:                                                                          # 保存
        # 使用pickle.dump()保存列表  
        pickle.dump((ret_label_list, ret_predict_list), f) 
    



if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description="Run script with external arguments")
    parser.add_argument('--prompt_list_name', type=str, required=True, help='提示词文件名')
    parser.add_argument('--model_name', type=str, required=True, help='模型路径')
    parser.add_argument('--dataset_info', type=str, required=True, help='表示独特性的字符串')
    parser.add_argument('--not_process', type=int, required=False, help='是否使用工程方法后处理')
    args = parser.parse_args()
    # 获取参数值
    prompt_list_name = args.prompt_list_name
    model_name = args.model_name
    dataset_info = args.dataset_info
    not_process = False if args.not_process==None else args.not_process
    """
    prompt_list_name = "prompt_list_rag"
    dataset_info = "cpl/table1/first_column"
    model_name = "chatglm3-6b"
    not_process = False
    """
    main( prompt_list_name, model_name, dataset_info, not_process )