model_list = {
    "e2e":{
        "table_total":{
            "part_total":[
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/ChatGLM3-6B/ZhipuAI/chatglm3-6b",
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/e2e_3_50/ZhipuAI/chatglm3-6b",
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/e2e_3_50/3",
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/e2e_3_50/4",
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/e2e_3_50/5",             # 对应Prompt3
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/e2e_3_50/6",             # 对应Prompt3
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/e2e_3_50/7",             # 对应Prompt4
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/e2e_3_50/8",             # 对应Prompt3
            ]
        }
    },
    "rotowire":{
        "table1":{
            "first_column":[
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/ChatGLM3-6B/ZhipuAI/chatglm3-6b",
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/rotowire/1",                  # 2: Prompt2 主客队一起且text, epoch 3.0 
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/rotowire/2",                  # 3: Prompt2 主客队一起且context, epoch 3.0 

                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/rotowire/3",                  # 4: Prompt3 主客队一起且text, epoch 3.0
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/rotowire/4",                  # 5: Prompt3 主客队一起且context, epoch 3.0 
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/rotowire/5",                  # 6: Prompt2 主客队一起且context, epoch 5.0 
            ],
            "data_cell":[
                
            ]
        }
    },
    "cpl":{
        "table1":{
            "first_column":[
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/ChatGLM3-6B/ZhipuAI/chatglm3-6b",
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/cpl/first_column/0",
                "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/TKGT_Model/cpl/first_column/1",
            ],
            "data_cell":[
                
            ]
        }
    }
}


VALUE_NAN = "<NOT FOUND>"

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
 'Trail Blazers',
 'Warriors',
 'Wizards'}



Rotowire_Instruction = """
You are a useful basketball news assistant who can extract the Home team name and Visiting team name of today's NBA basketball game from contexts.
(1) Firstly, I will provide you with a set of clips from a news bulletin reporting on this game in "Context" below;
(2) Secondly, I will also provide you a set of relative team name in the "Team Names" below and you should select answers from it;
(3) Thirdly, judge which name is the "Home team" or which is the "Visiting team".
(4) Attention, news fragments may lost some information, so if there is No "Home team" or "Visiting team", just response <NOT FOUND>, or you will be fired for fake news.
"""

Rotowire_Prompts = """
Example 1:
Context: ['The Pelicans got their first win since the DeMarcus Cousins trade in this 23 - point victory, but it happened to come with him being suspended for this fixture']
Team Names: ["Pistons"]
Question: What's the name of the Home team?
Answer: <NOT FOUND>

Example 2:
Context: ['Karl-Anthony Towns went off for 37 points on 15 - of - 26 shooting, to go along with 13 rebounds and four blocks, to lead the way for the young Timberwolves',]
Team Names: ["Timberwolves"]
Question: What's the name of the Home team?
Answer: Timberwolves

Example 3:
Context: ['The San Antonio Spurs (35 - 23) defeated the Sacramento Kings (20 - 36) 107 - 96 on Friday',
"The Spurs have been struggling as of late, losing their four games previous to Friday's win over the Kings, who were without DeMarcus Cousins due to hip and ankle injuries",
'The Kings are now 13 - 17 at home this season',
'San Antonio will travel to Phoenix to take on the Suns on Saturday, and the Kings will host the Portland Trail Blazers on Sunday']
Team Names: ["Kings", "Spurs"]
Question: What's the name of the Visiting team?
Answer: Spurs

Your Turn
Context: {Context}
Team Names: {Names}
Question: What's the name of the {VorH} team?
Answer:
"""

Rotowire_Instruction_2_context = """
You are a football enthusiast, now extract the name and Home team and Visiting team of today's NBA basketball game from contexts.
A context about players performance and team results will be provided in "Context" below.
(1) "Team Names" may contain multiple options, or it may not contain any options at all.
(2) Based on basketball game common sense, you should knowledge a Home team is the team belongs to the city holding the game; Visiting team is from another city. Usually, if muti options, the first to be mentioned in 'Context' is always the Home team.
(3) Extract the names of the Home and Visiting team in 'VS' format, such as "Knicks 'VS' Grizzlies", the name before 'VS' is the Home team, after is the Visiting team.
(4) Attention, fragments may lost some information, so if there is No Home team or Visiting team or the infomation is confusion, replace the name with <NOT FOUND>, or you will be fired for fake news.
"""

Rotowire_Prompts_2_context = """
Example 1:
Context: ['Following Monday's 36 - point performance in the Pacers' loss to the Hornets, George has now scored a combined 70 points over his last two games and did so while shooting a scorching 27 - of - 44 (61 percent) from the field and 12 - of - 23 (52 percent) from behind the arc.']
Team Names: ["Pacers"]
Question: What's the name of the Home team and Visiting team?
Answer: <NOT FOUND> VS <NOT FOUND>

Example 2:
Context: ['The All-Star guard almost outscored his other four teammates on the first unit, who only combined for 36 points, a total that was matched by the five players on the Clippers bench',
 'The Grizzlies received a combined 51 points from Mike Conley and Marc Gasol, but only 37 points from 10 other players who logged minutes',
 'They managed just a 37 percent success rate from the field, while their 19 turnovers led to 30 points for the Clippers.']
Team Names: ["Clippers", "Grizzlies"]
Question: What's the name of the Home team and Visiting team?
Answer: Grizzlies VS Clippers

Example 3:
Context: ['As a team, the Bulls shot a whopping 51 percent from the field and reached the free - throw line 35 times.']
Team Names: ["Bulls"]
Question: What's the name of the Home team and Visiting team?
Answer: Bulls VS <NOT FOUND>

Your Turn
Context: {Context}
Team Names: {Names}
Question: What's the name of the Home team and Visiting team?
Answer:
"""

Rotowire_Instruction_2_text = """
You are a football enthusiast, now extract the name and Home team and Visiting team of today's NBA basketball game from contexts.
A context about players performance and team results will be provided in "Context" below.
(1) "Team Names" may contain multiple options, or it may not contain any options at all.
(2) Based on basketball game common sense, you should knowledge a Home team is the team belongs to the city holding the game; Visiting team is from another city. Usually, if muti options, the first to be mentioned in 'Context' is always the Home team.
(3) Extract the names of the Home and Visiting team in 'VS' format, such as "Knicks 'VS' Grizzlies", the name before 'VS' is the Home team, after is the Visiting team.
(4) Attention, fragments may lost some information, so if there is No Home team or Visiting team or the infomation is confusion, replace the name with <NOT FOUND>, or you will be fired for fake news.
"""

Rotowire_Prompts_2_text = """
Example 1:
Context: "Following a week filled with trade rumors, Paul George came out of the All-Star break in fairly unimpressive fashion. In his first four games following the break, George shot a combined 16 - of - 54 (29 percent) from the field and was averaging just 14 points per game over that stretch. However, in his last two games, George has flipped the script entirely and rattled off a pair of incredible offensive performances. Following Monday's 36 - point performance in the Pacers' loss to the Hornets, George has now scored a combined 70 points over his last two games and did so while shooting a scorching 27 - of - 44 (61 percent) from the field and 12 - of - 23 (52 percent) from behind the arc. The performances from George on Sunday and Monday were by far his best back - to - back shooting and scoring performances of the season."
Team Names: ["Pacers"]
Question: What's the name of the Home team and Visiting team?
Answer: <NOT FOUND> VS <NOT FOUND>

Example 2:
Context: "Chris Paul stepped up his offense as the starting five found points relatively hard to come by for a second straight game. Paul's 27 points and six steals equaled season highs, while his 11 dimes represented a new high - water mark. His 15 free - throw shots were also a game high, and he converted 14 of them into points. The All-Star guard almost outscored his other four teammates on the first unit, who only combined for 36 points, a total that was matched by the five players on the Clippers bench. The Grizzlies received a combined 51 points from Mike Conley and Marc Gasol, but only 37 points from 10 other players who logged minutes. They managed just a 37 percent success rate from the field, while their 19 turnovers led to 30 points for the Clippers."
Team Names: ["Grizzlies", "Clippers"]
Question: What's the name of the Home team and Visiting team?
Answer: Grizzlies VS Clippers

Example 3:
Context: "On Sunday, rising young forward Doug McDermott had one of the better nights of his career. McDermott scored a team - high 31 points with three three - pointers and 10 - of - 11 from the free - throw line. Superstar forward Jimmy Butler anchored the starting five, going for 16 points, eight rebounds, six assists, and three steals. Veteran big man Taj Gibson led the starting five in scoring with 18 points and had eight rebounds. As a team, the Bulls shot a whopping 51 percent from the field and reached the free - throw line 35 times. The Grizzlies, meanwhile, saw strong play from their veteran core. Center Marc Gasol scored 24 points to go with 11 rebounds. Point guard Mike Conley, meanwhile, led the team with 28 points and eight assists. Off the bench, big man Zach Randolph had 16 rebounds, including eight on the offensive end."
Team Names: ["Bulls"]
Question: What's the name of the Home team and Visiting team?
Answer: Bulls VS <NOT FOUND>

Your Turn
Context: {Context}
Team Names: {Names}
Question: What's the name of the Home team and Visiting team?
Answer:
"""

Rotowire_Instruction_2_text = """
You are a football enthusiast, now extract the name and Home team and Visiting team of today's NBA basketball game from contexts.
A context about players performance and team results will be provided in "Context" below.
(1) "Team Names" may contain multiple options, or it may not contain any options at all.
(2) Based on basketball game common sense, you should knowledge a Home team is the team belongs to the city holding the game; Visiting team is from another city. Usually, if muti options, the first to be mentioned in 'Context' is always the Home team.
(3) Extract the names of the Home and Visiting team in 'VS' format, such as "Knicks 'VS' Grizzlies", the name before 'VS' is the Home team, after is the Visiting team.
(4) Attention, fragments may lost some information, so if there is No Home team or Visiting team or the infomation is confusion, replace the name with <NOT FOUND>, or you will be fired for fake news.
"""

Rotowire_Instruction_3_text = """
You are a football enthusiast, now extract the name of Home team and Visiting team of today's NBA basketball game from contexts.
A context about players performance and team results will be provided in "Context" below.
(1) "Team Names" may contain multiple options, or it may not contain any options at all. You must choose zero, one, or two names from "Team Names" based on "Context".
(2) If "Team Names" does not containe neither the Home team nor the Visiting team, just response "<NOT FOUND>".
(3) Else if "Team Names" only containes one of the Home and Visiting team, just response the team name like "Pacers"
(4) Else, "Team Names" containes both names, response the two names separated with commas ", " like "Pacers, Grizzlies". The order is not important.
"""

Rotowire_Prompts_3_text = """
Example 1:
Context: "Following a week filled with trade rumors, Paul George came out of the All-Star break in fairly unimpressive fashion. In his first four games following the break, George shot a combined 16 - of - 54 (29 percent) from the field and was averaging just 14 points per game over that stretch. However, in his last two games, George has flipped the script entirely and rattled off a pair of incredible offensive performances. Following Monday's 36 - point performance in the Pacers' loss to the Hornets, George has now scored a combined 70 points over his last two games and did so while shooting a scorching 27 - of - 44 (61 percent) from the field and 12 - of - 23 (52 percent) from behind the arc. The performances from George on Sunday and Monday were by far his best back - to - back shooting and scoring performances of the season."
Team Names: ["Pacers"]
Question: What's the name of the Home team and Visiting team?
Answer: <NOT FOUND>

Example 2:
Context: "Chris Paul stepped up his offense as the starting five found points relatively hard to come by for a second straight game. Paul's 27 points and six steals equaled season highs, while his 11 dimes represented a new high - water mark. His 15 free - throw shots were also a game high, and he converted 14 of them into points. The All-Star guard almost outscored his other four teammates on the first unit, who only combined for 36 points, a total that was matched by the five players on the Clippers bench. The Grizzlies received a combined 51 points from Mike Conley and Marc Gasol, but only 37 points from 10 other players who logged minutes. They managed just a 37 percent success rate from the field, while their 19 turnovers led to 30 points for the Clippers."
Question: What's the name of the Home team and Visiting team?
Answer: Grizzlies, Clippers

Example 3:
Context: "On Sunday, rising young forward Doug McDermott had one of the better nights of his career. McDermott scored a team - high 31 points with three three - pointers and 10 - of - 11 from the free - throw line. Superstar forward Jimmy Butler anchored the starting five, going for 16 points, eight rebounds, six assists, and three steals. Veteran big man Taj Gibson led the starting five in scoring with 18 points and had eight rebounds. As a team, the Bulls shot a whopping 51 percent from the field and reached the free - throw line 35 times. The Grizzlies, meanwhile, saw strong play from their veteran core. Center Marc Gasol scored 24 points to go with 11 rebounds. Point guard Mike Conley, meanwhile, led the team with 28 points and eight assists. Off the bench, big man Zach Randolph had 16 rebounds, including eight on the offensive end."
Team Names: ["Bulls"]
Question: What's the name of the Home team and Visiting team?
Answer: Bulls

Your Turn
Context: {Context}
Team Names: {Names}
Question: What's the name of the Home team and Visiting team?
Answer:
"""