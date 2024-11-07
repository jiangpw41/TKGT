
from tqdm import tqdm
import sys
import os

_ROOT_PATH = os.path.abspath(__file__)
for i in range(3):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert(0, _ROOT_PATH)
from utils import load_data
from KGs.dataset_KGs.cpl import Plaintiff_claim_attributes, cpl_keyword

class DataLoader( ):
    """读取整个数据集"""
    def __init__(self, dataset_name, file_name, part):
        self.data_path = os.path.join( _ROOT_PATH, f"data/{dataset_name}/{part}.{file_name}")
        if not os.path.exists( self.data_path ):
            raise Exception( f"文本路径不存在{self.data_path}")
        self.texts = load_data( self.data_path, "json")

class CplDataLoader( DataLoader ):
    def __init__(self, dataset_name, file_name, part):
        super().__init__( dataset_name, file_name, part )
        
        core_list = self.get_core_content( self.texts )
        split_list = self.split_core_content( core_list )
        self.rule_texts = self.merge_proof( split_list )
        self.keywords = self.get_cpl_keyword()
    
    # 从原始ruled_text中获取"申辩证"部分
    def get_core_content( self, ruled_texts ):
        core_list = []
        for i in range( len(ruled_texts) ):
            core_list.append( ruled_texts[i]["正文"]["申辩证"])
        return core_list

    # 将裁判文书粗略分为原告、被告、法院三方
    def split_core_content( self, core_list ):
        defandent = {
            "辩称":[],
            "答辩":[],
            "抗辩":[]
        }
        court = {
            "本院认为":[],
            "认定":["辩称"],
            "查明":["辩称"],
            "经审查":[]
            
        }
        orders = [ defandent, court]
        split_list = []
        # 遍历每一份文档
        for i in range(  len(core_list) ):
            texts = core_list[i]
            temp = {}
            split_index = [ None, None ]
            start_index = 0                 # 每次遍角色历开始的序号
            # 遍历每一份文档的每句，需要处理原被告可能的缺失
            for j in range( len(texts )):
                if start_index == 2:        # 当开始序号=2时，说明角色遍历已经完成
                    break
                line = texts[j]
                # 遍历两个角色
                for current_index in range( start_index, 2):
                    current_entity = orders[ current_index ]
                    for may_word in current_entity.keys():
                        if may_word in line:
                            flag = 0
                            for ban_word in current_entity[may_word]:
                                if ban_word in line:        # 有冲突词，匹配失败
                                    flag=1
                                    break
                            if flag==0:
                                # 没有禁用词
                                split_index[current_index] = j
                                start_index = current_index +1
                                break
            #if split_index[0] == None:
            #    print( f"""第{i}份文档没有原告诉请""" )
            if split_index[1] == None:
                raise Exception( f"""第{i}份文档没有法院判决{split_index}""")
            temp["原告"] = texts[ : split_index[0]] if split_index[0]!=None else texts[0: split_index[1]]
            temp["被告"] = texts[ split_index[0]: split_index[1]] if split_index[0]!=None else []
            temp["法院"] = texts[ split_index[1]: ]
            split_list.append( temp )
        return split_list

    # 将文本中之前安装/n分割造成的证据分段合并回去
    def merge_proof( self, split_list ):
        ret_list = []
        for p in range( len(split_list) ):
            splits_one = split_list[p]
            for key in splits_one.keys():
                lists = splits_one[key]
                new_list = []
                temp = None
                for i in range( len(lists)):
                    line = lists[i]
                    if line.endswith("证据："):
                        temp = line
                    else:
                        if line.endswith("；") and temp!=None:
                            temp = temp+line
                        else:
                            if temp!=None:
                                new_list.append( temp )
                                temp = None
                            else:
                                new_list.append( line )
                splits_one[key] = new_list
            ret_list.append( splits_one )
        return ret_list
    
    def get_cpl_keyword( self ):
        keywords = []
        for key in cpl_keyword.keys():
            if key in Plaintiff_claim_attributes:
                for keyword in cpl_keyword[key]:
                    if keyword not in keywords:
                        keywords.append( keyword )
        return keywords