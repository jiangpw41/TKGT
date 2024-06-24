import os
import re
import sys

sys.path.insert(0, os.path.dirname( os.path.abspath(__file__) ))

from functions import read_text_to_list

_ROOT_PATH = os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) )          #_ROOT_PATH = os.path.dirname( os.path.dirname( os.getcwd() ) ) 

_FIELDS = ["法律领域", "民间借贷案件领域"]                           # 设置领域描述，从左到右层级递减、范畴缩小，n个领域层级，
_FIELDS_TYPE = "Event-Oriented"                                # "Event-Oriented"和"Ontology-Oriented" 二选一选择领域类型：面向事件 or 面向本体(人或群体、组织)

_SEED = {                                                      # 专家种子知识，领域文本通用框架，空缺处填充为基于基本父类的class子类
    "Top_Event_Concept" : "民间借贷案件",                        # 事件模型顶层事件类型（唯一性），如民间借贷案件
    "Test_Description" : "法院判决文书",                             # 文本集描述
    "Sub_Event" : {
        "Scalable": True,                                      # 是否需要在实例学习中自动扩展
        "dict":{
            "借款": None, 
            "还款": None, 
            "担保": None
        }
    },                                                          # 子事件类（角色之间的动作、行为等，动态），都有多次可能
    "Role": {
        "Scalable": False,
        "dict":{
            "法院":None,
            "出借人（原告）": None, 
            "借款人（被告）": None, 
            "担保人（被告）": None,
            #"法官": None, 
            #"辩护律师": None, 
            #"法人代表": None, 
            #"律师事务所": None
        }
    },                                                      # 事件中独立角色类型，具有自然、法律人格，如自然人、组织（继承自基类）。因为是社科领域，所以默认角色具有人格
    "Thing": {
        "Scalable": True,
        "dict":{
            "证据": None,
            "本金": None,
            #"利息": None,
            #"违约金":None,
        }
        
    },                                                       # 事件中出现的无人格对象，
    "Relation" : {
        "Scalable": True,
        "list":[ ("出借人", "诉讼关系" ,"借款人"), ("借款人", "担保关系" ,"担保人"), ("出借人", "诉讼关系" ,"担保人"),
                  ("法院", "裁判第三方" ,"出借人"), ("法院", "裁判第三方" ,"担保人"),  ("法院", "裁判第三方" ,"借款人") ]
    },                                                        # 在Role和Thing的所有要素之间的静态关系，连线，三元组（subject, relation, object）
}


stop_pos_en = ["CC", "DT", "EX", "IN", "MD", "PDT", "POS", "PRP", "RP", "SYM", "TO", "UH", "WDT" , "WP"]
Supplementary_stop_words_en = ["the", "it", ".", ",", " ", "-", "(", ")", "``", "''", "--", ";", ":", "`", "'", "$", "..", "#", "!", "?", "...", "-lsb-"]
_POS_FILTER_zh = ["NR", "NN", "CD", "VV", "NT", "FW", "AD", "JJ" ]

_PRONON = [ '你', '我', '他', '她', '它', '你们', '我们', '他们', '她们', '它们' ]
_VIRTUAL = ['的', '了', '在', '是',  '啊', '呀', '哦', '吧', '呢', '吗', '之', '于', '并', '起']
_PUNCATUATION_EN = [',', '.', ';', '?', '!', '…', ":", '"', '"', "'", "'", "(", ")", ]
_PUNCATUATION_ZH = ['，', '。', '；', '？', '！', '......', "：",  '“', '”', '‘', '’', '（', '）', '《', '》', '【', '】', '[', ']', '、', "\\n"]

_STOPWORDS = read_text_to_list( os.path.join( _ROOT_PATH, "Mixed_IE/statistic/zh/stopwords.txt" ) )