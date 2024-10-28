
import os
import sys
import yaml
import importlib
import json
import pickle
from tqdm import tqdm

_RAG_MODE =  'rule_based'  #"naive"
_SPLITE = True

_ROOT_PATH = os.path.abspath(__file__)
for i in range(2):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert(0, _ROOT_PATH)
from KGs.get_empty_kg_by_name import return_kg, prompt_templates, config_data
from data.data_manager import DataManager, data_split
from Hybird_RAG.retriever.Retriver import HybirdRAG_for_Context
from Hybird_RAG.functions import rotowire_total_team_name
from utils import load_data, save_data
from copy import deepcopy



    
def load_shared( dataset_name, mode ):
    """
    mode: train或test
    """
    args = {}
    # 加载数据
    data_manager = DataManager( dataset_name, mode )
    datas = data_manager.main()
    # 加载配置
    config = config_data["DATASET_MANAGE"][dataset_name]
    args[ "language" ] = config["language"]
    args[ "prompt_temps" ] = prompt_templates[args[ "language" ]]
    args[ "field" ] = config["field"]
    args[ "extracted" ] = config["extracted"]

    ruled_text_path = os.path.join( _ROOT_PATH, f"data/{dataset_name}/{mode}.text_ruled.json")
    args[ "ruled_texts"] = load_ruled_text( ruled_text_path, dataset_name )
    # 加载KG
    kg = return_kg( dataset_name )


    return kg, datas, args



# 对单篇文章进行属性关系抽取，基于上面
def GetDataCellPrompt( 
        kg,                 # 空的知识图谱实例
        text,               # 文本
        prompt_temp,        # 提示词模板
        **args              # config中的一些配置，如extracted，predicate, field
    ):
    """
    获取这个知识图谱DataCell部分的提示词，由于非train模式必须两阶段分开，因此只有一种情况
        知识图谱已经通过真实的label add了不同的实体，通过kg.instance_num[entity]可以获得各个实体下对象的id列表
        此时遍历kg.entity_type_info中的属性类型定义字典中的实体，获取该实体的所有属性，同时遍历该实体下的对象，如果存在该属性则获取值作为answer，否则获取<NOT FOUND>
    """
    mode = args["mode"]
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

# 创建提示词列表
def construct( texts, tables, get_fuction, kg, prompt_temp, mode, **args ):
    temp = []
    args["mode"] = mode
    args[ "rag_mode" ] = _RAG_MODE
    for i in tqdm( range( len(texts) ), desc=f"Constructing {mode} data for {'multi entity' if args['multi_entity'] else 'single entity'} type dataset"):
        temp_kg = deepcopy( kg )
        args["order_number"] = i
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

        temp_list = get_fuction( temp_kg, text, prompt_temp, **args)
        if mode=="train":
            temp.extend( temp_list )
        else:
            temp.append( temp_list )
    return temp

# 准备FT数据
def Prepare_FT_Data( dataset_name, first_column ):
    """
    准备FT数据：e2e只有datacell模式，
    """
    mode = "train"
    kg, datas, args = load_shared( dataset_name, mode )
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

# 准备测试数据对
def Prepare_Test_Data( dataset_name, first_column, entity_list=None ):
    """
    准备测试数据，此时tables数据只是标签，需要entity_list作为DataCell阶段的启动
    """
    mode = "test"
    kg, datas, args = load_shared( dataset_name, mode )
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

# 准备应用数据（待完善）
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

# 自动化
def all_datasets(dataset_name):
    entity_list = None
    #for dataset_name in ["e2e", "rotowire", "cpl"]:
    for first_column, part in zip( [True, False], ["first_column_", "data_cell_"]):
        print(f"开始构建{dataset_name}数据集{part}部分的Fine-Tuning数据")
        ft_data = Prepare_FT_Data( dataset_name, first_column )
        save_path = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_{part}ft.json")
        save_data( ft_data, save_path)
        print(f"开始构建{dataset_name}数据集{part}部分的Test数据")
        prompts, labels = Prepare_Test_Data( dataset_name, first_column, entity_list )
        save_path_prompts = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_{part}prompt_list.pickle")
        save_path_labels = os.path.join( _ROOT_PATH, f"Hybird_RAG/temp/{dataset_name}/{dataset_name}_{part}label_list.pickle")
        save_data( prompts, save_path_prompts)
        save_data( labels, save_path_labels)
        """
        rotowire数据集first_column_部分的Fine-Tuning数据：6794, List[]
        rotowire数据集first_column_部分的Test数据: 3397, List[List[2]]
        rotowire数据集data_cell_部分的Fine-Tuning数据：953972, List[]
        rotowire数据集data_cell_部分的Test数据: 6794, List[List[95]]
        """

if __name__=="__main__":
    #for dataset_name in ["e2e", "rotowire", "cpl"]:
    #    all_datasets( dataset_name )
    all_datasets( "cpl" )
    print("sss")
