'''
停用词、词性标注、命名实体识别后分类统计
'''
import nltk  
from nltk.tokenize import word_tokenize  
from nltk.tag import pos_tag  
import spacy  
from spacy.lang.en.stop_words import STOP_WORDS  

from collections import Counter, OrderedDict
import pickle
import json
import os
import sys
from tqdm import tqdm
import concurrent
from concurrent.futures import ProcessPoolExecutor
import glob

_IE_PATH = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
sys.path.insert(0, _IE_PATH)
from functions import read_text_to_list
from config import stop_pos_en, Supplementary_stop_words_en

_ROOT_PATH = os.path.dirname( _IE_PATH )
sys.path.insert(0, _ROOT_PATH)
from utils import create_logger

_DATA_PATH = os.path.join(_ROOT_PATH, "raw")
_SAVE_Path = os.path.join(_ROOT_PATH, "Mixed_IE/further_processed/statistic")

_SETS= ['rotowire', 'e2e', 'wikitabletext', 'wikibio']
_TYPES = [ 'valid', 'test', 'train']

# _SCRIPT_PATH = os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) )

def pipeline( sentence ):
    '''
    使用nltk进行分词、词性标注、停用词库，使用spaCy进行命名实体识别。
    对每句话进行分词、词性标注、命名实体识别，并过滤停用词、停用词性，最后将处理完的词分三类进行统计返回。
    nltk库可以直接Pip但默认下载到用户根目录，此外，其数据包很难下载，建议直接git clone项目后将需要的数据放到pip下载的目录下
    # 确保已经下载了punkt和averaged_perceptron_tagger模型  
    # nltk.download('punkt')  
    # nltk.download('averaged_perceptron_tagger')
    '''
    stop_words = set(STOP_WORDS) 
    tokens = word_tokenize(sentence)  
    tagged = pos_tag(tokens)  
    filtered_tokens_class = {
        "Number":[],
        "NNP":[],
        "NN":[],
        "VB":[],
        "JJRB": [],
        "General": [],
    }
    
    filter_tok = [] 
    stop_words.update(Supplementary_stop_words_en)

    for token, pos in tagged:  
        if token.lower() not in stop_words and pos not in stop_pos_en:
            if pos =="CD":
                filtered_tokens_class["Number"].append( (token, pos))
            elif pos in ["NNP", "NNPS"]: # 专有名词，单复数形式
                filtered_tokens_class["NNP"].append( (token, pos))
                filter_tok.append( token.lower() )
            elif pos in ["NN", "NNS"]: # 常用名词，单复数形式
                filtered_tokens_class["NN"].append( (token, pos))
                filter_tok.append( token.lower() )
            elif pos in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]: # 动词各种形式
                filtered_tokens_class["VB"].append( (token, pos))
                filter_tok.append( token.lower() )
            elif pos in ["JJ", "JJR", "JJS", "RB", "RBR", "RBS"]: # 形容词副词各种形式
                filtered_tokens_class["JJRB"].append( (token, pos))
                filter_tok.append( token.lower() )
            else:
                filtered_tokens_class["General"].append( (token, pos))
                filter_tok.append( token.lower() )
    # 返回词性标注且过滤后的词（字典，用于存放）、所有过滤过的词（用于统计），未过滤的所有词的长度
    return  filtered_tokens_class, filter_tok, len(tokens)

def multi_process( processor, task_list , descs):
    # 所有使用多进程工具的函数，必须将迭代对象及其index作为函数参数的前两位
    splited_task_list = [None]*len(task_list)
    all_word_filter = []
    total_words = 0
    total_filter = 0
    with ProcessPoolExecutor(max_workers=48) as executor:    # 
        future_to_item = {}
        for j, item in enumerate(task_list):
            future_to_item[executor.submit(processor, item )] = j 
        with tqdm(total=len(future_to_item), desc=descs) as pbar:
            for future in concurrent.futures.as_completed(future_to_item): 
                splited_task_list[ future_to_item[future]], word_filter, orginal_total_num = future.result()
                all_word_filter.extend(word_filter)
                total_words += orginal_total_num
                total_filter += len(word_filter)
                pbar.update(1)

    # 返回所有过滤过的词(用于词频统计)，每行的处理结果（存储本地），所有词长度，所有过滤后的词长度
    return all_word_filter, splited_task_list, total_words, total_filter

def _split_wikibio_train():
    with open( os.path.join(_DATA_PATH, f"wikibio/train.text" ), 'r') as file:
        texts = file.readlines()
    lists = [
        texts[0:len(texts)//16], 
        texts[len(texts)//16 : 2*len(texts)//16], 
        texts[2*len(texts)//16 : 3*len(texts)//16],
        texts[3*len(texts)//16 : 4*len(texts)//16],
        texts[4*len(texts)//16 : 5*len(texts)//16],
        texts[5*len(texts)//16 : 6*len(texts)//16],
        texts[6*len(texts)//16 : 7*len(texts)//16],
        texts[7*len(texts)//16 : 8*len(texts)//16],
        texts[8*len(texts)//16 : 9*len(texts)//16],
        texts[9*len(texts)//16 : 10*len(texts)//16],
        texts[10*len(texts)//16 : 11*len(texts)//16],
        texts[11*len(texts)//16 : 12*len(texts)//16],
        texts[12*len(texts)//16 : 13*len(texts)//16],
        texts[13*len(texts)//16 : 14*len(texts)//16],
        texts[14*len(texts)//16 : 15*len(texts)//16],
        texts[15*len(texts)//16 : ],
    ]
    split_path =  os.path.join(_DATA_PATH, f"wikibio/train_splited")
    if not os.path.exists(split_path):  
        # 如果目录不存在，则创建它  
        os.makedirs(split_path) 
    for i in range(16):
        with open( os.path.join(split_path, f"wikibio_train_part_{i}.txt"), 'w', encoding='utf-8') as file:
            for j in range(len(lists[i])):
                file.write(lists[i][j])
    print( "Statistics: Splitting the large wikibio into 16 parts.")

def _statistic(_dataset, _type, logger, index=None):
    if index==None:
        sub_path = os.path.join(_DATA_PATH, _dataset )
        path = os.path.join(sub_path, _type+".text" ) 
    else:
        path = os.path.join(_DATA_PATH, f"wikibio/train_splited/wikibio_train_part_{index}.text")
    texts = read_text_to_list( path )
    
    freqs = OrderedDict()
    descs = f"{_dataset}_{_type}" if index==None else f"{_dataset}_{_type}_{index}"
    all_word_filter, splited_task_list, total_words, total_filter  = multi_process(pipeline, texts, descs)
    # 在字典用加入总词数、总行数等总体统计信息
    freqs["_Overview"] = {} 
    freqs["_Overview"]["Total words"] = total_words
    freqs["_Overview"]["Lines"] = len(texts)
    freqs["_Overview"]["Average_words_Line"] = total_words/len(texts)
    freqs["_Overview"]["Total words after filter"] = total_filter  # 
    prefix = f"{_dataset}_{_type}" if index==None else f"{_dataset}_{_type}_{index}"
    
 
    # 对所有过滤后的词统计词频
    word_freq = Counter( all_word_filter ) 
    for word, freq in word_freq.most_common():
       freqs[word] = freq
    # 保存总体统计信息和词频统计
    file_name = f"{_type}_{index}" if index!=None else f"{_type}"
    with open( os.path.join(_SAVE_Path, f"{_dataset}/{file_name}_freq.json"), 'w', encoding='utf-8') as file:
        json.dump(freqs, file, ensure_ascii=False, indent=4)
    # 保存进一步处理结果
    with open( os.path.join(_SAVE_Path, f"{_dataset}/{file_name}_filter.json"), 'w', encoding='utf-8') as file:
        json.dump(splited_task_list, file, ensure_ascii=False, indent=4)
    logger.info( f"{prefix}: total words={total_words}, total lens={len(texts)}, total filtered words={total_filter}, average words={total_words/len(texts)}")

def _merge( dataset_path, logger ):
    # 合并统计一个目录下所有的_freq.json结尾的文件
    files_with_full_path = glob.glob(os.path.join(dataset_path, '*_freq.json'))      #返回所有文件的完整路径名
    all_dicts = {}
    all_dicts["_Overview"] = {
        "Total words": 0,
        "Lines": 0,
        "Average_words_Line": 0,
        "Total words after filter": 0
    }
    temp_dict = {}          # 存放临时合并的字典
    for file_path in files_with_full_path:
        with open( file_path, "r" ) as file:
            freqs = json.load(file)
        all_dicts["_Overview"]["Total words"] += freqs["_Overview"]["Total words"]
        all_dicts["_Overview"]["Lines"] += freqs["_Overview"]["Lines"]
        all_dicts["_Overview"]["Total words after filter"] += freqs["_Overview"]["Total words after filter"]

        
        for key, value in freqs.items():
            if key !="_Overview":
                if key in temp_dict:
                    temp_dict[key] += value
                else:
                    temp_dict[key] = value
    print("Sorting...")
    sorted_items = sorted(temp_dict.items(), key=lambda x: x[1], reverse=True)
    for key, value in sorted_items:  
        all_dicts[key] = value

    all_dicts["_Overview"]["Average_words_Line"] = all_dicts["_Overview"]["Total words"] / all_dicts["_Overview"]["Lines"]
    with open( os.path.join(_SAVE_Path, f"{os.path.basename(dataset_path)}/freq_all.json"), 'w', encoding='utf-8') as file:
        json.dump(all_dicts, file, ensure_ascii=False, indent=4)
    logger.info( f"{os.path.basename(dataset_path)}: total words={all_dicts['_Overview']['Total words']}, total lens={all_dicts['_Overview']['Lines']}, total filtered words={all_dicts['_Overview']['Total words after filter']}, average words={all_dicts['_Overview']['Average_words_Line']}")

def main_wikibio():
    print("当前脚本的进程号是:", os.getpid())
    logger = create_logger("Statistic", os.path.join(_IE_PATH, "statistic/en/statistic_wikibio.log"), level=1)
    _dataset = 'wikibio'
    for i in range(3):
        _type = _TYPES[i]
        if _type != 'train':
             _statistic(_dataset, _type, logger)   
        else:
            for i in range(16):   # 进程机制问题，每隔几个需要手动重启
                _statistic(_dataset, _type, logger, i)
    _merge( os.path.join(_SAVE_Path, _dataset), logger )
    
def main_other():
    logger = create_logger("Statistic", os.path.join(_IE_PATH, "statistic/en/statistic.log"), level=1)
    for _dataset in _SETS[:-1]:
        print(f"Start_{_dataset}")
        for _type in _TYPES:
            _statistic(_dataset, _type, logger)
        _merge( os.path.join(_SAVE_Path, _dataset) , logger)
    del logger
        

if __name__=="__main__":
    if not os.path.exists(_DATA_PATH):  
        # 如果目录不存在，则创建它  
        raise FileNotFoundError(f"Directory '{_DATA_PATH}' does not exist.")
    
    sta_path = os.path.join(_IE_PATH, "further_processed/statistic")
    if not os.path.exists(sta_path):  
        # 如果目录不存在，则创建它  
        os.makedirs(sta_path) 
    if not os.path.exists(os.path.join(sta_path, "e2e")):  
        # 如果目录不存在，则创建它  
        os.makedirs(os.path.join(sta_path, "e2e"))
    if not os.path.exists(os.path.join(sta_path, "rotowire")):  
        # 如果目录不存在，则创建它  
        os.makedirs(os.path.join(sta_path, "rotowire"))
    if not os.path.exists(os.path.join(sta_path, "wikibio")):  
        # 如果目录不存在，则创建它  
        os.makedirs(os.path.join(sta_path, "wikibio"))
    if not os.path.exists(os.path.join(sta_path, "wikitabletext")):  
        # 如果目录不存在，则创建它  
        os.makedirs(os.path.join(sta_path, "wikitabletext"))

    #main_other()
    _split_wikibio_train()
    main_wikibio()