'''
所有数据集的table结构都用两个层级
Tablex > "Row_Name"("Number"表示列表里的角色是否可多个，列表中为角色类型) and "Fields"(字段字典，取值定义)
'''


import sys
import os
sys.path.insert(0, os.path.dirname( os.path.dirname( os.path.abspath(__file__) )))
from dataset_kgs.e2e_kg import e2e_value_range
from dataset_kgs.rotowire import rotowire_value_range


# This dataset include two table each instance
fields_list_rotowire = {
    # Table 1: Team-level info including fields and row_name
    "Table1":{
        "Row_Name" : {
            "Team " : 2,                   
        },
        "Fields" : {
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
            "Wins" : rotowire_value_range["Number"],                            # 球队胜场数，整数
        }
    },
    # Table 2: Player-level info only including fields because row_name is index
    "Table2": {
        "Row_Name" : {
            "player" : 0
        },
        "Fields" : {
            'Name' : rotowire_value_range["String"],                           # 球员名
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
        }
    }
}

fields_list_e2e = {
    "Table1":{
        "Row_Name" : {
            "Restaurant" : 1
        },
        "Fields" : {
            'Name' : e2e_value_range["String_Name"],                               # 餐厅名，理论上字符串无限，
            'Price range' : e2e_value_range["Price range"],                        # 价格范围，
            'Customer rating' : e2e_value_range["Customer rating"],                # 用户评价：
            'Near' : e2e_value_range["String_Name"],                               # 附近标识（地点），理论上字符串无限
            'Food' : e2e_value_range["Food"],                                      # 食物类型
            'Area' : e2e_value_range["Area"],                                      # 地区
            'Family friendly'  : e2e_value_range["Family friendly"]                # 是否家庭友好
        }
    }
}