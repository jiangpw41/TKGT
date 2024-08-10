import os
print(f"Working directory: {}".format(os.getcwd()))
import sys, os

tkgt_root = '~/text-kgs-table'
sys.path.append(tkgt_root)
model_selected = 'THUDM/chatglm3-6b' # if use gpt series model, set model name here and openai_key at LLM class initiation
qr_model_selected = 'gpt-4-turbo'
is_model_selected = 'gpt-4-turbo'
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

##################
### Prep KG-Class
##################

def get_between_colon_and_newline(result):
    """
    Return the string between ':' and '\n'.
    """
    start_index = result.find('回答:')
    if start_index == -1:
        return "NA"
    
    start_index += len('回答:')
    end_index = result.find('\n', start_index)
    
    if end_index == -1:
        return result[start_index:].strip()
    
    return result[start_index:end_index].strip()


class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_entity(self, entity_id, entity_info=None, default_labels=None):
        if default_labels is None:
            default_labels = []  # Default to an empty list if no default labels are provided
        # Initialize default labels with None or empty values
        entity_data = {label: None for label in default_labels}
        # Update with any provided entity info
        if entity_info is not None:
            entity_data.update(entity_info)
        self.graph.add_node(entity_id, **entity_data)

    def update_entity(self, entity_id, label, label_value):
        """
        Update the value of label for entity
        """
        if entity_id in self.graph:
            if label in self.graph.nodes[entity_id]:
                self.graph.nodes[entity_id][label] = label_value
            else:
                raise KeyError(f"Label '{label}' does not exist for entity '{entity_id}'.")
        else:
            raise KeyError(f"No entity found with ID '{entity_id}'.")



    def get_unfilled_labels(self):
        unfilled = {}
        for node_id, data in self.graph.nodes(data=True):
            missing_labels = {label: val for label, val in data.items() if val is None}
            if missing_labels:
                unfilled[node_id] = missing_labels
        return unfilled

    def get_entity(self, entity_id):
        return self.graph.nodes[entity_id]

    def add_relationship(self, entity1, entity2, attributes):
        """
        add directed relationship from entity1 to entity2
        """
        self.graph.add_edge(entity1, entity2, **attributes)

    def get_search_entity(self):
        """
        1. for all entities, calculate number of labels under entity, number of filled label under entity
        2. for all entities, calculate the number of labels under adjacent entities, number of filled labels under adjacent entities
        3. select the entities that has the largest number of (number of filled labels under adjacent entities)/(number of labels under adjacent entities)
        4. for the selected entities, return the entity that has the lowest value of (number of filled labels under entities)/(number of labels under entities)
        5. if there are more than one entitities has the same lowest value of (number of filled labels under entities)/(number of labels under entities), randomly return one of them
        6. if an entity has no adjancent entities, it should be viewed as equivalent as having the (number of filled labels under adjacent entities)/(number of labels under adjacent entities), if no entities has adjacent entities, the values of (number of filled labels under adjacent entities)/(number of labels under adjacent entities) for them would all be set to 1
        """
        # Step 1: Calculate number of labels and number of filled labels for each entity
        entity_scores = {}
        for entity_id, data in self.graph.nodes(data=True):
            num_labels = len(data)
            num_filled_labels = sum(1 for value in data.values() if value is not None)
            entity_scores[entity_id] = (num_labels, num_filled_labels)

        # Step 2: Calculate number of labels and filled labels for adjacent entities
        adjacent_scores = {}
        for entity_id in self.graph.nodes:
            num_adj_labels = 0
            num_adj_filled_labels = 0
            neighbors = list(self.graph.neighbors(entity_id))
            if neighbors:
                for neighbor in neighbors:
                    num_adj_labels += entity_scores[neighbor][0]
                    num_adj_filled_labels += entity_scores[neighbor][1]
                adj_filled_ratio = num_adj_filled_labels / num_adj_labels
            else:
                adj_filled_ratio = 1  # Handle the case where there are no adjacent entities
            adjacent_scores[entity_id] = (num_adj_labels, num_adj_filled_labels, adj_filled_ratio)

        # Step 3: Select entities based on adjacent entities' filled labels ratio
        selected_entities = []
        max_adj_filled_ratio = -1
        for entity_id, (num_adj_labels, num_adj_filled_labels, adj_filled_ratio) in adjacent_scores.items():
            if adj_filled_ratio > max_adj_filled_ratio:
                selected_entities = [entity_id]
                max_adj_filled_ratio = adj_filled_ratio
            elif adj_filled_ratio == max_adj_filled_ratio:
                selected_entities.append(entity_id)

        # Step 4: For selected entities, find the one with the lowest filled labels ratio
        best_entities = []
        min_filled_ratio = float('inf')
        for entity_id in selected_entities:
            num_labels, num_filled_labels = entity_scores[entity_id]
            if num_labels > 0:
                filled_ratio = num_filled_labels / num_labels
                if filled_ratio < min_filled_ratio:
                    best_entities = [entity_id]
                    min_filled_ratio = filled_ratio
                elif filled_ratio == min_filled_ratio:
                    best_entities.append(entity_id)

        # Step 5: Return one of the entities with the lowest filled ratio randomly
        if best_entities:
            return random.choice(best_entities)
        return None


    def get_random_unfilled_label(self, search_entity):
        """
        Randomly return an unfilled label under search_entity
        If the name label is unfilled, return the name label:
            entity_name = self.graph.nodes[search_entity]['Name Label']
        """
        if search_entity in self.graph:
            entity_data = self.graph.nodes[search_entity]
            entity_name = self.graph.nodes[search_entity][self.graph.nodes[search_entity]['Name Label']]
            if entity_name is None:
                return self.graph.nodes[search_entity]['Name Label']
            unfilled_labels = [label for label, value in entity_data.items() if value is None]
            if unfilled_labels:
                return random.choice(unfilled_labels)
        return None

    def describe_kg(self):
        """
        Return a string that describes the knowledge graph for passing it to a LLM
        """
        description = "Knowledge Graph Description:\n"
        for entity_id, data in self.graph.nodes(data=True):
            description += f"Entity: {entity_id}\n"
            for label, value in data.items():
                description += f"  {label}: {value}\n"
            neighbors = list(self.graph.neighbors(entity_id))
            if neighbors:
                description += f"  Connected to: {', '.join(neighbors)}\n"
            description += "\n"
        return description

    def describe_entity(self, entity):
        """
        Return a string that describes the entity in the KG,
        describe by its own labels, relationship to adjacent entities and labels of adjacent entities
        """
        if entity not in self.graph:
            return f"Entity {entity} does not exist in the knowledge graph."
        
        description = f"Entity: {entity}\n"
        entity_data = self.graph.nodes[entity]
        for label, value in entity_data.items():
            description += f"  {label}: {value}\n"
        
        neighbors = list(self.graph.neighbors(entity))
        if neighbors:
            description += "有向关系:\n"
            for neighbor in neighbors:
                description += f"    {neighbor}:\n"
                neighbor_data = self.graph.nodes[neighbor]
                for label, value in neighbor_data.items():
                    description += f"      {label}: {value}\n"
        else:
            description += "没有有向关系.\n"
        
        return description

    def get_entity_name(self, entity):
        return self.graph.nodes[entity][self.graph.nodes[entity]['Name Label']]

    def return_data_cpl(self):
        cells = []
        for entity in self.graph:
            entity_data = self.graph.nodes[search_entity]
            cells += [entity+data_item for data_item in entity_data]
        return cells

##########
### Main
##########

qr_prompt_extract_value_template="""
你是一个有用的可以根据用户提供的行值和列值帮助用户写出查询问题的query从而从原文中提取角色的属性字段值的ai助手。

你使用的检索器是: {RetrieverName}

以下是用户的问题：
角色: {ROLE}
属性: {FIELD}
相关背景: {RELATED_CONTEXT}
问题: {FIELD}的取值是什么?
查询query:
"""

is_prompt_extract_value_template="""
你是一个有用的信息总结助手，可以根据用户提供的行值和列值以及其对应的原文段落，从已知信息中提取有用信息并转述成简短精确的总结。

以下是用户的问题：
角色: {ROLE}
属性: {FIELD}
相关背景: {RELATED_CONTEXT}
值范围: {SCOPE}
问题: {FIELD}的取值是什么?

以下是已知信息:
{KGREP}

请从已知信息中提取有用信息并转述成简短精确的总结:
总结:
"""


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


def extract_query(text):
    answer_keyword = "查询query:"
    start_index = text.find(answer_keyword)
    
    if start_index != -1:
        start_index += len(answer_keyword)
        return text[start_index:].strip()
    else:
        return None

qr_model = LLM(model_name = qr_model_selected, 
               device=cuda_device, 
               client=client, 
               sys_prompt=sys_prompt_ie)


def extract_summary(text):
    answer_keyword = "总结:"
    start_index = text.find(answer_keyword)
    
    if start_index != -1:
        start_index += len(answer_keyword)
        return text[start_index:].strip()
    else:
        return None

is_model = LLM(model_name = is_model_selected, 
               device=cuda_device, 
               client=client, 
               sys_prompt=sys_prompt_ie)


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

RN = 'Hybrid Retriever: all-MiniLM-L12-v2 + BM25'

entitie_name = ['法院', '出借人（原告）', '借款人（被告）', '担保人（被告）', '其他诉讼参与人']

splitter = SpecialSubStringTextSplitter(SP_Str_List, "backward")

cells = []

for i in tqdm(range(450:)):
    text = lines[i].replace("\\n", "\n")
    segments_backward = splitter.split(text, 'backward')

    doc_store = DocStore(preprocessor=preprocessor,
                        doc_data = SplittedList2Doc(segments_backward))
    doc_store.init_retriever()
    doc_store.create_pipeline()
    cpl_kg = KnowledgeGraph()
    reference_table = table_data[i]
    
    for entity in entitie_name:
        entity_columns = {}
        for key, value in reference_table.items():
            if entity in key:
                entity_columns[key] = None
        cpl_kg.add_entity(entity, entity_columns)
    cpl_kg.add_relationship('法院', '出借人（原告）', {"审理关系": '审理'})
    cpl_kg.add_relationship('法院', '借款人（被告）', {"审理关系": '审理'})
    cpl_kg.add_relationship('法院', '担保人（被告）', {"审理关系": '审理'})
    cpl_kg.add_relationship('法院', '其他诉讼参与人', {"审理关系": '审理'})
    cpl_kg.add_relationship('出借人（原告）', '法院', {"审理关系": '被审理'})
    cpl_kg.add_relationship('出借人（原告）', '借款人（被告）', {"审理关系": '起诉'})
    cpl_kg.add_relationship('出借人（原告）', '担保人（被告）', {"审理关系": '起诉'})
    cpl_kg.add_relationship('出借人（原告）', '其他诉讼参与人', {"审理关系": '被验证'}) 
    cpl_kg.add_relationship('借款人（被告）', '法院', {"审理关系": '被审理'})
    cpl_kg.add_relationship('借款人（被告）', '借款人（被告）', {"审理关系": '被起诉'})
    cpl_kg.add_relationship('借款人（被告）', '担保人（被告）', {"审理关系": '被担保借款'})
    cpl_kg.add_relationship('借款人（被告）', '其他诉讼参与人', {"审理关系": '被验证借款'})    
    cpl_kg.add_relationship('担保人（被告）', '法院', {"审理关系": '被审理'})
    cpl_kg.add_relationship('担保人（被告）', '借款人（被告）', {"审理关系": '担保借款'})
    cpl_kg.add_relationship('担保人（被告）', '出借人（原告）', {"审理关系": '被起诉借款'})
    cpl_kg.add_relationship('担保人（被告）', '其他诉讼参与人', {"审理关系": '被验证'})    
    cpl_kg.add_relationship('其他诉讼参与人', '出借人（原告）', {"审理关系": '验证'})
    cpl_kg.add_relationship('其他诉讼参与人', '借款人（被告）', {"审理关系": '验证'})
    cpl_kg.add_relationship('其他诉讼参与人', '担保人（被告）', {"审理关系": '验证'})
    cpl_kg.add_relationship('其他诉讼参与人', '法院', {"审理关系": '被审理'})

    try:
        while True:
            # Get search target
            search_entity = rotowire_kg.get_search_entity()
            if not search_entity:
                break
            search_label = rotowire_kg.get_random_unfilled_label(search_entity)
            if not search_label:
                break
            search_entity_name = rotowire_kg.get_entity_name(search_entity)
            print(f"Retrieving {search_label} of {search_entity}")
            query_init = search_label
    
            query_docs = doc_store.retrieve(query_init,
                                        sparse_top_k = 5, 
                                        dense_top_k = 5, 
                                        join_top_k = 5, 
                                        reranker_topk = 1)[0].content
            role = key_role_dict_naive[query]['role']
            scope = key_role_dict_naive[query]['value_range']
    
            qr_prompt_instance = qr_prompt_extract_value_template.format(RetrieverName=RN, ROLE=role, FIELD=query_init, SCOPE=scope, RELATED_CONTEXT=query_docs)
            query_raw = qr_model.generate(qr_prompt_instance, max_new_tokens=64)
            query = extract_query(query_raw)
            
            
            incontext_example1 = incontext_docstore.retrieve(query_init,
                                        sparse_top_k = 5, 
                                        dense_top_k = 5, 
                                        join_top_k = 5, 
                                        reranker_topk = 1)[0].content
            incontext_example2 = incontext_docstore.retrieve(query,
                                        sparse_top_k = 5, 
                                        dense_top_k = 5, 
                                        join_top_k = 5, 
                                        reranker_topk = 1)[1].content
            kg_rep = '{}信息: {}\n已知信息: {}'.format(search_entity, cpl_kg.describe_entity(search_entity), cpl_kg.describe_kg())
            is_prompt_instance = is_prompt_extract_value_template.format(RetrieverName=RN, ROLE=role, FIELD=query_init, SCOPE=scope, RELATED_CONTEXT=query_docs, KGREP = kg_rep)
            kg_is_raw = qr_model.generate(qr_prompt_instance, max_new_tokens=64)
            kg_is = extract_summary(kg_is_raw)
            role_value_prompt = ie_prompt_extract_value_template.format(InContextExp1=incontext_example1, InContextExp2=incontext_example2, ROLE=role, FIELD=query, SCOPE=scope, RELATED_CONTEXT=query_docs+"已知信息总结:"+kg_is)
            role_value_answer = reference_table[query_init]
            search_value = ie_model.generate(role_value_prompt, max_new_tokens=1024)
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

