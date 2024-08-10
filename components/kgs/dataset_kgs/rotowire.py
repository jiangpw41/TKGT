from collections import OrderedDict
import os
import sys

_ROOT_PATH = os.path.abspath(__file__)
for i in range(4):
    _ROOT_PATH = os.path.dirname( _ROOT_PATH )
sys.path.insert(0, _ROOT_PATH)
from utils import KnowledgeGraph

rotowire_value_range = {
    "String" : str,
    "Number" : int
}


# 行数2（主客）,列原本15列，但实际12+1列（没有城市名、罚球命中率）
_team_col_name = OrderedDict({
    "Team name" : rotowire_value_range["String"],                      # 球队名，字符串
    "Number of team assists" : rotowire_value_range["Number"],         # 球队助攻，整数
    "Percentage of 3 points" : rotowire_value_range["Number"],         # 球队三分命中率，整数（43%——>43）
    "Percentage of field goals" : rotowire_value_range["Number"],      # 球队命中率，整数（43%——>43）
    "Losses" : rotowire_value_range["Number"],                         # 球队负场数，整数
    "Total points" : rotowire_value_range["Number"],                   # 球队总分，整数
    "Points in 1st quarter" : rotowire_value_range["Number"],          # 第一节得分，整数
    "Points in 2nd quarter" : rotowire_value_range["Number"],          # 第二节得分，整数
    "Points in 3rd quarter" : rotowire_value_range["Number"],          # 第三节得分，整数
    "Points in 4th quarter" : rotowire_value_range["Number"],          # 第四节得分，整数
    "Rebounds" : rotowire_value_range["Number"],                       # 篮板球数，整数
    "Turnovers" : rotowire_value_range["Number"],                      # 失误数，整数
    "Wins"  : rotowire_value_range["Number"]                           # 球队胜场数，整数
})
_team_name = [                  # 主队在前，可能为0
    "Home team ",                     # 主队
    "visiting team"                   # 客队
]

# 行数不定（球员编号0-25）,列原本24列，但实际19+1列（没有球员全名、球员姓氏、球员位置、所属球队所在城市）
_player_col_name = OrderedDict({
    'Name': rotowire_value_range["String"],                           # 球员名
    'Assists' : rotowire_value_range["Number"],                        # 助攻
    'Blocks' : rotowire_value_range["Number"],                         # 盖帽
    'Defensive rebounds' : rotowire_value_range["Number"],             # 防守篮板
    '3-pointers attempted' : rotowire_value_range["Number"],           # 三分球尝试次数
    '3-pointers made' : rotowire_value_range["Number"],                # 三分球命中次数
    '3-pointer percentage' : rotowire_value_range["Number"],            # 三分球命中率

    'Field goals attempted' : rotowire_value_range["Number"],          # 投篮尝试次数
    'Field goals made' : rotowire_value_range["Number"],               # 投篮命中次数
    'Field goal percentage' : rotowire_value_range["Number"],          # 投篮命中率

    'Free throws attempted' : rotowire_value_range["Number"],          # 罚球尝试次数
    'Free throws made' : rotowire_value_range["Number"],               # 罚球命中次数
    'Free throw percentage' : rotowire_value_range["Number"],          # 罚球命中率

    'Minutes played' : rotowire_value_range["Number"],                 # 上场时间
    'Offensive rebounds' : rotowire_value_range["Number"],             # 进攻篮板
    'Personal fouls' : rotowire_value_range["Number"],                 # 个人犯规
    'Points' : rotowire_value_range["Number"],                         # 得分
    'Total rebounds' : rotowire_value_range["Number"],                 # 总篮板
    'Steals' : rotowire_value_range["Number"],                         # 抢断
    'Turnovers' : rotowire_value_range["Number"],                      # 失误
})
_player_index = [ 
    i for i in range(26)              # 球员编号，实际从0顺延，可能为0
]  

'''

# Single entity each line of texts, no relationship and only properties
e2e_kg = KnowledgeGraph()
index = 0
e2e_kg.add_entity(f'{index}', { key:None for key in _col_name_value})
get_unfilled_labels = e2e_kg.get_unfilled_labels()
print(get_unfilled_labels)
'''