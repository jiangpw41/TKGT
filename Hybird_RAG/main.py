
import os
import sys
import yaml
import importlib
import json
import pickle
from tqdm import tqdm

_SPLITE = True

_ROOT_PATH = os.path.abspath(__file__)
for i in range(2):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert(0, _ROOT_PATH)
from KGs.get_empty_kg_by_name import return_kg, prompt_templates, config_data
from data.data_manager import DataManager
from Hybird_RAG.retriever.Retriver import HybirdRAG_for_Context
from utils import load_data, save_data
from copy import deepcopy

def load_shared( dataset_name, part ):
    """
    part: train或test
    """
    args = {}
    # 加载数据
    data_manager = DataManager( dataset_name, part )
    datas = data_manager.main()
    # 加载配置
    config = config_data["DATASET_MANAGE"][dataset_name]
    args[ "language" ] = config["language"]
    args[ "prompt_temps" ] = prompt_templates[args[ "language" ]]
    args[ "field" ] = config["field"]
    args[ "extracted" ] = config["extracted"]
    # 加载KG
    kg = return_kg( dataset_name )


    return kg, datas, args




# def get_prompt_


def construct_prompt( 
        entity_target,          # 模板实体
        target_attr,
        prompt_temp,            # 提示词模板
        text,                   # 本文档的字符串，用于context
        scopes,                 # 目标属性的取值范围信息
        entity_list=None,            # 本知识图谱的实体类型列表
        training_answer=None,   # 是否是训练Alpache格式，如果给了answer，说明要用在Alpache中
        **args                  # config中的一些配置，如extracted，predicate, field
    ):
    first_column = args["first_column"]          # 是否是提取entity名
    if "<SPLIT>" in entity_target:
        splits = entity_target.split("<SPLIT>")
        entity_target = splits[0]+f"({splits[1]})"
    field = args["field"]
    if first_column:
        instruction = prompt_temp["Instruction"].format( FIELD=field, ALL_ROLES=entity_list)
        context = HybirdRAG_for_Context( entity_target, target_attr, text)                    # 角色类型，属性
        example = prompt_temp["Example"].format( ROLE=entity_target, CONTEXT=context)
    else:
        if args["multi_entity"]==False and target_attr in ["Name", "姓名名称"]:
            entity_target = entity_target.split("(")[0]
        instruction = prompt_temp["Instruction"].format( FIELD=field, EXTRACTED=args["extracted"])
        context = HybirdRAG_for_Context( entity_target, target_attr,  text, )
        if args[ "language" ]=="ZH":
            example = prompt_temp["Example"].format( ROLE=entity_target, 
                                                    CONTEXT=context, 
                                                    ATTRIBUTE=target_attr, 
                                                    SCOPE=str(scopes), 
                                                    PREDICATE=args["predicate"]
                                                    )
        else:
            example = prompt_temp["Example"].format( ROLE=entity_target, 
                                                    CONTEXT=context, 
                                                    ATTRIBUTE=target_attr, 
                                                    SCOPE=str(scopes), 
                                                    )
    if training_answer!=None:
        prompt = {
            "instruction": instruction,
            "input": example,
            "output": training_answer
        }
    else:
        prompt = instruction + "//n" + example

    return prompt


# 对一篇文章进行实体抽取
def GetFirstColumnPrompt( 
        kg,                 # 空的知识图谱实例
        text,               # 文本
        prompt_temp,        # 提示词模板
        mode,
        **args              # config中的一些配置，如extracted，predicate, field, language等
    ):
    """
    获取这个知识图谱FirstColumn部分的提示词，两种情况
    （1）train模式：知识图谱已经通过真实的label add了不同的实体，通过kg.instance_num[entity]可以获得各个实体下对象的id列表
        此时遍历kg.entity_type_info中的实体键，获取该实体的所有Name，构建成逗号分隔的字符串形式，否则获取<NOT FOUND>
    （2）test和Application模式：空知识图谱，仅遍历kg.entity_type_info中的实体键构建prompt，没有answer
    """
    target_attr = "Name"
    entity_info = kg.entity_type_info
    entity_list = list( entity_info.keys() )

    ret_list = []
    for entity in entity_list:
        # 如果为train模式，知识图谱中已add实体
        if mode == "train":
            entity_answer = kg.get_objects( entity )
        # 否则，没有实体信息
        else:
            entity_answer = None
        scopes = "str"
        first_column = True
        args["predicate"] = entity_info[entity]["predicate"]
        prompt = construct_prompt( entity, target_attr, prompt_temp, text, scopes, entity_list,
                                    training_answer=entity_answer, **args )
        ret_list.append( prompt )
    return ret_list

# 对一篇文章进行属性关系抽取，基于上面
def GetDataCellPrompt( 
        kg,                 # 空的知识图谱实例
        text,               # 文本
        prompt_temp,        # 提示词模板
        mode,
        **args              # config中的一些配置，如extracted，predicate, field
    ):
    """
    获取这个知识图谱DataCell部分的提示词，由于非train模式必须两阶段分开，因此只有一种情况
        知识图谱已经通过真实的label add了不同的实体，通过kg.instance_num[entity]可以获得各个实体下对象的id列表
        此时遍历kg.entity_type_info中的属性类型定义字典中的实体，获取该实体的所有属性，同时遍历该实体下的对象，如果存在该属性则获取值作为answer，否则获取<NOT FOUND>
    """
    first_column = False
    entity_list = None
    entity_info_all = kg.entity_type_info
    ret_list = []
    name_ = "Name" if args["language"]=="EN" else "姓名名称"
    for entity in list( entity_info_all.keys() ):           # 遍历实体类型
        entity_num_list = kg.instance_num[entity]               # 类型对应的实例列表，为[]表示预测的 or 实际上这个文档中该类型不存在实例
        temp_prompt = []
        for entity_num in entity_num_list:                  # 遍历类型中每个实例对象
            object_info =  kg.get_info( query=entity_num, single=True, node=True)
            name = object_info[name_]["value"]
            target_entity = entity + "<SPLIT>" + name if name!= None else entity
            iterator = kg.get_attr_iter( entity_num )       # 迭代器，迭代获取一个对象的理论完备标签、真实标签、取值范围
            while True:                             
                try:
                    target_attr, scopes, answer = next(iterator)
                    if args["multi_entity"] and target_attr in ["Name", "姓名名称"]:        # 多实体在DataCell时Name作为已知
                        continue
                    if mode != "train":
                        answer = None
                    args["predicate"] = entity_info_all[entity]["predicate"]
                    prompt = construct_prompt( target_entity, target_attr, prompt_temp, text, scopes, entity_list,
                                        training_answer=answer, **args )
                    temp_prompt.append( prompt )
                except StopIteration:  
                    # 当没有更多元素时，退出循环  
                    break
        if mode=="train":
            ret_list.extend( temp_prompt )
        else:
            ret_list.extend( temp_prompt )
    return ret_list

# 展平输入table为一层的字典
def table_flatten( datas, length ):
    """
    texts：长度等于样本数的字符串列表
    datas：内容为二元组或三元组，可能有三种形式：
        1. 元组列表，长度与texts相等，代表单实体表格
        2. 单层字典列表，分为FirstColumn和DataCell两个键，值都是长度与texts相等的元组列表，与多实体、单表对应
        3. 多层字典列表，分为FirstColumn和DataCell两个键，前者与前面一样，后者有多个自定义的子表名为键，值为长度与texts相等的元组列表
    """
    table_flatten = {}
    for i in range( length ):
        if isinstance( datas, list ):                                       # 最简单的单实体表
            if i == 0:
                table_flatten["SingleEntity"] = []
            table_flatten["SingleEntity"].append( datas[i] )
        elif isinstance( datas, dict ) and "FirstColumn" in datas.keys():   # 常用的
            if i == 0:                                                         # 实体表部分
                table_flatten["FirstColumn"] = []
            table_flatten["FirstColumn"].append( datas["FirstColumn"][i] )

            if isinstance( datas["DataCell"], list ):                          # 属性关系部分，如果也是列表，那就和实体表一样；如果不是，就遍历所有子表
                if i == 0:
                    table_flatten["DataCell"] = []
                table_flatten["DataCell"].append( datas["DataCell"][i] )
            elif isinstance( datas["DataCell"], dict ):
                sub_keys = list( datas["DataCell"].keys() )
                for sub_key in sub_keys:
                    if i == 0:
                        table_flatten[f"DataCell<SPLIT>{sub_key}"] = []
                    table_flatten[f"DataCell<SPLIT>{sub_key}"].append( datas["DataCell"][sub_key][i] )
    return table_flatten





    return prompts_list

def construct( texts, tables, get_fuction, kg, prompt_temp, mode, **args ):
    temp = []
    for i in tqdm( range( len(texts) ), desc=f"Constructing {mode} data for {'multi entity' if args['multi_entity'] else 'single entity'} type dataset"):
        temp_kg = deepcopy( kg )
        if isinstance( tables, tuple) and len(tables)==2:       # 是(tables["FirstColumn"], tables["DataCell"][sub_table_name])结果
            table = tables[0][i] | tables[1][i]
        else:
            table = tables[i] if tables!=None else None
        if table!=None and args["dataset_name"]=="cpl":
            for item in table:
                if "）_" in item[0]:
                    temp_tuple = ( item[0].split("_")[0], item[1])
                    table.remove( item )
                    table.add( temp_tuple )
        text = texts[i]
        """
        所有数据集的Train模式都应该用add_from_tuple
        所有数据集的Test的FirstColumn都应该用add_from_no_tuple
        所有数据集的Test的Datacell中除了e2e都应该用add_from_tuple
        """
        if mode == "train":
            temp_kg.add_from_tuple( table, args["multi_entity"], True)
        else:
            if args["first_column"]:
                temp_kg.add_from_no_tuple( args["multi_entity"], False )
            else:
                if args["multi_entity"]:
                    temp_kg.add_from_tuple( table, args["multi_entity"], True)
                else:    # e2e
                    temp_kg.add_from_no_tuple( args["multi_entity"], False )

        temp_list = get_fuction( temp_kg, text, prompt_temp, mode, **args)
        if mode=="train":
            temp.extend( temp_list )
        else:
            temp.append( temp_list )
    return temp

def Prepare_FT_Data( dataset_name, first_column ):
    """
    准备FT数据：e2e只有datacell模式，
    """
    mode = "train"
    kg, datas, args = load_shared( dataset_name, "train" )
    prompt_temp = args["prompt_temps"]["FirstColumn"] if first_column else args["prompt_temps"]["DataCell"]
    texts, tables = datas       # table是二元组或三元组
    prompt_list = []
    args["multi_entity"] = True
    args["dataset_name"] = dataset_name
    args["first_column"] = first_column
    if isinstance( tables, list ): # 单实例
        args["multi_entity"] = False
        prompt_list = construct( texts, tables, GetDataCellPrompt, kg, prompt_temp, mode, **args )
    else:
        if first_column:
            if isinstance( tables["FirstColumn"], list ):
                prompt_list = construct( texts, tables["FirstColumn"], GetFirstColumnPrompt, kg, prompt_temp, mode, **args )
            else:
                label_list = []
                for k in range( len( texts )):
                    temp = set()
                    for sub_table_name in tables["FirstColumn"].keys():
                        temp = temp | tables["FirstColumn"][sub_table_name][k]
                    label_list.append( temp )
                prompt_list = construct( texts, label_list , GetFirstColumnPrompt, kg, prompt_temp, mode, **args )
        else:
            if isinstance( tables["DataCell"], list ):
                prompt_list = construct( texts, (tables["FirstColumn"], tables["DataCell"]), GetDataCellPrompt, kg, prompt_temp, mode, **args )
            else:
                for sub_table_name in tables["DataCell"].keys():
                    temp_list = construct( texts, (tables["FirstColumn"][sub_table_name], tables["DataCell"][sub_table_name]), GetDataCellPrompt, kg, prompt_temp, mode, **args )
                    prompt_list.extend( temp_list )
    return prompt_list

def Prepare_Test_Data( dataset_name, first_column, entity_list=None ):
    """
    准备测试数据，此时tables数据只是标签，需要entity_list作为DataCell阶段的启动
    """
    mode = "test"
    kg, datas, args = load_shared( dataset_name, "train" )
    prompt_temp = args["prompt_temps"]["FirstColumn"] if first_column else args["prompt_temps"]["DataCell"]
    texts, tables = datas       # table是二元组或三元组
    prompt_list = []
    label_list = []
    args["multi_entity"] = True
    args["dataset_name"] = dataset_name
    args["first_column"] = first_column
    if isinstance( tables, list ):
        # 单实例，E2E专用   
        args["multi_entity"] = False
        prompt_list = construct( texts, entity_list, GetDataCellPrompt, kg, prompt_temp, mode, **args )
        label_list = tables
    else:
        # 多实例，Rotowire或CPL
        if first_column:
            # 实体名抽取
            if isinstance( tables["FirstColumn"], list ):
                prompt_list = construct( texts, entity_list, GetFirstColumnPrompt, kg, prompt_temp, mode, **args )
                label_list = tables["FirstColumn"]
            else:
                for k in range( len( texts )):
                    temp = set()
                    for sub_table_name in tables["FirstColumn"].keys():
                        temp = temp | tables["FirstColumn"][sub_table_name][k]
                    label_list.append( temp )
                prompt_list = construct( texts, entity_list , GetFirstColumnPrompt, kg, prompt_temp, mode, **args )
        else:
            # 属性关系抽取，SPLIT时，直接使用FirstColumn的实体类型、名称信息填充空知识图谱
            if _SPLITE:
                entity_list = tables["FirstColumn"]
            if isinstance( tables["DataCell"], list ):
                # 单表，CPL
                prompt_list = construct( texts, entity_list, GetDataCellPrompt, kg, prompt_temp, mode, **args )
                label_list = tables["DataCell"]
            else:
                # 多表，Rotowire
                for sub_table_name in tables["DataCell"].keys():
                    prompt_list.extend( construct( texts, entity_list[sub_table_name], GetDataCellPrompt, kg, prompt_temp, mode, **args ) )
                    label_list.extend( tables["DataCell"][sub_table_name] )
    return prompt_list, label_list

def Prepare_Application_Data( dataset_name, first_column, entity_list=None ):
    """
    准备测试数据，此时tables数据只是标签，需要entity_list作为DataCell阶段的启动
    """
    mode = "test"
    kg, datas, args = load_shared( dataset_name, "train" )
    prompt_temp = args["prompt_temps"]["FirstColumn"] if first_column else args["prompt_temps"]["DataCell"]
    texts = datas       # table是二元组或三元组
    prompt_list = construct( texts, entity_list, GetDataCellPrompt, kg, prompt_temp, mode, **args )
    return prompt_list

def all_datasets(dataset_name):
    entity_list = None
    #for dataset_name in ["e2e", "rotowire", "cpl"]:
    if dataset_name=="e2e":
        first_column = False
        # FT
        print(f"开始构建{dataset_name}数据集DataCell部分的Fine-Tuning数据")
        ft_data = Prepare_FT_Data( dataset_name, first_column )         # len = 251986， List[]
        save_path = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/ft.json")
        save_data( ft_data, save_path)
        # Test
        print(f"开始构建{dataset_name}数据集DataCell部分的Test数据对")
        prompts, labels = Prepare_Test_Data( dataset_name, first_column, entity_list )      # 35998, List[List[7]]
        save_path_prompts = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/prompt_list.pickle")
        save_path_labels = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/label_list.pickle")
        save_data( prompts, save_path_prompts)
        save_data( labels, save_path_labels)
    else:
        for first_column, part in zip( [True, False], ["first_column_", "data_cell_"]):
            print(f"开始构建{dataset_name}数据集{part}部分的Fine-Tuning数据")
            ft_data = Prepare_FT_Data( dataset_name, first_column )
            save_path = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{part}ft.json")
            save_data( ft_data, save_path)
            print(f"开始构建{dataset_name}数据集{part}部分的Test数据")
            prompts, labels = Prepare_Test_Data( dataset_name, first_column, entity_list )
            save_path_prompts = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{part}prompt_list.pickle")
            save_path_labels = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{part}label_list.pickle")
            save_data( prompts, save_path_prompts)
            save_data( labels, save_path_labels)
        """
        rotowire数据集first_column_部分的Fine-Tuning数据：6794, List[]
        rotowire数据集first_column_部分的Test数据: 3397, List[List[2]]
        rotowire数据集data_cell_部分的Fine-Tuning数据：953972, List[]
        rotowire数据集data_cell_部分的Test数据: 6794, List[List[95]]
        """
if __name__=="__main__":
    all_datasets( "cpl" )
    print("sss")
