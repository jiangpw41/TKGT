import os
import sys
import re
from collections import OrderedDict

_ROOT_PATH = os.path.abspath(__file__)
for _ in range(4):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert(0, _ROOT_PATH)

from utils import load_data, online_local_chat, save_data

# Split E2E labels
def split_e2e_label( datas ):
    area_label, cust_label, family_label, food_label, name_label, near_label, price_label = [], [], [], [], [], [], []
    for i in range(len(datas)):
        dict = {}
        for item in datas[i]:
            dict[item[0]] = item[1]
        area_label.append( dict['area'] if 'area' in dict else None )
        cust_label.append( dict['customer rating'] if 'customer rating' in dict else None )
        family_label.append( dict['family friendly'] if 'family friendly' in dict else None )
        food_label.append( dict['food'] if 'food' in dict else None )
        name_label.append( dict['name'] if 'name' in dict else None )
        near_label.append( dict['near'] if 'near' in dict else None )
        price_label.append( dict['price range'] if 'price range' in dict else None )
    return area_label, cust_label, family_label, food_label, name_label, near_label, price_label

def keyword_context( text:str, keyword:str, left_edge: int, right_edge: int):
    left_word_list, right_word_list = text.split( keyword )[0].split(" "), text.split( keyword )[1].split(" ")
    left_context = " ".join(left_word_list[ - min(left_edge, len(left_word_list)):]) if left_edge!=0 else ""
    right_context = " ".join(right_word_list[ : min(right_edge, len(right_word_list))]) if right_edge!=0 else ""
    return left_context + " " + right_context


def get_friend_e2e( texts, left_edge=6, right_edge=3):
    # 错误率从1183降低到 228/15428
    predicts_rule = []
    for i in range(len(texts)):
        text = texts[i].lower()
        key_words = [ "famil", "friend", "kid", "child"]
        # 明确的否定信息
        if "unfriend" in text or "adult" in text or "friendly no" in text:
            predicts_rule.append( "no" )
            continue
        # 不明确，进一步
        flag = 0
        sub_flag = 0
        for key in key_words:
            if key in text:
                # 如果有关键词，说明有答案
                flag = 1
                context = keyword_context( text, key, left_edge, right_edge)
                ban_word = [ "non", "not", "n't", "no ", "prohibited", "home"]
                for bans in ban_word:
                    if bans in context:
                        sub_flag = 1
                        break
                # 如果sub_flag变了，说明匹配到否定词
                if sub_flag == 1:
                    predicts_rule.append( "no" )
                    break
        if flag == 1 and sub_flag == 0:
            predicts_rule.append( "yes" )
        # 如果没有关键词，说明没这个信息
        if flag == 0:
            predicts_rule.append( None )
    return predicts_rule

def get_area_e2e( texts ):
    """
    texts为原始文本
    错误率为从4271降低到426/15428，剩下的绝大多数为数据集本身的错误，即明明文中表示在center，但标签没有，或者标签为riverside
    """
    predicts_rule = []
    for i in range(len(texts)):
        text = texts[i].lower()
        if "river" in text:
            predicts_rule.append( "riverside")
        elif ("centr" in text or "cente" in text) and ("city" in text or "town" in text):
            # 需要加一个否定逻辑
            flag = 0
            pre_winds = text.split("cent")[0][-15:]
            pre_winds_lang = text.split("cent")[0][-30:]
            ban_word = [ "of", "not"]
            
            for bans in ban_word:
                if bans in pre_winds or "not" in pre_winds_lang:
                    flag = 1
                    break
            if "outside" in text:
                flag = 1
            elif "heart" in text:
                flag = 0

            if flag==0:
                predicts_rule.append( "city centre")
            else:
                predicts_rule.append( None )
        else:
            predicts_rule.append( None )
    return predicts_rule


def get_price_e2e( texts ):
    """
    texts为原始文本
    错误率为从6072降低到1261/15428，
    [])
    """
    dict_map = {
        "cheap" :{
            "range": ['cheap', "low pri", "less", "£20 ", "low co", "lower", "inexpensive", "discount"],
            "not" : [],
            "label": 'cheap',
        },
        "moderate":{
            "range": ['mode', "mid-", "medium", "mid ", "25", "for average", "affordable", "average pr", "fair prices", "average-pr"],
            "not" : ["moderate rating"],
            "label": 'moderate',
        },
        "high":{
            "range": ['is high', 'high pr', 'highly pr', "high-pri", "pricey", "expensive", "over av", "higher", "above average", "more", "30"],
            "not" : [],
            "label": 'high',
        }
    }
    predicts_rule = []
    for i in range(len(texts)):
        text = texts[i].lower()
        text = text.replace("highly rate", "")
        
        father_flag = 0
        for key in dict_map.keys():
            key_range = dict_map[key]["range"]
            label = dict_map[key]["label"]
            not_a = dict_map[key]["not"]
            flag = 0
            not_b = 0
            for maybe in not_a:
                if maybe in text:
                    not_b = 1
                    break
            if not_b==0:
                for maybe in key_range:
                    if maybe in text:
                        flag = 1
                        predicts_rule.append( label )
                        break
            if flag == 1:
                father_flag = 1
                break
        if father_flag == 0:
            predicts_rule.append( None )
    return predicts_rule


def get_rating_e2e( texts ):
    """
    texts为原始文本
    错误率为从2006降低到1051/15428，
    [])
    """
    dict_map = {
        "cheap" :{
            "range": {
                "striking":[],
                "not great":[],
                "low customer rating":[],
                "poor": [],
                "1 ": [ "1 star or"],
                ' low': ["low pr", "lower pr", "low-co", "low co", "low quality fo", "low-pri"],
                "one star": [ "one star p"],
                "below average":[]
            },
            "label": 'low',
        },
        "moderate":{
            "range": {
                "of 3":[],
                "3 ": [ "3 star menu"], 
                "3-5":[],
                
                " ok ":[],
                "mid rate": [],
                "reasonable cu":[],
                'average' : [ "average pr", "above average", "below average", "averagely pr", "average-pr", "average bill", "average cost", "20 average"], 
            },
            "label": 'average',
        },
        "high":{
            "range": {
                "excellent":[],
                "high customer ra": [],
                "high":[ "high p", "highly pr", "highly ex", "high q", "high-p", "high cos", "higher p", "price range is high", "high end"],
                " 5": [ "1 out of 5", "3 out of 5", ] ,
                "favourably":[],
                "five": [ "five star dinin", "five star cof"],
                "good cus":[]
            },
            "label": 'high',
        }
    }
    predicts_rule = []
    for i in range(len(texts)):
        text = texts[i].lower()
        father_flag = 0
        # 遍历三种种取值
        for key in dict_map.keys():
            key_range = dict_map[key]["range"]
            label = dict_map[key]["label"]
            flag = 0
            for sub_key in key_range.keys():
                if sub_key in text:
                    not_flag = 0
                    for not_a in key_range[ sub_key ]:
                        if not_a in text:
                            not_flag = 1
                            break
                    if not_flag ==0:
                        flag = 1
                        predicts_rule.append( label )
                        break
            if flag==1:
                father_flag = 1
                break
        if father_flag == 0:
            predicts_rule.append( None )
    return predicts_rule


def keyword_context_near( text:str, keyword:str, right_edge: int):
    right_word_list = text.split( keyword )[1].strip().split(" ")
    right_context = " ".join(right_word_list[ : min(right_edge, len(right_word_list))]) if right_edge!=0 else ""
    return right_context


def get_near_e2e( texts, near_label_predict):
    """
    2009到1499
    """

    map_dict = {
        "express by": [],
        "near to": ["outskirts"],
        "near" : ["city", "river"],
        "next to": ["city", "river"],
        "joint by ": ["city", "river"],
        "close to":[ "city", "river"],
    }
    predicts_rule = []
    for i in range(len(texts)):
        text = texts[i].lower()
        # 仅对空的进行
        if near_label_predict[i]==None:
            flag = 0
            for key in map_dict.keys():
                if key in text:
                    context = keyword_context_near( text, key, 2)
                    sub_flag = 0
                    for not_a in map_dict[key]:
                        if not_a in context:
                            sub_flag = 1
                            break
                    if sub_flag == 1:
                        break
                    flag = 1
                    if key == "express by":
                        context = "express by" + " " + context
                    
                    predicts_rule.append( context )
                    break
            if flag == 0:
                predicts_rule.append( None )
        else:
            predicts_rule.append( near_label_predict[i] )
    return predicts_rule

def compare( labels, _predicts):
    not_same = []
    for i in range( len(labels) ):
        if labels[i] != _predicts[i]:
            not_same.append(i)
    return not_same

def re_process_e2e_pari(text_path, pair_path):
    
    texts = load_data( text_path, "text")
    pair = load_data( pair_path, "pickle")
    labels, predicts = pair[0], pair[1]
    # 7个标签的单独情况
    area_label_label, cust_label_label, family_label_label, food_label_label, name_label_label, near_label_label, price_label_label = split_e2e_label( labels )
    # 7个预测的单独情况: food 154, name 264, near 2009, price 6072-1200,  rating 2006   || friend 228, area 426
    area_label_predict, cust_label_predict, family_label_predict, food_label_predict, name_label_predict, near_label_predict, price_label_predict = split_e2e_label( predicts )
    # 获得每个字段对应的规则结果并转变为集合形式
    insert_area_list = get_area_e2e( texts )
    insert_friend_list = get_friend_e2e( texts )
    insert_price_list = get_price_e2e(texts)
    insert_rating_list = get_rating_e2e(texts)
    insert_near_list = get_near_e2e( texts, near_label_predict)
    def get_insert_sets( insert_lists, names ):
        ret_list = []
        for i in range( len(insert_lists[0]) ):
            new_set = set()
            for j in range( len(insert_lists)):
                if insert_lists[j][i] != None:
                    new_set.add( (names[j], insert_lists[j][i]))
            ret_list.append( new_set )
        return ret_list

    insert_set_list = get_insert_sets( [insert_area_list, insert_friend_list, insert_price_list, insert_rating_list, insert_near_list], ["area", "family friendly", "price range", "customer rating", "near"] )

    # 将规则结果替换掉原来的预测结果并保存
    def replace( texts, insert_predicts):
        replace_attr = ["area", "family friendly", "price range", "customer rating", "near"]
        new_predict_list = []
        for i in range( len(texts)):
            insert_predict_set = insert_predicts[i]
            predict_set = predicts[i]
            temp_set = set()
            for item in predict_set:
                if item[0] not in replace_attr:
                    temp_set.add( item )
            for item in insert_predict_set:
                temp_set.add( item )
            new_predict_list.append( temp_set )
        return new_predict_list
    new_predict_list = replace( texts, insert_set_list)
    pair_path_ = pair_path[:-7]+"_rule" + ".pickle"
    save_data( (labels, new_predict_list), pair_path_)
    # area_result = compare( cust_label_label, insert_rating_list )   # 5181 - 1051
    #area_result = compare( area_label_label, insert_area_list )   # 2756 - 426
    #area_result = compare( family_label_label, insert_friend_list )   # 1031 - 228
    #area_result = compare( price_label_label, insert_price_list )   # 7691 - 1261
    #area_result = compare( food_label_label, food_label_predict )   # 154
    #area_result = compare( name_label_label, name_label_predict )   # 264
    #area_result = compare( near_label_label, insert_near_list )   # 1472
    #len(area_result)
    """
    aaa = []    # 14175, 314
    for i in range( len(texts)):
        if new_predict_list[i] != labels[i]:
            aaa.append( )
    len(aaa)
    def show_by_index( index, predicts_rule, _label, texts):
        print(f"原文：{texts[index]}
    标签：{_label[index]}
    预测：{predicts_rule[index]}")

    show_by_index( 20, near_new, near_label_label, texts)
    """

if __name__=="__main__":
    text_path = "/home/jiangpeiwen2/jiangpeiwen2/TKGT/data/e2e/test.text"
    pair_path = "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/evaluation/eval_results/e2e_all_all_eval_pair_list_100000.pickle"
    re_process_e2e_pari(text_path, pair_path)