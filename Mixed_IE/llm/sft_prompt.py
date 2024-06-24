'''
所有数据集中的提取都可以分为：角色提取、字段值提取。前者是后者前提
（1）角色提取：基于前期对每个数据集IE处理结果得到的专属名词列表"NNP"（角色名大概率存在于专属名词中），路径text-kgs-table/components/mix_ie/further_processed/statistic/{e2e}/{test}_filter.json。
    遍历每个专属名词，RAG获取其相关原文，结合KGs中定义的角色取值范围，让大模型推断每个专属名词是否是角色名，以及属于哪个角色。KGs中对每张表中每个角色（行）的数量有规定，Row_Name角色类型：-1为任意（可以0和多个），0表示至少一个，>0为准确数
    最终返回一个列表字典，每个角色类型有一个实例列表
（2）字段值提取：遍历每个字段值、每个角色，根据RAG获得的原始段落、预定义的字段值范围/类型，提取知识。
    提取结果以字典形式（结构见text-kgs-table/components/kgs/dataset_kgs/xxx_filed.py）
    最后通过特定于表格和KGs的映射逻辑转换为xlsx
为了快速构建SFT数据集，从各数据集的表格出发，将相应的值提取填入下列两个模板即可。
'''


import json

from components.kgs.dataset_kgs.e2e_rotowire_field import fields_list_rotowire, fields_list_e2e
from components.kgs.dataset_kgs.CPL_field import fields_list_CPL

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from componets.models.LLM import *

openai_key_dict = {
    0:'sk-kHSJWmX805GX4IXr5326123c978d4b39978f67Fa4b09080f',
    1:'sk-M6oGLVzTjmsSyNJN2d20E549Da1448A08b7aF2259623BcC1',
    2:'sk-NlGLUqlHiEQn6hhZ179eE38a947f4eE7Ae69EbB1C119Ed9c',
    3:'sk-5tRECZ3r52wUXbRk03AaD9C7F4F7408eBb02B8E65918B518',
    4:'sk-kBmzsmV6P6PJEmzT0871D41d6d844a6d913012A500Cb2a47',
    5:'sk-QKCK06d9xHOMSfDf3577Ff32272f49689b0f41C9B1553c3d',
    6:'sk-LDci0nn1IQ2oxDCADf164e2fC58b4d1d8687155aC3Fa4207',
    7:'sk-S8p5An0ADCW2bTDl2131D5D7193043999cB1F041A516E94f',
    8:'sk-xQjENQbjjyfZqF4CE8Ac4b2f1bAc46C4907a816d55C3E5D0',
    9:'sk-vHcTowCmsDraQ8LF6753Ad7800694d5cA6Ef7278E057Ae60',
    10:'sk-rA6j2oV3V94iYaB4EfC6C92e1aB24a9497724b6079723c88',
}

openai_key = openai_key_dict[0]
client = OpenAI(
    api_key = openai_key,
    base_url="https://www.gptapi.us/v1/chat/completions",
    http_client = httpx.Client(proxies={
        "http://": "http://127.0.0.1:7890",
        "https://": "http://127.0.0.1:7890",
    }),
)


# 角色提取：对每篇文档，对预处理获得的专有名词列表进行遍历，根据RAG获得的专有名词相关段落，检查其是否属于该文档所属数据集领域中预定义的角色。
role_extra_prompt = """
    You are a useful assistant who can classify given proper nouns based on the list of role options and related information provided by the user.
    1. Determine whether this proper noun belongs to any of the given role lists. If it does not belong to any of them, respond 'Not Role'.
    2. If it belongs to a certain role in the role list, you only need to respond the options in the list. You cannot output any content not in the role list.
    3. Respond to the user's question like the examples provided below:

    Proper noun: Hawks
    Related Context: The Atlanta Hawks (46 - 12) beat the Orlando Magic (19 - 41) 95 - 88 on Friday. Al Horford had a good all - around game, putting up 17 points, 13 rebounds.
    Role option scope: ['Team']
    Question: Dose the proper noun is a Role in the scope? If dose, which is?
    Answer: Team

    Proper noun: Vaults
    Related Context: The Vaults pub near Café Adriatic has a 5 star rating.  Prices start at £30.
    Role option scope: ['Restaurant']
    Question: Dose the proper noun is a Role in the scope? If dose, which is?
    Answer: Restaurant

    Proper noun: Blue
    Related Context: Close to Café Brazil, The Cambridge Blue pub serves delicious Tuscan Beef for the cheap price of £10.50. Delicious Pub food.
    Role option scope: ['Team', 'Player']
    Question: Dose the proper noun is a Role in the scope? If dose, which is?
    Answer: Not Role

    Below is the usr's question: 
"""

role_extra_request = PromptTemplate(
    input_variables=["PRNON", "RELATED_CONTEXT", "SCOP"],
    template="""
        Proper noun: {PRNON}
        Related Context: {RELATED_CONTEXT}
        Role option scope: {SCOP}
        Answer:
    """
)

# 键值提取：对每个字段，对每个角色，根据RAG获得的相关原文段落，提取该字段（列）、该角色（行）的表格值。
kv_extra_prompt = """
    You are a useful table content filling assistant that can extract the attribute field values of the role based on the row and column values provided by the user, as well as their corresponding paragraph original text, from the original text.
    1. Check if the provided paragraph contains the attribute values corresponding to the role. If not, respond 'Bad Infomation'.
    2. If the relevant paragraph contains attribute values for the role, respond the value according to the given requirements.
    3. Respond to the user's question like the examples provided below:

    Role: Taste of Cambridge
    Attribute: Price range
    Related Context: Taste of Cambridge is a restaurant with a customer rating of 3 out of 5 and and a price range of £20-£25
    Value scope: ['More than £30', 'Cheap', 'Less than £20', '£20-25', 'Moderate', 'High']
    Question: What's the value of Taste of Cambridge's Price range?
    Answer: £20-£25

    Role: Zizzi
    Attribute: Food
    Related Context: A pub named Zizzi has a customer rating of 3 out of 5, serves French cuisine, and is kid friendly.
    Value scope: ['Japanese', 'French', 'English', 'Fast food', 'Italian', 'Indian', 'Chinese']
    Question: What's the value of Zizzi's Food?
    Answer: French

    Role: James Harden
    Attribute: Points
    Related Context: It was another day at work on Tuesday for superstar James Harden, who led the Rockets to a blowout victory with 34 points and 11 assists.
    Value scope: integer
    Question: What's the value of Player's Points?
    Answer: 34

    Role: Suns
    Attribute: Number of team assists
    Related Context: Memphis also registered 25 assists compared to only 13 - on 32 field goals - for the Suns
    Value scope: integer
    Question: What's the value of Suns's Number of team assists?
    Answer: 13

    Below is the usr's question:
"""

kv_extra_request = PromptTemplate(
    input_variables=["ROLE", "FIELD", "RELATED_CONTEXT", "SCOPE"],
    template="""
        Role: {ROLE}
        Attribute: {FIELD}
        Related Context: {RELATED_CONTEXT}
        Value scope: {SCOPE}
        Question: What's the value of {ROLE}'s {FIELD}?
        Answer:
    """
)




# 遍历专有名词，分配给相应角色
def extra_roles( _scop,  _PRNON_list, model):
    ret = {
        key:[] for key in role_dict.keys()
    }
    for word in _PRNON_list:
        '''
        这里需要补充RAG逻辑
        related_info = 
        '''
        
        result = model.generate( role_extra_request.format(PRNON=word, RELATED_CONTEXT=related_info, SCOP=_scop) )
        if result in _scop:
            ret[result].append( word )
    return ret


def extra_main(field_list:dict, text_filter:dict):
    '''
    param: field_list                # the given structure of fields and value range belonging to a certain dataset
    param: text_filter               # a list of results of one doc's pos_tag from preprocessed file (example path /home/jiangpeiwen2/jiangpeiwen2/text-kgs-table/components/mix_ie/further_processed/statistic/e2e/test_filter.json)
    '''
    _role_model = LLM(model_name = 'gpt-3.5-turbo', device=None, client=client, sys_prompt=role_extra_prompt )     # 用于提取角色
    _value_model = LLM(model_name = 'gpt-3.5-turbo', device=None, client=client, sys_prompt=kv_extra_prompt )      # 用于提取字段值
    _answer = {}

    for table in field_list.keys():
        _answer[table] = {}                 # the container to store value in table
        _SCOP = list( field_list[table]["Row_Name"].keys() )
        _top_level_fields_list = list( field_list[table]["Fields"].keys() )

        # Get roles:
        _PRNON_list = [ text_filter["NNP"][i][0] for i in range(len(text_filter["NNP"]))]
        role_candidates = extra_roles( _SCOP,  _PRNON_list, _role_model)
        for role in role_candidates:
            _type = field_list[table]["Row_Name"][role]        # Row_Name角色类型：-1为任意（可以0和多个），0表示至少一个，>0为准确数
            _lens = len( role_candidates[role] )
            flag = 0
            if _type==0 and _lens=0:
                flag = 1
            elif _type>0 and _type != _lens:
                flag = 1
            if flag==1:
                '''
                这里可以插入更稳定的复查逻辑
                '''
                return "ROLE NUMBER ERROR"
            else:
                continue
        
        # Fill table
        for field in _top_level_fields_list:
            for role in role_candidates:
                '''
                这里需要补充RAG逻辑
                related_info = 
                '''
                _input = kv_extra_request.format(ROLE=role, FIELD=field, RELATED_CONTEXT=related_info, SCOPE= field_list[table]["Fields"][field])
                _answer[table][role][field] = _value_model.generate( _input )
                '''
                CPL除了一级字段外，还有二级字段，待补充逻辑
                '''

        return _answer

def main():
    '''
    对每一份文档，调用上述extra_main逻辑，获得该文档表格对应的字典
    调用特定于表格的parser将字典转换为xlsx表格，进行存储和评估
    '''


if __name__=="__main__":
    main()