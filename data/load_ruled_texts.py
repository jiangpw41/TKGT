import os
import sys
import re

_ROOT_PATH = os.path.abspath(__file__)
for i in range(2):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert(0, _ROOT_PATH)
from utils import load_data, save_data
from data.data_manager import DataManager, data_split
from KGs.dataset_KGs.rotowire import rotowire_total_team_name


def ruled_rotowire( ):
    for part in [ "train", "test"]:
        texts = load_data( os.path.join( _ROOT_PATH, f"data/rotowire/{part}.text"), "text")
        candidate_team_context = []
        candidate_player_context = []
        save_dict = {}
        for i in range( len(texts) ):
            text = texts[i]
            text_split = text.split(". ")
            candidate_team_name = []
            candidate_context = []
            temp_player = []
            for chunk in text_split:
                flag = 0
                for _name in rotowire_total_team_name:
                    if _name.strip().lower() in chunk.strip().lower():
                        flag = 1
                        if _name not in candidate_team_name:
                            candidate_team_name.append( _name )
                        if chunk.strip() not in candidate_context:
                            candidate_context.append( chunk.strip() )
                if flag==0:
                    temp_player.append( chunk.strip() )
            candidate_player_context.append( f"Candidate context: {temp_player}" )
            candidate_team_context.append( f"Candidate team name: {candidate_team_name}; Candidate context: {candidate_context}")
        save_dict["Team"] = candidate_team_context
        save_dict["Player"] = candidate_player_context
        save_path = os.path.join( _ROOT_PATH, f"data/rotowire/{part}.text_ruled.json")
        save_data( save_dict, save_path)


def _ruled_load( dataset_name, mode, resplit, subtable_name=None ):
    
    if dataset_name == "cpl":
        ruled_text_path = os.path.join( _ROOT_PATH, f"data/{dataset_name}/{mode}.text_ruled.json")
        if not os.path.exists( ruled_text_path ) or resplit:
            # 加载与筛选对齐
            jsons_all = load_data( os.path.join( _ROOT_PATH, "Mixed_IE/further_processed/regulation/para_splited_B.json"), "json")
            times_3_index  = load_data( os.path.join( _ROOT_PATH, "data/cpl/original/over_3_time.json"), "json")
            new_jsons_all = []
            for i in range( len(jsons_all) ):
                if i not in times_3_index["over_list"]:
                    new_jsons_all.append( jsons_all[str(i)] )
            index = load_data( os.path.join(_ROOT_PATH , "data/cpl/index.pickle"), "pickle")
            # 修正部分划分不到位
            new_jsons_all_new = []
            for i in range( len(new_jsons_all) ):
                temp_dict = {
                    "标题" : new_jsons_all[i]["标题"],
                    "开头" : new_jsons_all[i]["开头"],
                    "附录" : new_jsons_all[i]["附录"],
                    "正文" : {},
                }
                current_json_core = new_jsons_all[i]["正文"]
                new_procedure = []
                new_argue = []
                new_tail = []
                # 处理程序信息
                match_word = re.compile(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:万)?元')
                for j in range(len(current_json_core["程序信息"])):
                    matched_words = re.findall(match_word, current_json_core["程序信息"][j])
                    if len(matched_words)>0:
                        new_procedure = current_json_core["程序信息"][ : j]
                        new_argue = current_json_core["程序信息"][ j: ]
                        break
                    else:
                        new_procedure.append( current_json_core["程序信息"][j] )
                temp_dict["正文"]["程序信息"] = new_procedure
                # 处理申诉
                for j in range(len(current_json_core["申辩证"])):
                    if "受理费" in current_json_core["申辩证"][j] and j >= len(current_json_core["申辩证"])-4:
                        new_tail = current_json_core["申辩证"][ j: ]
                        break
                    else:
                        new_argue.append( current_json_core["申辩证"][j] )
                temp_dict["正文"]["申辩证"] = new_argue
                new_tail.extend( current_json_core["末尾信息"] )
                temp_dict["正文"]["末尾信息"] = new_tail
                new_jsons_all_new.append( temp_dict )

            ruled_text_train, ruled_text_test = data_split( new_jsons_all_new, [0.7, 0.3], index)
            
            save_data( ruled_text_train, os.path.join( _ROOT_PATH, f"data/cpl/train.text_ruled.json"))
            save_data( ruled_text_test, os.path.join( _ROOT_PATH, f"data/cpl/test.text_ruled.json"))
        return load_data( ruled_text_path, "json")         # 加载规则TEXT用于Context
    elif dataset_name == "rotowire":
        ruled_text_path = os.path.join( _ROOT_PATH, f"data/{dataset_name}/{mode}.text_ruled.json")
        if subtable_name==None:
            raise Exception( f"Rotowire数据集需要指定子表格名")
        if not os.path.exists( ruled_text_path ) or resplit:
            ruled_rotowire( )
        return load_data( ruled_text_path, "json")[subtable_name]
    else:
        print(f"数据集{dataset_name}没有规则分割")
        return None
    
if __name__=="__main__":
    """
    parser = argparse.ArgumentParser(description="Run script with external arguments")
    parser.add_argument('--dataset_name', type=str, required=True, help='数据集名')
    parser.add_argument('--subtable_name', type=str, required=False, help='子表名')
    parser.add_argument('--resplit', type=int, required=False, help='是否覆盖')
    args = parser.parse_args()
    dataset_name = args.dataset_name
    subtable_name = args.subtable_name if args.subtable_name else None
    resplit = False if args.resplit==0 else True
    """
    dataset_name = "cpl"
    subtable_name = None
    resplit = True
    
    for mode in [ "train", "test"]:
        ruled_texts = _ruled_load( dataset_name, mode, resplit, subtable_name)
    print("sss")