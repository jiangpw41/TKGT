import os
os.getcwd()
import sys, os
sys.path.append('/home/zbzhao/text-kgs-table')
import pandas as pd
from components.kgs.dataset_kgs.e2e_kg import *
from utils import visualize_knowledge_graph_interactive, KnowledgeGraph, visualize_knowledge_graph
from components.retriever.DocData import *

file_path = f'../../data/CPL/text'

# Reading the file line by line and storing each line in a list
lines = []
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        lines.append(line.strip())

from components.kgs.dataset_kgs.e2e_rotowire_field import fields_list_rotowire, fields_list_e2e
from components.kgs.dataset_kgs.CPL_field import fields_list_CPL
import json
import numpy as np
import pandas as pd


ie_prompt_extract_value_template="""
你是一个有用的表格内容填充助手，可以根据用户提供的行值和列值以及其对应的原文段落，从原文中提取角色的属性字段值。

检查提供的段落是否包含对应角色的属性值。如果没有，回答'Bad Information'。
如果相关段落包含角色的属性值，按照给定的要求回答值。
按照下面提供的例子回答用户的问题：

角色: 原告
属性: 出借人（原告）需返回本金总额（元）
相关背景: 本案现已审理终结。原告卢江平诉称：被告自2013年10月起，以经营周转为由向原告借款。后原告分别于2013年10月10日向被告汇款630500元、于2014年4月21日向被告汇款291000元，合计921500元。2015年5月12日，因被告无法按期偿还借款，经双方对账，被告于当日向原告出具借条一张，载明欠原告707100元借款，限于2015年6月30日之前付清。还款到期后，被告拒绝偿还借款。请求法院判令被告向原告偿还借款707100元、利息22921。66元（从2015年7月1日起按同期银行6个月贷款利率计算至起诉之日，后续按照年息4。35%的标准计算至实际还款之日止），两项合计730021。66元；本案诉讼费用由被告承担。
角色选项范围: ['Team']
问题: 出借人（原告）需返回本金总额（元）的取值是什么?
回答: 707100

角色: 法院
属性: '法院1需返回逾期利息利息率类型'
相关背景: 被告刘维辉于本判决生效后十日内偿还原告卢江平借款本金707100元，并支付逾期利息（以707100元为基数，自2015年7月1日起按照同期银行六个月贷款利率计算至借款本金付清之日止）。
角色选项范围: ['1=年利率;', '2=年利息;', '3=月利率;', '4=月利息;', '5=日利率', '6=日利息', '7=中国人民银行同期同档次贷款基准利率', '8=贷款市场报价利率(LPR)', '9=中国人民银行同期同档次贷款基准利率的四倍', '10=贷款市场报价利率(LPR)的四倍', '11=同国家规定/司法保护上限', '12=借款额的占比', '13=约定的数额（固定数额）', '14=年固定分红', '15=月固定分红', '16=日固定分红']
问题: 法院1需返回逾期利息利息率类型的取值是什么?
回答: 7=中国人民银行同期同档次贷款基准利率

以下是用户的问题：

以下是用户的问题：
角色: {ROLE}
属性: {FIELD}
相关背景: {RELATED_CONTEXT}
值范围: {SCOPE}
问题: {FIELD}的取值是什么?
回答:
"""

import json
file_path = '../../data/CPL/table_processed.json'
# Load data from the JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    table_data = json.load(file)


from components.kgs.dataset_kgs.CPL_kg import key_role_dict_naive

from tqdm import tqdm

ft_data = []

splitter = SpecialSubStringTextSplitter(SP_Str_List, "backward")

#for i in tqdm(range(len(lines))):
for i in tqdm(range(len(lines))):
    text = lines[i].replace("\\n", "\n")
    segments_backward = splitter.split(text, 'backward')

    doc_store = DocStore(preprocessor=preprocessor,
                        doc_data = SplittedList2Doc(segments_backward))
    doc_store.init_retriever()
    doc_store.create_pipeline()

    reference_table = table_data[i]
    
    for query in reference_table.keys():
        try:
            query_docs = doc_store.retrieve(query,
                                        sparse_top_k = 5, 
                                        dense_top_k = 5, 
                                        join_top_k = 5, 
                                        reranker_topk = 1)[0].content
            role = key_role_dict_naive[query]['role']
            scope = key_role_dict_naive[query]['value_range']
            role_value_prompt = ie_prompt_extract_value_template.format(ROLE=role, FIELD=query, SCOPE=scope, RELATED_CONTEXT=query_docs)
            role_value_answer = reference_table[query]
            if pd.isna(role_value_answer):
                role_value_answer = "No Info Found"
            ft_data.append({"instruction": "Given the context, extract the information", "input": role_value_prompt, "output": str(role_value_answer)})
        except Exception as e:
            print(f"Warning: {e}")

print(f"length of finetuning data: {len(ft_data)}")

# Specify the filename
ft_data_path = './'#"/data/zhaozibo/text-kgs-table/LLaMA-Factory/data"
filename = 'cpl_ie_train.json'
file_path = os.path.join(ft_data_path, filename)
# Open the file in write mode
with open(file_path, 'w') as json_file:
    json.dump(ft_data, json_file)

