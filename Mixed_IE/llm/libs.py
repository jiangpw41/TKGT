'''
大模型生成知识图谱类的质量评估方法（知识图谱的类而非实例）
1.基于辅助人类构建领域知识图谱这一目的，而非直接生成领域知识图谱
2.指定得分标准，人类进行评价
3.评分标准如下：
（1）角色数量及其关系完备度：当数据集较为简单时，人类先验知识就已经可以完备抽取，则不进行评分
（2）角色/关系属性完备度：对目标数据集由人指定字段集合，遍历生成的字段逐个与目标字段进行匹配，总分为1，所有字段平分得分（也可根据重要性）
    完全匹配Totally Match：生成的字段中有至少一个字段和目标中的某个字段在形式或语义上完全匹配，则获得该目标字段的总分。但只有一个计分。
    包含匹配Including：生成的字段中有至少一个是目标字段中某个或某些字段的邻近父概念（邻近指可以通过后续原文信息自然推断出子概念），则获得所有目标字段之和的75%
    被包含匹配Included：生成的字段中至少一个是某个目标字段的子概念。若父概念有限可分，则获得字段分数/类别数（如目标字段是双亲，预测父亲，则获得1/2的分数，不同的子概念可叠加，如预测除了父亲和母亲，则获得全部）；若父概念不可分，则获得25%
    不匹配Not Match：预测字段中没有和目标字段相关的，如汽车和狗。
在预测的字段中找目标字段的匹配结果，累计得分

'''


from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
import os
import sys
import json

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate

_ROOT_PATH = "/home/jiangpeiwen2/jiangpeiwen2/text-kgs-table/"
_DATA_PATH = os.path.join(_ROOT_PATH, "components/mix_ie/further_processed/statistic")
data_list = [ "e2e", "rotowire","wikitabletext", "CPL", "wikibio"]

# 角色属性提取
role_info_extra_prompt = PromptTemplate(
    input_variables=["ROLE", "DESC", "WORDS"],
    template="""
        You are a useful assistant on Knowledge Graph, you need to infer the property of roles given by users, user will provide a description and a set of high-frequency words about this roles.
        1. You will be clearly informed of the role type and its description by users, and there is only one entity.
        2. You need to determine the role's attributes such as name, birthday; 
        3. Respond to the user's question like the examples provided below:

        Role type: City
        Decription: A basic introduction of a city including various aspects
        High-frequency Words: ['name', 'located', 'mayor', 'people', 'industry', 'culture', 'GDP', 'history']
        Request: Please list the property of this given role type.
        Response : Name, Population, Area, Mayor, Location, GDP, Historical Evolution, Major Airports, Traffic Congestion, Education Level

        Role type: Artist
        Decription: A rough introduction of an artist about his whole life.
        High-frequency Words: ['name', 'talent', 'artwork', 'style', 'exhibition', 'inspiration', 'gallery', 'award', 'museum', 'legacy']
        Request: Please list the property of this given role type.
        Response: Name, Talent Area, Artistic Style, Signature Artwork, Major Exhibitions, Inspirations, Representation Gallery, Awards Won, Museums Displaying Work, Artistic Legacy
        
        Role type: Chef
        Decription: Some information about a chef and his/her job.
        High-frequency Words: ['name', 'restaurant', 'cuisine', 'recipe', 'ingredients', 'flavor', 'menu', 'award', 'culinary', 'experience']
        Request: Please list the property of this given role type.
        Response: Name, Restaurant Name, Specialty Cuisine, Signature Recipe, Key Ingredients, Flavor Profile, Menu Offerings, Culinary Awards, Years of Experience, Unique Culinary Skills.
        
        Below is the usr's question: 

        Role type: {ROLE}
        Decription: {DESC}
        High-frequency Words: {WORDS}
        Request: Please list the property of this given role type.
        Response:
    """
)


# 角色补充
role_types_extra_prompts = PromptTemplate(
    input_variables=["EVENT", "DESC","ROLES_KNOW", "WORDS"],
    template="""
        You are a useful assistant on Knowledge Graph, you need to infer the roles types and their relation of an event given by users, user will provide a set of high-frequency words about this event.
        1. You will be clearly informed of the event type and short description by users, and you cannot deviate from this domain.
        2. The provided high-frequency words may not complete, you may need to infer the event's roles type and relations.
        3. User may provide some roles he/she already know or not, you should response based on the given roles if there are.
        4. Respond to the user's question like the examples provided below:

        Event: War
        Description: Elements about a human war event
        Already known roles: ['Neutral States', 'Belligerent State', ]
        High-frequency Words: ['Time', 'Location', 'Belligerent', 'Alliance', 'Faction', 'Politics', 'Economy', 'Society', 'Territorial Dispute' ,'Resource Competition', 'Battle', 'Campaign']
        Request: Please list other roles highly related with this event and known roles.
        Response: Alliance, Faction, General, Soldier

        Event: Wedding
        Description: Elements about a wedding
        Already known roles: ['Bride', 'Groom' ]
        High-frequency Words: ['Wedding', 'Family', 'Bride', 'Groom', 'Tuxedo', 'Dress', 'Love', 'Joy', 'Ceremony' ,'Vows', 'Kiss', 'Cake']
        Request: Please list other roles highly related with this event and known roles.
        Response: Bridesmaids, Groomsmen, Flower Girl, Ring Bearer, Parents, Officiant

        Event: Birthday Party
        Description: Elements about a Birthday Party
        Already known roles: ['Birthday Person']
        High-frequency Words: ['Birthday', 'Party', 'Cake', 'Friends', 'Family', 'Gifts', 'Fun', 'Celebration', 'Decorations', 'Invitations', 'Guests']
        Request: Please list other roles highly related with this event and known roles.
        Response: Host, Party Guests, Gift Givers, Party Planner, Entertainers, Decorator, Photographer

        Below is the usr's question:

        Event: {EVENT} 
        Description: {DESC}
        Already known roles: {ROLES_KNOW}
        High-frequency Words: {WORDS}
        Request: Please list other roles highly related with this event and known roles.
        Response:
    """
)


# 事件提取
event_role_relation_request = PromptTemplate(
  input_variables=["EVENT", "DESCRIPTION", "KONWN_ROLES", "WORDS"],
  template="""
      You are an expert in Event Modeling for Knowledge Graphs. Your task is to extract relevant roles and their relationships from a given event description.
      1. You will be provided with an event type and a brief description of the event and a set of high-frequency words about this events.
      2. Based on the event description and high-frequency words, you need to identify the key roles involved and their relationships with each other.  
      3. Respond to the user's question in a structured manner of triplet, outlining the roles and their relationships.  
      4. Respond to the user's question like the examples provided below:

      Event Type: Birthday Party  
      Event Description: A gathering of friends and family to celebrate the birthday of a special person. There is usually a cake, gifts, and fun activities.  
      Already known roles : Birthday Person, Host, Party Guests, Gift Givers, Party Planner, Entertainers, Decorator, Photographer
      High-frequency Words: ['Wedding', 'Family', 'Bride', 'Groom', 'Tuxedo', 'Dress', 'Love', 'Joy', 'Ceremony' ,'Vows', 'Kiss', 'Cake']
      Request: Please list the relevant roles and their relationships for this event type.  

      Response:  
      Roles: 
      - Birthday Person: The person whose birthday is being celebrated.  
      - Host: The person or persons organizing the party.  
      - Guests: The invited friends and family members.  

      Relationships:  
      - ( Host, organizes the party for, the Birthday Person ).  
      - ( Guests, attend, the party).
      - ( Guests, celebrate the birthday of, Birthday Person) .  
      - ( Guests, bring Gifts for, the Birthday Person).  

      Below is the user's question for a new event:
      Event Type: {EVENT}
      Event Description: {DESCRIPTION}
      Already known roles : {KONWN_ROLES}
      High-frequency Words: {WORDS}
      Request: Please list the relevant roles and their relationships for this event type.
      Response:
  """
)


# KGs构建
Entity_KGs_construction_request = PromptTemplate(
  input_variables=["TYPE", "DESCRIPTION", "INFORMATION"],
  template="""
    You are an expert of Knowledge Graphs (KGs). Your task is to construct a Knowledge Graphs based on related information provided by the user, 
    1. This task only contains Single Role, you only need to list all useful attributes of the role, you should response with Python class definition.
    2. User will provide information available for reference, they may be structured or non-structure, containing roles types, known attributes.  
    3. Respond to the user's question like the examples provided below:

    Object Type: a City
    Description: Basic information about a city.
    Available Information: 'Name, Population, Area, Mayor, Location, GDP, Historical Evolution, Major Airports, Traffic Congestion, Education Level'
    Request: Please construct a knowledge graph of above object.  
    Response: 
        class City:
            self.Name = None,
            self.Country = None
            self.Population = None,
            self.Area = None,
            self.Mayor = None,
            self.Location = None,
            self.GDP = None,
            self.Historical_Evolution = None,
            self.Well-Known_Figures = None

    Below is the user's request for a new role type:
    Object Type: {TYPE}
    Description: {DESCRIPTION}
    Available Information: {INFORMATION}
    Request: Please construct a knowledge graph as a python class format for above object.
    Response:
  """
)


# 词频统计结果加载
def read_hot_words( index, part=100):
    # [ "e2e", "rotowire","wikitabletext", "CPL", "wikibio"]
    dataset_path = os.path.join(_DATA_PATH, data_list[index])
    with open( os.path.join(dataset_path, "freq_all.json"), "r" ) as file:
            data_freq = json.load(file)
    if '_Overview' in data_freq:
        data_freq_overview = data_freq['_Overview']
        print( data_freq_overview )
        '''
        {'Total words': 1152364,
        'Lines': 51426,
        'Average_words_Line': 22.408198187687162,
        'Total words after filter': 565068}
        '''
    else:
        data_freq = data_freq['TT_freq']
    data_freq_lens = len(data_freq) - 1           # 2579
    limitation = data_freq_lens//part   # 25
    count = 0
    reference_list = []
    for i, key in enumerate(data_freq, start=0):
        if key!="_Overview":
            if count < limitation:
                count += 1
                reference_list.append(key)
    return reference_list


# NVIDIA OpenSource API
from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "xxx"
)


def chat_LLM( inputs ):
    completion = client.chat.completions.create(
    model="meta/llama3-70b-instruct",
    messages=[{"role":"user","content":inputs}],
    temperature=0,
    #top_p=1,
    max_tokens=1024,
    stream=True
    )

    responses = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            responses += chunk.choices[0].delta.content
    print( responses )
    return responses


def Role_Info_Extra( _role = 'Restaurant', _words_freq = None):
    inputs = role_info_extra_prompt.format(ROLE = _role, WORDS = _words_freq)
    #_role_model = LLMs( model_name = 'gpt-4-turbo', device=None, client=client)     # 用于提取角色
    #_role_candidates = _role_model.generate_gpt4( inputs )
    responses = chat_LLM(inputs)
    print( responses )
    return responses


def Role_Type_Completion( _event = 'Basketball Game', _role_know = "Team"  , _words_freq = None):
    inputs = role_types_extra_prompts.format(EVENT = _event, ROLES_KNOW = _role_know, WORDS = _words_freq)
    responses = chat_LLM(inputs)
    print( responses )
    return responses

def Event_Modeling( _event, _description, _role_know, _words_freq):
    inputs = event_role_relation_request.format(EVENT = _event, DESCRIPTION = _description, KONWN_ROLES = _role_know, WORDS = _words_freq)
    responses = chat_LLM(inputs)
    print( responses )
    return responses