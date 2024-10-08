"""
本文件负责
（1）将分开预测的结果合并
（2）清理预测结果中的bad outputs（用外挂函数解决）
（3）组成(label, predict)列表对保存到3evaluation中
"""
import pickle
import argparse
import os
import sys

_ROOT_PATH = os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )
#_ROOT_PATH = "/home/jiangpeiwen2/jiangpeiwen2/workspace/TKGT"
sys.path.insert(0, _ROOT_PATH )

def _split( _set ):
    ret_set = set()
    for item in _set:
        if '目标角色' in item:
            item = item.replace( '目标角色' , "")
        
        item = item.strip()
        item = item.replace("\n", "")
        item = item.replace(" ", "")
        if "、" in item:
            temp_item = item.split("、")
        elif "，" in item:
            temp_item = item.split("，")
        elif "-" in item:
            temp_item = item.split("-")
        elif "：" in item:
            temp_item = item.split("：")[1]
        elif "（" in item:
            temp_item = item.split("（")[0]
        elif "(" in item:
            temp_item = item.split("(")[0]
        else:
            temp_item = item
        if isinstance(temp_item, list):
            for sub_item in temp_item:
                if sub_item.strip()!="":
                    ret_set.add(sub_item.strip())
        else:
            if temp_item.strip()!="":
                if temp_item.strip().endswith("有限"):
                    temp_item = temp_item.strip()+"公司"
                ret_set.add(temp_item.strip())
    return ret_set

def post_process_cpl( index, _predict, _label, court_name_rule ):
    # (1)分割与strip 
    ret_label, ret_predict = _split(_label), _split(_predict)
    # (2)如果court_name_rule为真，说明court_name是通过规则获取的百分百准确
    if court_name_rule:
        flag = 0
        for item in ret_label:
            if "法院" in item:
                ret_predict.add(item)
                flag=1
                break
        if flag==0:
            print(f"Court Name Error {index}")
    return ret_label, ret_predict