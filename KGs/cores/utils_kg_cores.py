import os
import sys


_ROOT_PATH = os.path.abspath(__file__)
for i in range(3):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert(0, _ROOT_PATH)
from data.data_manager import DataManager
from data.load_ruled_texts import _ruled_load

from KGs.get_empty_kg_by_name import return_kg, prompt_templates, config_data

class PromptConstructor():
    """提示词构建接口
    只根据args和提示词类型返回提示词
    """
    def __init__(self, temp_kg, type, mode):
        self.type = type            # 类型SingleEntity, FirstColumn, DataCell
        self.mode = mode
        self.kg = temp_kg           # 空初始化，或用标签，用FirstColumn推理结果，三者之一初始化完毕的知识图谱

    def get_prompt_list(self, HybirdRAG_for_Context, iterator, **configs):
        prompt_list = []
        # 对于FirstColumn，只需要回答哪些Entity类型有哪些实例
        if self.type == "FirstColumn":
            entity_list = list( self.kg.entity_type_info.keys() )
            for entity in entity_list:
                if self.mode == "train":
                    answer = self.kg.get_objects( entity )              # 如果是构建训练数据对，则output由get_objects函数产生：
                else:
                    answer = None                                       # 如果是进行测试，不需要output，直接有生成好的tuple标签集合
                target_attr = "Name" if self.kg.language=="EN" else "姓名名称"
                scopes = "<class 'str'>"
                configs["predicate"] = self.kg.entity_type_info[entity]["predicate"]
                configs["entity_type"] = entity
                # 构建提示词
                prompt = self.get_prompt(HybirdRAG_for_Context, target_attr, scopes, answer, **configs )

                prompt_list.append( prompt )
        # 对于DataCell，需要遍历不同Entity的属性
        else:
            while True:                             
                try:
                    target_attr, scopes, answer = next(iterator)
                    
                    prompt = self.get_prompt(HybirdRAG_for_Context, target_attr, scopes, answer, **configs )
                except StopIteration:  
                    # 当没有更多元素时，退出循环  
                    break
                prompt_list.append( prompt )
        return prompt_list
    
    def get_prompt(self, HybirdRAG_for_Context, target_attr, scopes, answer, **configs):
        instruction = self.get_instruction( **configs)
        context = HybirdRAG_for_Context( configs["entity_type"], target_attr, **configs )
        example = self.get_example( context, target_attr, scopes, **configs)
        # 不同目的的prompt数据不一样
        if self.mode == "train":
            prompt = {
                "instruction": instruction,
                "input": example,
                "output": answer if answer!=None else "<NOT FOUND>"
            }
        else:
            prompt = instruction + "/n" + example
        return prompt
    
    def get_instruction(self, **args):
        if self.type == "SingleEntity":
            return args["prompt_temp"]["Instruction"].format( FIELD = args["field"], ROLE = args["entity_type"])
        elif self.type == "FirstColumn":
            return args["prompt_temp"]["Instruction"].format( FIELD = args["field"], ALL_ROLES = args["entity_list"] )
        elif self.type == "DataCell":
            return args["prompt_temp"]["Instruction"].format( FIELD = args["field"], EXTRACTED = args["extracted"] )

    def get_example(self, context, target_attr, scopes, **args):
        if self.type == "SingleEntity":
            return args["prompt_temp"]["Example"].format( ROLE= args["entity_type"], 
                                                CONTEXT = context, 
                                                ATTRIBUTE = target_attr, 
                                                SCOPE = scopes, 
                                                )
        elif self.type == "FirstColumn":
            return args["prompt_temp"]["Example"].format( ROLE=args["entity_type"], CONTEXT=context)
        elif self.type == "DataCell":
            if args[ "language" ]=="ZH":
                return args["prompt_temp"]["Example"].format( ROLE = args["entity_type_with_name"], 
                                                        CONTEXT = context, 
                                                        ATTRIBUTE = target_attr, 
                                                        SCOPE = scopes, 
                                                        PREDICATE = args["predicate"]
                                                        )
            else:
                return args["prompt_temp"]["Example"].format( ROLE = args["entity_type_with_name"], 
                                                        CONTEXT = context, 
                                                        ATTRIBUTE = target_attr, 
                                                        SCOPE = scopes, 
                                                        )

def get_tables_list( datas, part_name = None, subtable_name=None ):
    """
    datas: table部分数据，元组，以列表或字典形式组织
    part_name: 第一次指的是FirstColumn或DataCell
    subtable_name: 子表名称
    不管读取的tables是什么格式的，只返回列表格式
    """
    if isinstance( datas, list ):
        return datas
    elif isinstance( datas, dict ):
        if part_name==None:
            raise Exception( f"请指定任务目标：{datas.keys()}")
        part_table = datas[part_name]
        return get_tables_list( part_table, subtable_name, None)

def load_shared( dataset_name, mode, subtable_name=None, only_data=False):
    """
    dataset_name: 数据集名称，如cpl, rotowire, e2e，用于加载对应的数据、配置、知识图谱
    mode: train或test，用于加载不同的数据
    subtable_name: 默认为None，当非None时，表示数据集内部分为多个独立的子表，需要特别指定哪个子表
    """
    # 加载数据
    data_manager = DataManager( dataset_name, mode )
    datas = data_manager.main()
    if only_data:
        return datas
    # 加载ruled_text
    ruled_texts = _ruled_load( dataset_name, mode, subtable_name )
    # 加载配置
    configs = config_data["DATASET_MANAGE"][dataset_name]
    configs["prompt_temps"] = prompt_templates[configs[ "language" ]]
    # 加载KG
    kg = return_kg( dataset_name, subtable_name )

    return kg, datas, ruled_texts, configs