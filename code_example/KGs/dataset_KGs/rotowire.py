
__all__=["rotowire_kg_schema"]

rotowire_total_team_name = {'76ers',
 'Bucks',
 'Bulls',
 'Cavaliers',
 'Celtics',
 'Clippers',
 'Grizzlies',
 'Hawks',
 'Heat',
 'Hornets',
 'Jazz',
 'Kings',
 'Knicks',
 'Lakers',
 'Magic',
 'Mavericks',
 'Nets',
 'Nuggets',
 'Pacers',
 'Pelicans',
 'Pistons',
 'Raptors',
 'Rockets',
 'Spurs',
 'Suns',
 'Thunder',
 'Timberwolves',
 'TrailBlazers',
 'Warriors',
 'Wizards'}

total_team_city_map = {
    "Orleans" : "Pelicans",
    "Phoenix": "Suns",
    "Dallas": "Mavericks",
    "Orlando": "Magic",
    "Atlanta": "Hawks",
    "Cleveland": "Cavaliers",
    "Brooklyn": "Nets",
    "Angeles": "Lakers",
    "Milwaukee ": "Bucks",
    "Utah": "Jazz",
    "Denver": "Nuggets",
    "Antonio": "Spurs",
    "Indiana": "Pacers",
    "York": "Knicks",
    "Sixers": "76ers",
    "Detroit": "Pistons",
    "Houston": "Rockets",
    "Cavs": "Cavaliers",
    "Sacramento": "Kings",
    "City": "Thunder",
    "Minnesota ": "Timberwolves",
    "Charlotte": "Hornets",
    "Philadelphia": "76ers",
    "Chicago" : "Bulls",
    "Miami": "Heat",
    "Memphis": "Grizzlies",
    "Portland": "TrailBlazers",
    "Toronto": "Raptors",
    "Boston": "Celtics",
    "Golden State": "Warriors",
    "Washington": "Wizards"
    
}

rotowire_value_range = {
    "String" : str,
    "Number" : int
}

team_attr = {
    "Name" : rotowire_value_range["String"],                      # 球队名，字符串
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


player_attr = {
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

kg_schema = {
    "intro" : "It's a Knowledge Graph of the NBA basketball game, each graph contains as least two teams and several players' infomation.",
    "entity_type" : "multi_entity",        # "single_entity", or "multi_entity"
    "event_type" : "static",        # 完全静态如E2E和Rotowire的属性"static", 属性类化可多次可迭代成整体的"dynamic"
    "entity":{
        "Team":{
            "number": (1,2),     # 左右一样表示固定数量，左小右大表示闭区间取值范围，左大右小表示>=
            "intro" : "NBA球队整体数据",
            "predicate" : "的全组数据",
            "attributes": team_attr
        },
        "Player":{
            "number": (1,26),     # 左右一样表示固定数量，左小右大表示闭区间取值范围，左大右小表示>=
            "intro" : "球员个人数据",
            "predicate" : "的个人数据",
            "attributes": player_attr
        }
    },
    "relation":{                    # 仅仅记录需要被采集的关系
        "Team_and_Team":{
            "Home_and_Visiting":{
                "number": (1,1),
                "intro" : "主客队关系"
            },
        },
    }
}