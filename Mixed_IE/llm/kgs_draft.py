import pickle
from typing import OrderedDict
import re

from config import _SEED, _FIELDS, _FIELDS_TYPE, _ROOT_PATH
from PromptTemplate import Instrcutions_Template

from api.baichuan_api import chat_baichuan as model_API
#（1）模板和专家知识
# 领域基类，
def Basic_Class():
    def __init__(self, Type):
        self.type = Type                           # _EVENT_TEMPLATE中的所有键名事件类型
        self.property_dict = {}                    # 类属性
    def modify(self, key, value):            # 自动添加、修改类属性的函数
        self.property_dict[key] = value

# 领域人类角色类
def Basic_Human_Class( Basic_Class ):
    def __init__(self, Type):
        super.__init__( Type )
        self.property_dict = {                          # 重写基类属性
            "name" : None,                              # 姓名
            "gender" : None,                            # 性别
            "ethnic" : None,                            # 民族
            "birth_day" : None,                         # 出生日期
            "registered_residence" : None,              # 户籍地
            "current_residence" : None,                 # 现居地
            "job":None
        }

# 领域组织角色类
def Basic_Orgnization_Class( Basic_Class ):
    def __init__(self, Type):
        super.__init__( Type )
        self.property_dict = {
            "name" : None,                              # 姓名
            "type" : None,                              # 政治、企业、非盈利
            "location" : None,                          # 所在地
        }

# 领域事物类
def Basic_Thing_Class( Basic_Class ):
    def __init__(self, Type):
        super.__init__( Type )
        self.property_dict = {
            "name" : None,                              # 姓名
            "owner" : None,                             # 所在地
        }

# 领域事件类
def Basic_Event_Class( Basic_Class ):
    def __init__(self, Type):
        super.__init__( Type )
        self.property_dict = {
            "name" : None,                              # 如借款
            "number" : None,                            # 同类型的事件发生第几次
            "parts" : [],                               # 当事人列表，后续可自定义主被动角色关系名
            "time" : None,                              # 事件发生事件
            "location" : None,                          # 事件发生地点
            "reason" : None,
        }


#（2）参考专家种子，利用大模型内部知识创建领域模型草图draft
# 核心是Prompt指令，架构为领域专家定位+领域文本基本情况+具体情况与需求+输出格式
#        https://blog.51cto.com/flydean/8674912



# 构建Prefix指令
def Basic_Instruction(_FIELDS, _FIELDS_TYPE, _SEED, template):
    ret = template
    if len(_FIELDS)==0:
        return ""
    ret["Domain_Experts"] = template["Domain_Experts"].format( SJTUYYDS= "的".join(_FIELDS))
    insert_ = "事件要素" if _FIELDS_TYPE == "Event-Oriented" else "对象属性"
    ret["Basic_Info"] = template["Basic_Info"].format( SJTUYYDS_1= _SEED["Test_Description"], SJTUYYDS_2=insert_)
    return ret

# 构建Draft指令
def Requirement_Draft_Instruction(_SEED, template_dicts, Prefix, _type):
    ret = []
    if _type=="Event-Oriented":
        for key in template_dicts:
            if key!="Property":
                if key!="Relation":
                    ret.append( (key, Prefix+template_dicts[key].format(SJTUYYDS= "、".join( list( _SEED[key]["dict"].keys())) ) ) )
                else:
                    ret.append( (key, Prefix+template_dicts[key].format(SJTUYYDS= f"{list( _SEED[key]['list'])}" ) ))
    else:
        if not _SEED["Role"]["Individual"]:
            ret.append( ("Role", Prefix+template_dicts["Role"].format(SJTUYYDS= "、".join( list(_SEED["Role"]["dict"].keys())) ) ) )
    return ret

# 大模型输出检查器
def format_checker(response, Instrcutions, role_type=None):
    if role_type==None:
        pattern = re.compile(f'\\[.+\\]')
        match = pattern.search(response)
        if not match:
            return None
        else:
            response = match.group(0).replace("，", ",").replace("\"", "").replace("“", "").replace("”", "")
            response = response[1:-1].split(",")
            return response
    else:
        if response not in role_type:
            format_error = 0
            while True:
                if format_error == 2:
                    print(f"下列指令无法指导大模型按照格式输出：{Instrcutions}")
                    return None
                format_error += 1
                response = model_API(Instrcutions+"请从给出的选项中进行选择并输出!!")
                if response not in role_type:
                    continue
                else:
                    return response
        else:
            return response

# 使用大模型扩充Seed中的类型
def KG_Draft_Class( _FIELDS, _FIELDS_TYPE, _SEED, instrcutions_template, _type):
    instrcutions_template = Basic_Instruction( _FIELDS, _FIELDS_TYPE, _SEED, instrcutions_template)     # 填充prefix
    Prefix = instrcutions_template["Domain_Experts"] + instrcutions_template["Basic_Info"]
    Instrcutions = Requirement_Draft_Instruction(_SEED, instrcutions_template["Requirements"]["Draft"], Prefix, _type)   # 获取第一阶段的提示词列表
    for i in range( len(Instrcutions) ):
        key = Instrcutions[i][0]
        task = Instrcutions[i][1]
        response = model_API( task )
        response = format_checker(response, Instrcutions)
        if response!=None and _SEED[key]["Scalable"] == True:
            for item in response:
                SEED[key]["dict"][item] = None
    return _SEED

# 使用大模型填充类的属性
def KG_Draft_Class_Property( instrcutions_template, seed, _type):
    if _type!="Event-Oriented":
        return None
    else:
        role_type = ["组织", "个人"]
        def role_judger( inputs, role_type):
            task = instrcutions_template["Requirements"]["Classification"].replace("<Input>", inputs).replace("<Types>", f"{role_type}")
            ret = model_API(task)
            ret = format_checker(ret, task, role_type )
            return ret
        for key in seed["Sub_Event"]["dict"]:
            seed["Sub_Event"]["dict"][key] = Basic_Event_Class("Sub_Event")
        for key in seed["Role"]["dict"]:
            if role_judger( key, role_type)==role_type[0]:
                seed["Role"]["dict"][key] = Basic_Human_Class(on_key)
            else:
                seed["Role"]["dict"][key] = Basic_Orgnization_Class(on_key)
        for key in seed["Thing"]["dict"]:
            seed["Thing"]["dict"][key] = Basic_Thing_Class("Thing")

        
        for i, key in ["Sub_Event", "Role" , "Thing"]:
            names = ["事件类型", "核心角色类型", "二级角色类型", "事物类型" ]
            key_name = names[i]
            for sub_key in seed[key]["dict"]:
                class_ins = seed[key]["dict"][sub_key]
                class_name = key_name+"中的"+sub_key
                property_instruction = Instrcutions_Template["Requirements"]["Property"].replace("<SJTUYYDS_1>", class_name).replace("<SJTUYYDS_2>", f"{list(class_ins.property_dict.keys())}")
                response = model_API(property_instruction)
                response = format_checker(response, property_instruction)
                if response!=None:
                    for new_pro in response:
                        class_ins.modify(new_pro, None)
        return seed

def main(_type="Event-Oriented"):
    seed = KG_Draft_Class( _FIELDS, _FIELDS_TYPE, _SEED, Instrcutions_Template,  _type)
    seed = KG_Draft_Class_Property( Instrcutions_Template, seed,  _type)
    with open('seed.pkl', 'wb') as f:  
        pickle.dump(seed, f)  
    return seed

if __name__ == "__main__":
    seed = main()
    print(seed)