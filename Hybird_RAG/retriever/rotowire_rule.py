import os
import sys
import re
from collections import OrderedDict

_ROOT_PATH = os.path.abspath(__file__)
for _ in range(4):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert(0, _ROOT_PATH)

from KGs.dataset_KGs.rotowire import total_team_city_map
from utils import load_data

def keyword_context( text:str, keyword:str, left_edge: int, right_edge: int):
    """
    text: 输入的文本
    keyword：核心关键词
    left_edge, right_edge：关键词周边的上下文窗口
    """
    left_word_list, right_word_list = text.split( keyword )[0].split(" "), text.split( keyword )[1].split(" ")
    left_context = " ".join(left_word_list[ - min(left_edge, len(left_word_list)):]) if left_edge!=0 else ""
    right_context = " ".join(right_word_list[ : min(right_edge, len(right_word_list))]) if right_edge!=0 else ""
    return left_context + " " + right_context

# 比较标签和预测列表，返回不相等的index列表
def match_number( predict_lists, label_lists):
    ret_not = []
    for i in range( len( predict_lists) ):
        if predict_lists[i] != label_lists[i]:
            ret_not.append( i )
    return ret_not

# 从Team label中拆分12个标签的独立情况
def rotowire_team_split( label_lists ):
    # 12个属性
    names = []
    Losses, Wins, Turnovers, Rebounds, Percentage_of_3_points, Percentage_of_field_goals, team_assists = [], [], [], [], [], [], []
    Total_points,  Points_1st_quarter, Points_2st_quarter, Points_3st_quarter, Points_4st_quarter =  [], [], [], [], []

    list_list = [ Losses, Wins, Turnovers, Rebounds, Percentage_of_3_points, Percentage_of_field_goals, team_assists,
                 Total_points,  Points_1st_quarter, Points_2st_quarter, Points_3st_quarter, Points_4st_quarter ]
    field_name_list = [
        "Losses", "Wins", "Turnovers", "Rebounds", "Percentage of 3 points", "Percentage of field goals", "Number of team assists", 
        "Total points", "Points in 1st quarter", "Points in 2nd quarter", "Points in 3rd quarter", "Points in 4th quarter"
    ]
    # 合并情况
    Losses_Wins = [ set() for _ in range(len(label_lists)) ]
    names = [ [] for _ in range(len(label_lists)) ]
    # 遍历每个样本
    for i in range( len(label_lists)):
        sets_ = label_lists[i]
        for item in sets_:
            if item[0] not in names[i]:
                names[i].append( item[0] )
            for name_, name_list in zip( field_name_list, list_list ):
                if item[1] == name_:
                    name_list[i].append( item )
        
        Losses_Wins[i].update(Losses[i])
        Losses_Wins[i].update(Wins[i])

    return names, Losses_Wins, Turnovers, Rebounds, Percentage_of_3_points, Percentage_of_field_goals, team_assists, Total_points,  Points_1st_quarter, Points_2st_quarter, Points_3st_quarter, Points_4st_quarter


def check_context( Names_list, context, score):
    ret = set()
    for _name in Names_list:
        temp_name = 'Blazers' if _name == 'TrailBlazers' else _name
        temp_name = temp_name.lower()
        # 球队名称在
        if " "+temp_name.lower() in context:
            """
            splits_ = score.replace("(", "").replace(")", "").split("-")
            win_, loss_ = splits_[0], splits_[1]
            """
            if "-" in score:
                splits_ = score.replace("(", "").replace(")", "").split("-")
                win_, loss_ = splits_[0].strip(), splits_[1].strip()
            else:
                win_, loss_ = score.replace("(", "").replace("0)", ""), "0"
            if win_ != "0":
                ret.add( (_name, "Wins", win_))
            if loss_ != "0":
                ret.add( (_name, "Losses", loss_))
    # 检查球队所在城市名称是否在
    for _name in total_team_city_map.keys():
        # 如果在
        if _name.lower() in context and total_team_city_map[_name] in Names_list:
            """
            splits_ = score.replace("(", "").replace(")", "").split("-")
            win_, loss_ = splits_[0], splits_[1]
            """
            if "-" in score:
                splits_ = score.replace("(", "").replace(")", "").split("-")
                win_, loss_ = splits_[0].strip(), splits_[1].strip()
            else:
                win_, loss_ = score.replace("(", "").replace("0)", ""), 0
            if win_ != "0":
                ret.add( (total_team_city_map[_name], "Wins", win_))
            if loss_ not in [0, "0"]:
                ret.add( (total_team_city_map[_name], "Losses", loss_))
    return ret

def find_rotowire_team_win_and_loss( index, text, Names_list ):
    ret = set()
    text = text.lower()

    # (1)检查(xx)形式
    pattern = r'\(\d+-\d+\)'
    matches = re.findall(pattern, text)
    pattern_2 = r'\(\d{1,2}0\)'
    matches_2 = re.findall(pattern_2, text)
    matches.extend(matches_2)
    for i in range(len(matches)):
        score = matches[i]      # 得分字符串
        if i==1 and matches[0] == matches[1]:
            text = text.split( score )[1] + score + text.split( score )[2]
        context = keyword_context( text, score, left_edge=3, right_edge=1)
        ret.update( check_context( Names_list, context, score) )
    """
    # (2)检查特殊a xx lead语法
    pattern = r'a \d{1,3} lead'
    matches = re.findall(pattern, text)
    pattern_2 = r'a \d{1,2}-\d{1,2} lead'
    matches_2 = re.findall(pattern_2, text)
    matches.extend(matches_2)
    for i in range(len(matches)):
        score = matches[i]      # 得分字符串
        if i==1 and matches[0] == matches[1]:
            text = text.split( score )[1] + score + text.split( score )[2]
        context = keyword_context( text, score, left_edge=7, right_edge=1)
        ret.update( check_context( Names_list, context, score) )
    """

# 比较与修正
def remedy_team( index, label, predict):
    print("修正如下")
    marked_predict = set()
    for item in label:
        if item not in predict:
            # 如果标签中哪一组不出现在预测中
            team_name = item[0]
            attr = item[1]
            old_value = item[2]
            # 先预置为0，如果预测中有一样的队名和属性则采用预测的新值，否则保持为0
            new_value = 0
            for pre_item in predict:
                if pre_item[0] == team_name and pre_item[1]==attr:
                    marked_predict.add( pre_item )      # 仅仅标记不同值得
                    new_value = pre_item[2]
            print_text = f"{index}, {item[0]}, {item[1]}, {old_value}, {new_value}"
            print(print_text)      # 整理后序号，队名，属性，原值，修改后的值
        else:
            # 如果一致，也标记
            marked_predict.add( item )
    for item in predict:
        if item not in marked_predict:
            print_text = f"{index}, {item[0]}, {item[1]}, {0}, {item[2]}"
            print(print_text)
            


def show_content(  index,text, label, predict=None):
    print( "原文：")
    list_ =  text.split(". ")
    for i in range(len(list_)):
        print( list_[i] )
    print( "标签：")
    for item in label:
        print( item )
    if predict!=None:
        print( "预测：")
        for item in predict:
            print( item )
        remedy_team( index, label, predict)
    """
    error_index_iterator = (value for index, value in enumerate(ret_not) if index >=27 )    # 27--258
    show_content(  index, texts[index], Losses_Wins[index], ret_list[index])
    """

    def run_():
        pair = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/evaluation/eval_results/rotowire_data_cell_Team_eval_pair_list.pickle", "pickle")
        prompt_lists = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/temp/rotowire/rotowire_data_cell_Team_prompt_list.pickle", "pickle")
        texts = load_data( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/data/rotowire/test.text", "text")
        label_lists, predict_lists = pair[0], pair[1]   # 1456个测试样本，每个样本的prompt为0或12或24
        Names, Losses_Wins, Turnovers, Rebounds, Percentage_of_3_points, Percentage_of_field_goals, team_assists, Total_points,  Points_1st_quarter, Points_2st_quarter, Points_3st_quarter, Points_4st_quarter = rotowire_team_split( label_lists )

        ret_list = []
        for index in range( len(texts) ):
            sets_ = find_rotowire_team_win_and_loss( index, texts[index], Names[index] )
            ret_list.append( sets_ )
        ret_not = match_number( ret_list, Losses_Wins)
        len(ret_not)
    