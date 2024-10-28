import pandas as pd
import os
import sys
from tqdm import tqdm
import concurrent
import shutil
from concurrent.futures import ProcessPoolExecutor


# Event-Oriented
_ROOT_PATH = os.path.abspath(__file__)
for i in range(2):
    _ROOT_PATH = os.path.dirname( _ROOT_PATH )
sys.path.insert(0, _ROOT_PATH)
from utils import read_text_to_list, create_logger

logger = create_logger( "preprocess_log", os.path.join(_ROOT_PATH, "preprocess/preprocess.log"))
_DATA_PATH = os.path.join( _ROOT_PATH, "raw/rotowire")
_SAVE_PATH = os.path.join( _ROOT_PATH, "data/rotowire/original")

if not os.path.exists(_SAVE_PATH):  
    # 如果目录不存在，则创建它  
    os.makedirs(_SAVE_PATH)
    logger.info( "Preprocess: have created path of Rotowire.")

# 行数2（主客）,列原本15列，但实际12+1列（没有城市名、罚球命中率）
_team_col_name = [
    "Team name",                      # 球队名，字符串
    "Number of team assists",         # 球队助攻，整数
    "Percentage of 3 points",         # 球队三分命中率，整数（43%——>43）
    "Percentage of field goals",      # 球队命中率，整数（43%——>43）
    "Losses",                         # 球队负场数，整数
    "Total points",                   # 球队总分，整数
    "Points in 1st quarter",          # 第一节得分，整数
    "Points in 2nd quarter",          # 第二节得分，整数
    "Points in 3rd quarter",          # 第三节得分，整数
    "Points in 4th quarter",          # 第四节得分，整数
    "Rebounds",                       # 篮板球数，整数
    "Turnovers",                      # 失误数，整数
    "Wins"                            # 球队胜场数，整数
] 
_team_name = [                  # 主队在前，可能为0
    "Home team ",                     # 主队
    "visiting team"                   # 客队
]

# 行数不定（球员编号0-25）,列原本24列，但实际19+1列（没有球员全名、球员姓氏、球员位置、所属球队所在城市）
_player_col_name = [
    'Name',                           # 球员名
    'Assists',                        # 助攻
    'Blocks',                         # 盖帽
    'Defensive rebounds',             # 防守篮板
    '3-pointers attempted',           # 三分球尝试次数
    '3-pointers made',                # 三分球命中次数
    '3-pointer percentage',            # 三分球命中率

    'Field goals attempted',          # 投篮尝试次数
    'Field goals made',               # 投篮命中次数
    'Field goal percentage',          # 投篮命中率

    'Free throws attempted',          # 罚球尝试次数
    'Free throws made',               # 罚球命中次数
    'Free throw percentage',          # 罚球命中率

    'Minutes played',                 # 上场时间
    'Offensive rebounds',             # 进攻篮板
    'Personal fouls',                 # 个人犯规
    'Points',                         # 得分
    'Total rebounds',                 # 总篮板
    'Steals',                         # 抢断
    'Turnovers',                      # 失误
]
_player_index = [ 
    i for i in range(26)              # 球员编号，实际从0顺延，可能为0
]  

def multi_process( processor, task_list, _type ):
    # 所有使用多进程工具的函数，必须将迭代对象及其index作为函数参数的前两位
    splited_task_list = [None]*len(task_list)
    with ProcessPoolExecutor() as executor:
        future_to_item = {}
        for j, item in enumerate(task_list):
            future_to_item[executor.submit(processor, _type, item, j)] = j 
        with tqdm(total=len(future_to_item), desc=f"Preprocess Rotowire: {_type}") as pbar:
            for future in concurrent.futures.as_completed(future_to_item): 
                future.result()
                pbar.update(1)

def convert_rotowore_to_table( _type, table, index):
    # init
    _empty_team_data = [[None for _ in range( len(_team_col_name))] for _ in range( len(_team_name) )]
    _empty_player_data = [[None for _ in range( len(_player_col_name))] for _ in range( len(_player_index) )]

    team = pd.DataFrame(_empty_team_data, columns=_team_col_name )
    team.index = _team_name

    player = pd.DataFrame(_empty_player_data, columns=_player_col_name )
    player.index = _player_index
    
    # fill
    #if i == 1514:
    empty_list = [team, player]
    table = table.split("Player: <NEWLINE> |  ")    # 将表格分为球队和球员两类'Team: <NEWLINE> Player: <NEWLINE> |  |'
    for k in range( len(table) ):
        _object = table[k]
        if k ==0:
            _object = _object[len("Team: <NEWLINE> "):]
        empty_table = empty_list[k]
        if len(_object)>0:
            _object = list(filter(None, _object.split("<NEWLINE>") ))
            total = []
            for i in range(len(_object)):
                temp = []
                attr = _object[i].strip()[1:-1]
                if attr=="":
                    continue
                attr = list(filter(None, attr.split('|') ))
                if i == 0:
                    if k==1:
                        temp.append("Name")
                    for item in attr:
                        if item.replace(" ", "")=="":
                            temp.append("Team name")
                            continue
                        item = item.replace("|","").strip()
                        temp.append(item)
                else:
                    if len(attr)!=len(total[0]):
                        print( f"Index{index} _object not match ")
                        break
                    for p in range(len(attr)):
                        item = attr[p]
                        item = item.replace(" ","").strip()
                        if item!="":
                            if p==0:
                                temp.append(item)
                            else:
                                temp.append(int(item))
                        else:
                            temp.append(0)
                total.append(temp )
            if len(total)>0:
                attributes = total[0]
                indexes = _team_name if k==0 else _player_index
                for inde in range(1, len(total)):
                    line = total[inde]
                    for j in range(len(attributes)):
                        empty_table.loc[ indexes[inde-1], attributes[j]] = line[j]

    # 使用ExcelWriter对象写入Excel文件
    prefix, suffix = _type.split(".")[0], _type.split(".")[1]
    _SAVE_PATH_prefix = os.path.join( _SAVE_PATH, f"tables/{prefix}")
    if not os.path.exists(_SAVE_PATH_prefix):  
        # 如果目录不存在，则创建它  
        os.makedirs(_SAVE_PATH_prefix)
        logger.info( f"Preprocess: have created sub_path {prefix} of Rotowire.")
    with pd.ExcelWriter( os.path.join( _SAVE_PATH_prefix, f"{index}.xlsx") ) as writer:  
        team.to_excel(writer, sheet_name='team')  # 将df1写入Sheet1  
        player.to_excel(writer, sheet_name='player')  # 将df2写入Sheet2  


if __name__ == "__main__":
    
    datasets = ["train.data", "valid.data", "test.data"]
    for dataset in datasets:
        tables = read_text_to_list( os.path.join(_DATA_PATH, dataset) )
        multi_process(convert_rotowore_to_table, tables, dataset)
    for files in [ "test.text",  "train.text",  "valid.text"]:
        _from_path = os.path.join( _DATA_PATH, files)
        _to_path = os.path.join( _SAVE_PATH, files)
        shutil.copy2( _from_path, _to_path)
    #df_team = pd.read_excel('output.xlsx', sheet_name="team", index_col=0)        # df_player.loc[1]['Assists']
    #df_player = pd.read_excel('output.xlsx', sheet_name="player", index_col=0)