'''
 社科（以人类及人类系统为核心）领域模型：避免本体论分类体系的庞杂。
 面向的是大规模、同类型、同领域的文本，从这些文本中可以构建领域模型
 先确定领域模型是event-oriented还是ontology-oriented，人类确定
 如果是ontology-oriented，则确定其完备的属性集，相关的关系、事件全都属性化
 如果是event-oriented，则确定顶层事件，并
    # 确定角色（有属性，角色类集成自人类或组织类）、关系（无属性）、事件（有属性）
    # 首先：构建领域所有角色类型的完备集合（确定层级关系），并补充其属性字段名
    # 其次：构建领域所有事件类型(有限个体)，并确定顶层事件，然后补充属性字段
    # 最后：建立关系，领域中所有角色和事件的确定关系，双向的


 （1）先基于专家知识设定通用种子，种子越多效果越好
 （2）参考专家种子，利用大模型内部知识创建领域模型草图draft。大模型只需要完成两种任务，枚举、选择，并按照格式要求输出
 （3）IE：基于block规则、统计（tokenizer、TF、DF）、深度学习方法（词性标注、命名实体识别、LLM问答），进行滚动实例学习的方法：可扩展。最终构建知识图谱
'''

from typing import OrderedDict
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate

list_example = [
    [{"示例输入": "医生、护士、警察、教师、士兵",
     "示例输出": "律师、消防员、公务员、清洁工、厨师"}],
    [{"示例输入": "上课、签约、巡检、咨询、求助",
     "示例输出": "违约、延后、看守、等待"}],
    [{"示例输入": "赔偿金、约定日期、手枪、扫把、桌子",
     "示例输出": "电脑、茶杯、飞机、行星"}],
    [{"示例输入": "(父亲，父子关系，儿子)、(老板, 雇佣关系, 员工)、(警察, 执法者与违法者关系, 小偷)",
     "示例输出": "(汽车, 保养与维修关系, 4S店)、(厨师, 服务关系, 顾客)"}],
]


_FIELD_TEMPLATE = {
    "Event-Oriented":{
        "Top_Event_Concept" : None,                            # 事件模型顶层事件类型（唯一性），如民间借贷案件
        "Test_Description" : None,                             # 文本集描述
        "Sub_Event" : {
            "Scalable": True,                                      # 是否需要在实例学习中自动扩展
            "dict":{}
        },                                                          # 子事件类（角色之间的动作、行为等，动态），都有多次可能
        "Role": {
            "Scalable": True,
            "dict":{}
        },                                                      # 事件中独立角色类型，具有自然、法律人格，如自然人、组织（继承自基类）。因为是社科领域，所以默认角色具有人格
        "Thing": {
            "Scalable": True,
            "dict":{}
        },                                                       # 事件中出现的无人格对象，
        "Relation" : {
            "Scalable": True,
            "list":[]
        },                                            
    },
    "Ontology-Oriented":{                                      # 面向本体的模型，不涉及事件
        "Top_Ontology_Concept" : None,                         # 本体模型顶层类型（唯一性）如历史人物、餐馆等
        "Test_Description" : None,
        "Role" :{
            "Individual": True,
            "Scalable": True,
            "dict":None
        },
    }
}




Instrcutions_Template = OrderedDict({
    "Domain_Experts" : PromptTemplate( input_variables=["SJTUYYDS"], template="你是{SJTUYYDS}专业人士，" ),
    "Basic_Info" : PromptTemplate( input_variables=["SJTUYYDS_1", "SJTUYYDS_2"], template="现有该领域{SJTUYYDS_1}文本，全面描述了{SJTUYYDS_2}信息。" ),
    "Requirements":{
        "Draft":OrderedDict({
            "Role" : FewShotPromptTemplate(
                    examples = list_example[0],
                    example_prompt = PromptTemplate(
                        input_variables=["已知角色类型", "补充角色类型"],
                        template='''
                        示例输入：{已知角色类型}
                        示例输出：{补充角色类型}
                        '''),
                    prefix = "请你根据给出的一组示例补充该领域主要的角色类型，用顿号分隔的形式返回\n",
                    suffix='''
                        已知角色类型：{input}
                        补充角色类型：''',
                    input_variables=["input"],
                    example_separator=" ",
                ),
            "Sub_Event" : FewShotPromptTemplate(
                    examples = list_example[1],
                    example_prompt = PromptTemplate(
                        input_variables=["已知事件类型", "补充事件类型"],
                        template='''
                        已知事件类型：{已知事件类型}
                        补充事件类型": {补充事件类型}
                        '''),
                    prefix = "请你根据给出的一组示例补充该领域主要的事件类型，用顿号分隔的形式返回\n",
                    suffix='''
                        已知事件类型：{input}
                        补充事件类型：''',
                    input_variables=["input"],
                    example_separator=" ",
                ),
            "Thing" :FewShotPromptTemplate(
                    examples = list_example[2],
                    example_prompt = PromptTemplate(
                        input_variables=["已知事物类型", "补充事件类型"],
                        template='''
                        已知事物类型：{已知事物类型}
                        补充事物类型": {补充事件类型}
                        '''),
                    prefix = "请你根据给出的一组示例补充该领域主要的事物类型，用顿号分隔的形式返回\n",
                    suffix='''
                        已知事物类型：{input}
                        补充事物类型：''',
                    input_variables=["input"],
                    example_separator=" ",
                ),
            "Relation" :FewShotPromptTemplate(
                    examples = list_example[3],
                    example_prompt = PromptTemplate(
                        input_variables=["已知关系类型", "补充关系类型"],
                        template='''
                        已知关系类型：{已知关系类型}
                        补充事物类型": {补充关系类型}
                        '''),
                    prefix = "请你根据给出的一组示例补充该领域主要的关系类型，用顿号分隔的形式返回\n",
                    suffix='''
                        已知关系类型：{input}
                        补充关系类型：''',
                    input_variables=["input"],
                    example_separator=" ",
                ),
            "Property" :  PromptTemplate(
                    input_variables=["SJTUYYDS_1", "SJTUYYDS_2"],
                    template='''
                            请你为该领域内的角色和事物已知的属性进行补充，列出其他的属性，用逗号分隔的形式返回。
                            对象：{SJTUYYDS_1}
                            已知属性：{SJTUYYDS_2}
                            格式指令：{format_instructions}
                            ''',
                )
        }),
        "Classification" : PromptTemplate(
                    input_variables=["SJTUYYDS_1", "SJTUYYDS_2"],
                    template='''
                            请你根据上下文，列出其他的属性，用逗号分隔的形式返回。
                            对象：{SJTUYYDS_1}
                            已知属性：{SJTUYYDS_2}
                            格式指令：{format_instructions}
                            '''"请判断{SJTUYYDS_1}属于{SJTUYYDS_2}中哪一类，只需从中选择一个选项输出即可，禁止输出其他信息。",
                )
    }  
})
