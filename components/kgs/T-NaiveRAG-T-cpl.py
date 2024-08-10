import os
print(f"Working directory: {}".format(os.getcwd()))
import sys, os

tkgt_root = '~/text-kgs-table'
sys.path.append(tkgt_root)
model_selected = 'THUDM/chatglm3-6b' # if use gpt series model, set model name here and openai_key at LLM class initiation
cuda_device = 'cuda:0'

import pandas as pd
import json
import numpy as np
from components.kgs.dataset_kgs.e2e_kg import *
from utils import visualize_knowledge_graph_interactive, KnowledgeGraph, visualize_knowledge_graph
from components.retriever.DocData import *
from components.kgs.dataset_kgs.CPL_field import fields_list_CPL
import json
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from components.kgs.dataset_kgs.CPL_kg import key_role_dict_naive

file_path = f'../../data/CPL/text'

sys_prompt_ie_text = """
您是一位有帮助的人工智能助手，会根据用户的要求从用户提供的文本中准确提取信息，并用中文如实回答所有问题。
"""

sys_prompt_ie = {"role": "system", "content": sys_prompt_ie_text}


# Reading the file line by line and storing each line in a list
lines = []
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        lines.append(line.strip())

doc_store = DocStore(preprocessor=preprocessor,
                    doc_data = SplittedList2Doc([lines[index]]))
doc_store.init_retriever()
doc_store.create_pipeline()


file_path = '../../data/CPL/table_processed.json'
# Load data from the JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    table_data = json.load(file)

### Preparing Incontext Example from training data

incontext_example_template="""
角色: {ROLE}
属性: {FIELD}
相关背景: {RELATED_CONTEXT}
值范围: {SCOPE}
问题: {FIELD}的取值是什么?
回答: {ANSWER}
"""

incontext_examples_docs = []

splitter = SpecialSubStringTextSplitter(SP_Str_List, "backward")

for i in tqdm(range(450)):
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
            search_value = reference_table[query]
            incontext_example = ie_prompt_extract_value_template.format(ROLE=role, FIELD=query, SCOPE=scope, RELATED_CONTEXT=query_docs, ANSWER=search_value)
            incontext_examples_docs.append(incontext_example)
        except Exception as e:
            print(f"Warning: {e}")


incontext_docstore = DocStore(preprocessor=preprocessor, doc_data = incontext_examples_docs)


ie_prompt_extract_value_template="""
你是一个有用的表格内容填充助手，可以根据用户提供的行值和列值以及其对应的原文段落，从原文中提取角色的属性字段值。

检查提供的段落是否包含对应角色的属性值。如果没有，回答'Bad Information'。
如果相关段落包含角色的属性值，按照给定的要求回答值。
按照下面提供的例子回答用户的问题：

{InContextExp1}

{InContextExp2}

以下是用户的问题：
角色: {ROLE}
属性: {FIELD}
相关背景: {RELATED_CONTEXT}
值范围: {SCOPE}
问题: {FIELD}的取值是什么?
回答:
"""


def extract_answer(text):
    answer_keyword = "回答:"
    start_index = text.find(answer_keyword)
    
    if start_index != -1:
        start_index += len(answer_keyword)
        return text[start_index:].strip()
    else:
        return None

ie_model = LLM(model_name = model_selected, 
               device=cuda_device, 
               client=client, 
               sys_prompt=sys_prompt_ie)




splitter = SpecialSubStringTextSplitter(SP_Str_List, "backward")

for i in tqdm(range(450:)):
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

            incontext_example1 = incontext_docstore.retrieve(query,
                                        sparse_top_k = 5, 
                                        dense_top_k = 5, 
                                        join_top_k = 5, 
                                        reranker_topk = 1)[0].content
            incontext_example2 = incontext_docstore.retrieve(query,
                                        sparse_top_k = 5, 
                                        dense_top_k = 5, 
                                        join_top_k = 5, 
                                        reranker_topk = 1)[1].content
            
            role_value_prompt = ie_prompt_extract_value_template.format(InContextExp1=incontext_example1, InContextExp2=incontext_example2, ROLE=role, FIELD=query, SCOPE=scope, RELATED_CONTEXT=query_docs)
            role_value_answer = reference_table[query]
            search_value = ie_model.generate(role_value_prompt, max_new_tokens=1024)
            print(f"Extraction Result: {search_value}")
            ie_model.reset_chat()
            cells.append({'pred': search_value, 'groundtruth':str(role_value_answer)})
        except Exception as e:
            print(f"Warning: {e}")



# Function to replace empty strings, single spaces, and 'nan' with 'Bad Information'
def replace_bad_info(item):
    for key, value in item.items():
        if value in ['', ' ', 'nan', np.nan]:
            item[key] = 'Bad Information'
        elif key == 'pred':
            if '是：' in value:
                item[key] = value.split('是：')[-1]
            elif '是' in value and len(value)>=3:
                item[key] = value.split('是')[-1]
            elif '回答: ' in value:
                item[key] = value.split('回答: ')[-1]
    return item


# Apply the function to each dictionary in the list
cells = [replace_bad_info(d) for d in cells]

from sklearn.metrics import precision_score, recall_score, f1_score
from sacrebleu import corpus_chrf
from bert_score import score
from sacrebleu import CHRF


preds = [d['pred'] for d in first_cols]
groundtruths = [d['groundtruth'] for d in first_cols]


# 1. Exact Match
exact_matches = [1 if p == g else 0 for p, g in zip(preds, groundtruths)]
precision_exact = np.mean(exact_matches)
recall_exact = np.mean(exact_matches)
f1_exact = f1_score([1]*len(exact_matches), exact_matches, average='binary')

# 2. Character F-score (chrf)
chrf_scorer = CHRF(word_order=0)  # Use word_order=0 for character-level scoring
chrf_score = chrf_scorer.corpus_score(preds, [groundtruths])
chrf_f1 = chrf_score.score / 100.0

# 3. BERTScore
P, R, F1 = score(preds, groundtruths, lang="en", rescale_with_baseline=True)
bert_precision = P.mean().item()
bert_recall = R.mean().item()
bert_f1 = F1.mean().item()

# Results
print("Exact Match F1 Score:", f1_exact)
print("chrf F1 Score:", chrf_f1)
print("BERTScore Precision:", bert_precision)
print("BERTScore Recall:", bert_recall)
print("BERTScore F1 Score:", bert_f1)

