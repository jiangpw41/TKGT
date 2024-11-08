'''
对目标文档进行词频统计，根据特定的规则对词重要性进行排序、分类。注重完备性，发掘潜质
'''
import sys
import os
import json
from tqdm import tqdm
from typing import List
import re
from concurrent.futures import ProcessPoolExecutor
import math

import hanlp
from collections import Counter, OrderedDict
import torch.multiprocessing as mp


_ROOT_PATH = os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ))))
sys.path.insert(0, _ROOT_PATH)
from utils import create_logger

from Mixed_IE.config import _ROOT_PATH, _POS_FILTER_zh, _STOPWORDS
from Mixed_IE.functions import read_text_to_list
from Mixed_IE.regulation.regulation_lib import regulations

logger = create_logger( "preprocess_log", os.path.join(_ROOT_PATH, "Mixed_IE/mixed_ie.log"))

class Statistic_Methods():
    def __init__(self, texts):
        pass
    # 统计一个单词在一篇文档中出现的次数
    @classmethod
    def count_words(cls, word, document):
        return document.count(word)
    # 有某个单词的文档比例
    @classmethod
    def count_documents(cls, word, documents):
        count=0
        for document in documents:
            if word in document:
                count += 1
        return count/len(documents)

    @classmethod
    def merge_ordered_dict(cls, dict_all_path, merged_key):
        pattern_year = regulations['Element'][1]
        pattern_mon = regulations['Element'][2]
        sorted_dict = {}
        with open( dict_all_path, "r") as file:
            total_dict = json.load(file)
        for par_key in total_dict.keys():
            if par_key in merged_key:
                for key in total_dict[par_key].keys():
                    temp_word = key
                    if len(temp_word)>1 and temp_word not in ["n", "\n", "XXX", "\\n", "n"] and pattern_year.search(temp_word)==None and pattern_mon.search(temp_word)==None:      #根据预先观察结果过滤一些高频但无意义的词
                        if key in sorted_dict:
                            sorted_dict[key] += total_dict[par_key][key]
                        else:
                            sorted_dict[key] = total_dict[par_key][key]
        sorted_items = sorted(sorted_dict.items(), key=lambda x: x[1], reverse=True)
        temp = OrderedDict()
        for key, value in sorted_items:  
            temp[key] = value
        total_dict["TT_freq"] = temp
        with open( dict_all_path, 'w', encoding='utf-8') as file:
            json.dump(total_dict, file, ensure_ascii=False, indent=4)

    @classmethod
    def count_tokens_and_filter(cls):
        _target_path = os.path.join( _ROOT_PATH, "Mixed_IE/further_processed/statistic/CPL" )
        part_list = ["Core", "Procedure", "Appendix"]
        total_tokens = 0
        for part in part_list:
            merge_path = os.path.join(_target_path, part )
            json_files = []  
            for filename in os.listdir(merge_path):  
                if filename.endswith('.json'):  
                    # 使用正则表达式检查文件名是否以数字开头  
                    if re.match(r'^\d+\.', filename):  
                        json_files.append(os.path.join(merge_path, filename)) 
            for _path in json_files:
                with open( _path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                tokens_list = data["tok"]
                for ttt in tokens_list:
                    total_tokens += len(ttt)
        with open( os.path.join(_target_path, "freq_all.json" ), 'r', encoding='utf-8') as file:
            data2 = json.load(file)

        total_tokens_filter = 0
        totals = data2["TT_freq"]
        for key in totals:
            total_tokens_filter += totals[key]
        logger.info(f"Statistics CPL: Total words {total_tokens}, filter {total_tokens_filter}")

class _HANLP_CUSTOM():
    def __init__(self, _STOPWORDS, dict_combine=None, dict_force=None):

        # hanlp
        self.sent_spliter = hanlp.utils.rules.split_sentence
        #self.tokenizer = hanlp.load('COARSE_ELECTRA_SMALL_ZH')   # 统计模型，粗分
        self.tokenizer = hanlp.load('FINE_ELECTRA_SMALL_ZH') 
        # HanLP支持合并和强制两种优先级的自定义词典，以满足不同场景的需求。
        self.tokenizer.dict_combine = dict_combine    # 合并模式的优先级低于统计模型，即dict_combine会在统计模型的分词结果上执行最长匹配并合并匹配到的词条，含有空格、制表符等（Transformer tokenizer去掉的字符）的词语需要用tuple的形式提供：
        self.tokenizer.dict_force = dict_force        # 优先输出正向最长匹配到的自定义词条,自定义词语越长，越不容易发生歧义。

        self.POS_tagger = hanlp.load('CTB9_POS_ELECTRA_SMALL')   # HanLP支持多种词性标注体系，包括但不限于 CTB、PKU、863 等。每种体系都有自己的词性标签集
        self.NER_c = hanlp.load('MSRA_NER_ELECTRA_SMALL_ZH')
        self.DEP_c = hanlp.load('CTB9_DEP_ELECTRA_SMALL', conll=0)

        self.HanLP = hanlp.pipeline() \
            .append( self.sent_spliter, output_key='sentences') \
            .append( self.tokenizer, output_key='tok', ) \
            .append( self.POS_tagger, output_key='pos') \
            .append( self.NER_c, output_key='ner', input_key='tok') \
            #.append( self.DEP_c, output_key='dep', input_key='tok')\

        # custom
        self.stopwords = _STOPWORDS
        self.save_path = os.path.join( _ROOT_PATH, "Mixed_IE/further_processed/statistic/CPL")

    def filter( self, tokens: List[ List[str] ], pos: List[ List[str] ]):
        # 过滤停用词，并抽取特定词性
        ret = { key:[] for key in _POS_FILTER_zh}
        for i in range( len(tokens) ):
            for j in range( len(tokens[i]) ):
                if tokens[i][j] not in _STOPWORDS and pos[i][j] in ret:
                    ret[pos[i][j]].append( tokens[i][j] )
                    
        return ret

    # 完整性工程：分词、分句、词性标注、命名实体识别
    def Completeness(self, texts: List[List[str]], part):
        sub_path = os.path.join( self.save_path, part)
        if not os.path.exists(sub_path):  
            # 如果目录不存在，则创建它  
            os.makedirs(sub_path)
            logger.info( f"Statistics CPL: have created path for {part}.")
        ret = OrderedDict()
        for key in _POS_FILTER_zh:
            if key not in ["CD", "NT", "FW"]:              #在全集层面统计基数词、时间名词、外来词（英文符号等）没有意义 
                ret[key] = OrderedDict()    #  按照词性存放词频统计信息
        all_words = { key:[] for key in _POS_FILTER_zh}        # 用于分词性统计词频
        all_words_no_pos = []

        for i in tqdm(range( len(texts) ), desc=f"Statistic {part}"):
            result = self.HanLP( "\\n".join(texts[i]) )
            keys_set = result.keys()
            sent = result[ 'sentences' ]   # 分句列表，一维
            tok = result[ 'tok' ]          # 分词列表，二维
            pos = result[ 'pos' ]          # 词性标注，二维
            ner = result[ 'ner' ]          # 命名实体识别
            #dep = result[ 'dep' ]          # 依存句法分析
            result[ 'filtered_tok' ] = self.filter( tok, pos)

            with open( os.path.join( sub_path, f'{i}.json'), 'w', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False, indent=4)                          # 为每份文档存一份

            for key in ret:
                all_words[key].extend( result[ 'filtered_tok' ][key] ) 
                all_words_no_pos.extend( result[ 'filtered_tok' ][key] ) 
        
        # 计算词频
        word_freq = { key:Counter(all_words[key])  for key in ret}
        word_freq_no_pos = Counter(all_words_no_pos)
        ret["No_pos_tag"] = OrderedDict()
        for word, freq in word_freq_no_pos.most_common():
            #if freq>1:
            ret["No_pos_tag"][word] = freq
        # 打印词频（可以按频率排序）  
        for key in ret:
            if key!="No_pos_tag":
                for word, freq in word_freq[key].most_common():
                    #if freq>1:
                    ret[key][word] = freq
        with open( os.path.join( sub_path, 'WordFreq.json'), 'w', encoding='utf-8') as file:
            json.dump(ret, file, ensure_ascii=False, indent=4)
        return ret
    
    def main(self):
        # 使用regulation步骤处理完毕的数据
        with open( os.path.join( _ROOT_PATH, "Mixed_IE/further_processed/regulation/para_splited_B.json"), 'r', encoding='utf-8') as file:
            data = json.load(file)
        # （1）程序性信息列表
        procedure = []
        for i in range( len(data) ):
            temp = []
            temp.extend( data[ str(i) ][ "开头" ] )
            temp.extend( data[ str(i) ][ "正文" ]["程序信息"] )
            temp.extend( data[ str(i) ][ "正文" ]["末尾信息"] )
            #temp.extend( data[ str(i) ][ "正文" ]["附录"] )
            procedure.append( temp )
        self.Completeness( procedure, "Procedure")
        # （2）核心申辩证信息列表
        core = []
        for i in range( len(data) ):
            core.append( data[ str(i) ][ "正文" ]["申辩证"] )
        self.Completeness( core, "Core")
        # （3）附录信息列表
        appendix = []
        for i in range( len(data) ):
            appendix.append( data[ str(i) ]["附录"] )
        self.Completeness( appendix, "Appendix")

        # 合并统计
        sorted_dict = {}
        with open( os.path.join( self.save_path, "Core/WordFreq.json"), "r") as file:
            total_dict = json.load(file)
        with open( os.path.join( self.save_path, "Procedure/WordFreq.json"), "r") as file:
            pre_dict = json.load(file)
        for par_key in pre_dict.keys():
            for key in pre_dict[par_key].keys():
                if key in total_dict[par_key]:
                    total_dict[par_key][key] += pre_dict[par_key][key]
                else:
                    total_dict[par_key][key] = pre_dict[par_key][key]
            sorted_items = sorted(total_dict[par_key].items(), key=lambda x: x[1], reverse=True)
            temp = OrderedDict()
            for key, value in sorted_items:  
                temp[key] = value
            sorted_dict[par_key] = temp

        # 增加文档频率
        texts = read_text_to_list( os.path.join(_ROOT_PATH, "data/CPL/text"))
        Doc_Fre = OrderedDict()
        temp = []
        for key in sorted_dict["No_pos_tag"].keys():
            temp.append( (key,  Statistic_Methods.count_documents(key, texts) ) )
        sorted_items = sorted(temp, key=lambda x: x[1], reverse=True)
        for key, value in sorted_items: 
            Doc_Fre[key] = value
        sorted_dict["Doc_Fre"] = Doc_Fre
        with open( os.path.join( self.save_path, 'freq_all.json'), 'w', encoding='utf-8') as file:
            json.dump(sorted_dict, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    current_start_method = mp.get_start_method(allow_none=True)
    if current_start_method != 'spawn':
        mp.set_start_method('spawn', force=True)

    sta_path = os.path.join( _ROOT_PATH, "Mixed_IE/further_processed/statistic/CPL" )
    if not os.path.exists(os.path.join(sta_path, "CPL")):  
        # 如果目录不存在，则创建它  
        os.makedirs(os.path.join(sta_path, "CPL"))
        logger.info( "Statistics: have created path for CPL.")
    
    processor = _HANLP_CUSTOM( _STOPWORDS )
    processor.main()
    logger.info( f"Statistics CPL: each position tag completed.")
    dict_all_path = os.path.join( _ROOT_PATH, "Mixed_IE/further_processed/statistic/CPL/freq_all.json" )
    merged_key = ["NR", "NN", "VV", "AD", "JJ", "No_pos_tag"]  # 除去数量词和时间名词
    Statistic_Methods.merge_ordered_dict( dict_all_path, merged_key)
    logger.info( f"Statistics CPL: merging all position tag.")
    Statistic_Methods.count_tokens_and_filter()
    