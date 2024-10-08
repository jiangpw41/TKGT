"""
在这个文件夹中注册用于微调/推理的提示词模板
"""

########################################(提示词实体_下)##################################################
INSTRUCTION_e2e = """
 You are a inforamtion extractor for {ROLE}, and you can response questions strictly based on context in {LAN} and no more than 5 words. 
 (1) Firstly, judge whether answers are in the context. If not, resoponse {NO_VALUE}, or you will be fired for responsing fake infomation. If are, response base on context.
 (2) Secondly, if Scope provided, your answers must be chosen from it; if <No Scope>, extract from context precisely.
"""

PROMPT_TEMPLATE_e2e = """
Example 1
 Question: What's the 'Price range' of the Restaurant?
 Context: The Mill is a pub providing English Food with Moderate price range.
 Scope: ['More than £30', 'Cheap', 'Less than £20', '£20-25', 'Moderate', 'High']
 Answer: Moderate

Example 2
 Question: What's the 'Customer rating' of the Restaurant?
 Context: The Mill, a low price family friendly breakfast.
 Scope: ['5 out of 5', 'Low', 'Average', '3 out of 5', '1 out of 5', 'High'] 
 Answer: <NOT FOUND>

Example 3
 Question: What's the 'Near' of the Restaurant?
 Context: Green Man is located riverside near the Express by Holiday Inn. 
 Scope: <No Scope>
 Answer: Express by holiday inn

Your Turn
 Question: What's the {FIELD} of the {ROLE}?
 Context: {CONTEXT} 
 Scope: {VALUE_RANGE} 
 Answer: 
"""

Rotowire_Instruction_First_Column_v3_context = """
You are a football enthusiast, now extract the name of Home team and Visiting team of today's NBA basketball game from contexts.
A context about players performance and team results will be provided in "Context" below.
(1) "Team Names" may contain multiple options, or it may not contain any options at all. You must choose zero, one, or two names from "Team Names" based on "Context".
(2) If "Team Names" does not containe neither the Home team nor the Visiting team, just response "<NOT FOUND>".
(3) Else if "Team Names" only containes one of the Home and Visiting team, just response the team name like "Pacers"
(4) Else, "Team Names" containes both names, response the two names separated with commas ", " like "Pacers, Grizzlies". The order is not important.
"""

Rotowire_Prompts_First_Column_v3_context = """
Example 1:
Context: ['Following Monday's 36 - point performance in the Pacers' loss to the Hornets, George has now scored a combined 70 points over his last two games and did so while shooting a scorching 27 - of - 44 (61 percent) from the field and 12 - of - 23 (52 percent) from behind the arc.']
Team Names: ["Pacers"]
Question: What's the name of the Home team and Visiting team?
Answer: <NOT FOUND>

Example 2:
Context: ['The All-Star guard almost outscored his other four teammates on the first unit, who only combined for 36 points, a total that was matched by the five players on the Clippers bench',
 'The Grizzlies received a combined 51 points from Mike Conley and Marc Gasol, but only 37 points from 10 other players who logged minutes',
 'They managed just a 37 percent success rate from the field, while their 19 turnovers led to 30 points for the Clippers.']
Team Names: ["Clippers", "Grizzlies"]
Question: What's the name of the Home team and Visiting team?
Answer: Grizzlies, Clippers

Example 3:
Context: ['As a team, the Bulls shot a whopping 51 percent from the field and reached the free - throw line 35 times.']
Team Names: ["Bulls"]
Question: What's the name of the Home team and Visiting team?
Answer: Bulls

Your Turn
Context: {Context}
Team Names: {Names}
Question: What's the name of the Home team and Visiting team?
Answer:
"""

CPL_INSTRUCTION_First_Column_v1 = """
 你是一名中国大陆民法领域的法律助手，主要从事民间借贷方向的法院裁判文书整理和结构化工作。下面请你根据裁判文书相关上下文提取指定对象的名称，要求如下：
 （1）我将在后文中的“目标角色”部分为你明确提供一个要提取名称信息的对象，并为你在“相关上下文”部分提供关于这个目标角色在名称方面的裁判文书原文片段信息。
 （2）目标角色指的范畴是民间借贷法律领域的不同角色，如'出借人（原告）', '被告'。如果某个角色为公司、组织等法人，只返回公司名称而非法人代表名称。
 （3）如果某个角色存在多个对象，比如多个被告，请提取全部被告的名称，并返回以顿号“、”分隔的名称列表，如“陈亚莉、马保国、马成功”。
 （4）请你精练、直接地返回提取到的字段目标的值，不要有任何其他间接性的说明。例如，对于“被告”这一目标角色的名称，直接返回提取到的值，如“许超”。不允许任何形式的附加格式如“名称：许超”。
 （5）如果你返回虚假的内容，你将被解雇。
"""

CPL_PROMPT_First_Column_v1 = """
 样例 1：
 目标角色：原告
 相关上下文：["原告：周俭，女，1971年5月31日出生，汉族，住合肥市庐阳区。",
            "原告周俭诉被告苗健玮、方惠、安徽俊惠建筑装饰有限责任公司（以下简称“俊惠公司”）民间借贷纠纷一案，本院立案受理后，依法组成合议庭，公开开庭进行了审理。原告周俭的委托代理人刘玮，被告苗健玮到庭参加诉讼。被告方惠、俊惠公司经本院传票传唤无正当理由未庭参加诉讼。本案现已审理终结。"]
 问题：出借人（原告）的名称是？
 答案：周俭

 样例 2：
 目标角色：被告
 相关上下文：["被告：陈亚莉，女，1991年9月22日出生，汉族，住安徽省合肥市包河区。",
 "被告：马郭保，男，1972年5月20日出生，汉族，住安徽省合肥市蜀山区。",
 "原告王章发与被告陈亚莉、马郭保民间借贷纠纷一案，本院于2016年11月7日立案后，依法适用简易程序公开开庭进行了审理。原告王章发及其委托代理人陈叶艇，被告马郭保到庭参加诉讼，被告陈亚莉经本院传票传唤拒不到庭参加诉讼。本案现已审理终结。"]
 问题：被告的名称是？
 答案：陈亚莉、马郭保

 看过了前面2个样例，现在到你实践了：
 目标角色：{ROLE}
 相关上下文：{CONTEXT}
 问题：{ROLE}的名称是？
 答案：
"""


CPL_INSTRUCTION_First_Column_v2 = """
 你是一名中国大陆民法领域的法律助手，请你根据裁判文书信息提取原告和所有被告的姓名名称，要求如下：
 （1）我将在后文中的“目标角色”部分为你明确提供一个要提取名称信息的对象，并为你在“相关上下文”部分提供裁判文书原文片段信息。
 （2）目标角色指的范畴是民间借贷法律领域的不同角色，如'原告', '被告'，你要从上下文中准确识别哪些人名、企业名属于原告（出借人），哪些属于被告（借款人）。
 （3）如果某个角色存在多个被告，请提取全部被告的名称，并返回以顿号“、”分隔的名称列表，如“陈亚莉、马保国、马成功”。
 （4）你返回的名称必须是来自原文的人名或公司名，不能有多余的文字，也不能返回不存在的名字。如果你返回虚假的内容，你将被解雇。
"""

CPL_PROMPT_First_Column_v2 = """
 样例 1：
 目标角色：原告
 相关上下文：["原告：周俭，女，1971年5月31日出生，汉族，住合肥市庐阳区。",
            "原告周俭诉被告苗健玮、方惠、安徽俊惠建筑装饰有限责任公司（以下简称“俊惠公司”）民间借贷纠纷一案，本院立案受理后，依法组成合议庭，公开开庭进行了审理。原告周俭的委托代理人刘玮，被告苗健玮到庭参加诉讼。被告方惠、俊惠公司经本院传票传唤无正当理由未庭参加诉讼。本案现已审理终结。"]
 问题：原告是？
 答案：周俭

 样例 2：
 目标角色：被告
 相关上下文：["被告：陈亚莉，女，1991年9月22日出生，汉族，住安徽省合肥市包河区。",
 "被告：马郭保，男，1972年5月20日出生，汉族，住安徽省合肥市蜀山区。",
 "原告王章发与被告陈亚莉、马郭保民间借贷纠纷一案，本院于2016年11月7日立案后，依法适用简易程序公开开庭进行了审理。原告王章发及其委托代理人陈叶艇，被告马郭保到庭参加诉讼，被告陈亚莉经本院传票传唤拒不到庭参加诉讼。本案现已审理终结。"]
 问题：被告是？
 答案：陈亚莉、马郭保

 看过了前面2个样例，现在到你实践了：
 目标角色：{ROLE}
 相关上下文：{CONTEXT}
 问题：{ROLE}是？
 答案：
"""
########################################(提示词实体_上)##################################################

e2e_prompt_list = {
    "total" : [
        (INSTRUCTION_e2e, PROMPT_TEMPLATE_e2e), 
    ]
}

rotowire_prompt_list = {
    "first_column" : [
        (Rotowire_Instruction_First_Column_v3_context, Rotowire_Prompts_First_Column_v3_context), 
    ]
}

cpl_prompt_list = {
    "first_column" : [
        (CPL_INSTRUCTION_First_Column_v1, CPL_PROMPT_First_Column_v1), 
        (CPL_INSTRUCTION_First_Column_v2, CPL_PROMPT_First_Column_v2), 
    ]
}

_TOTAL_PROMPT_LIST = {
    "e2e": e2e_prompt_list,
    "rotowire": rotowire_prompt_list,
    "cpl": cpl_prompt_list
}