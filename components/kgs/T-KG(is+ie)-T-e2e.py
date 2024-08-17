import sys, os
from tqdm import tqdm
print("Working directory: {}".format(os.getcwd()))

tkgt_root = '/data/zhaozibo/TKGT/'
sys.path.append(tkgt_root)
model_selected = 'gpt-4o' # if use gpt series model, set model name here and openai_key at LLM class initiation

qr_model_selected = 'gpt-4o'
is_model_selected = 'gpt-4o'
ie_model_selected = 'gpt-4o'
cuda_device = 'cuda:0'


import pandas as pd
import json
import numpy as np
from components.kgs.dataset_kgs.e2e_kg import *
from utils import visualize_knowledge_graph_interactive, KnowledgeGraph, visualize_knowledge_graph
from components.retriever.DocData import *
from components.kgs.dataset_kgs.CPL_field import fields_list_CPL
import json
from components.kgs.dataset_kgs.CPL_kg import key_role_dict_naive

file_path = f'../../data/e2e/train.text'

##########

sys_prompt_ie_text = """
You are a helpful AI assistant who will accurately extract information from the text provided by the user based on the user’s requirements, and truthfully answer all questions in English."""

sys_prompt_ie = {"role": "system", "content": sys_prompt_ie_text}

##########

sys_prompt_is_text = """
You are a helpful AI assistant who will accurately summarize information related to the user’s questions from the text provided by the user, and truthfully answer in English.
"""

sys_prompt_is = {"role": "system", "content": sys_prompt_is_text}

##########

sys_prompt_qr_text = """
You are a helpful AI assistant who will write a query to retrieve useful information based on the user’s requirements and questions, and you will answer in English."""

sys_prompt_qr = {"role": "system", "content": sys_prompt_qr_text}

lines = []
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        lines.append(line.strip())


file_path = '../../data/e2e/train.xlsx'
# Load data from the JSON file
table_data = pd.read_excel(file_path)
table_data = table_data.applymap(lambda x: x.strip() if isinstance(x, str) else x)


# ### Preparing Incontext Example from Training Data


ie_prompt_extract_role_name_e2e_template= """
You are a useful table content filling assistant that can extract the attribute field values of the role based on the row and column values provided by the user, as well as their corresponding paragraph original text, from the original text.
1. Check if the provided paragraph contains the attribute values corresponding to the role. If not, respond 'Bad Infomation'.
2. If the relevant paragraph contains attribute values for the role, respond the value according to the given requirements.
3. Respond to the user's question like the examples provided below:

{EXAMPLE1}

{EXAMPLE2}

Below is the usr's question:
    Attribute: {FIELD}
    Related Context: {RELATED_CONTEXT}
    Question: What's the {FIELD} of {ROLE}?
    Answer:

"""


ie_example_template = """
Attribute: {FIELD}
Related Context:  {CONTEXT}
Question: What's the {FIELD} of {ARRT}?
Attribute Values: {VALUE_RANGE}
Answer: {ANSWER}
"""


ie_question_template = """
Attribute: {FIELD}
Related Context:  {CONTEXT}
Question: What's the {FIELD} of {ARRT}?
Attribute Values: {VALUE_RANGE}
Answer:
"""

incontext_examples_docs = []

splitter = SpecialSubStringTextSplitter(SP_Str_List, "backward")

def process_na(value):
    if pd.isna(value):
        return 'Bad Information'
    elif value.strip() == '':
        return 'Bad Information'
    elif value == 'nan':
        return 'Bad Information'
    else:
        return value

from components.kgs.dataset_kgs.e2e_rotowire_field import fields_list_rotowire, fields_list_e2e

fields = fields_list_e2e['Table1']['Fields']

ARRT = 'Restaurant'

for i in tqdm(range(len(lines)), desc='tables'):
    context = lines[i]
    row = table_data.iloc[i,:]
    for key, value in fields.items():
        attribute = key
        value_range = value
        answer = row[key]
        ie_example = ie_example_template.format(FIELD=attribute, CONTEXT=context, ARRT=ARRT, VALUE_RANGE=value_range, ANSWER=process_na(answer))
        incontext_examples_docs.append(ie_example)

incontext_docstore = DocStore(preprocessor=preprocessor, doc_data = SplittedList2Doc(incontext_examples_docs))
incontext_docstore.init_retriever()
incontext_docstore.create_pipeline()


# ### Prepare KG Class

import networkx as nx
import random
##################
### Prep KG-Class
##################

def get_between_colon_and_newline(result):
    """
    Return the string between ':' and '\n'.
    """
    start_index = result.find('Answer:')
    if start_index == -1:
        return "NA"
    
    start_index += len('Answer:')
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
            entity_name = self.graph.nodes[search_entity]['Name']
            if entity_name is None:
                return 'Name'
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
            description += "Direct:\n"
            for neighbor in neighbors:
                description += f"    {neighbor}:\n"
                neighbor_data = self.graph.nodes[neighbor]
                for label, value in neighbor_data.items():
                    description += f"      {label}: {value}\n"
        else:
            description += "没有有向关系.\n"
        
        return description

    def get_entity_name(self, entity):
        return self.graph.nodes[entity]['Name']

    def return_data_cpl(self):
        cells = []
        for entity in self.graph:
            entity_data = self.graph.nodes[search_entity]
            cells += [entity+data_item for data_item in entity_data]
        return cells


import plotly.graph_objects as go 

def visualize_knowledge_graph_interactive(kg):
    pos = nx.kamada_kawai_layout(kg.graph)

    # For edges
    edge_x, edge_y, edge_hovertext = [], [], []
    for edge in kg.graph.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append((x0 + x1) / 2)
        edge_y.append((y0 + y1) / 2)
        edge_hovertext.append('<br>'.join([f"{key}: {value}" for key, value in edge[2].items()]))

    edge_trace = go.Scatter(x=edge_x, y=edge_y, text=edge_hovertext,
                            mode='markers', hoverinfo='text',
                            marker=dict(size=1, color='rgba(0,0,0,0)'))

    # For nodes
    node_x = [pos[node][0] for node in kg.graph.nodes()]
    node_y = [pos[node][1] for node in kg.graph.nodes()]
    node_info = ['<br>'.join([f"{key}: {value}" for key, value in data.items()]) for node, data in kg.graph.nodes(data=True)]
    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text',
                            text=[data.get('name', 'Unnamed Entity') for node, data in kg.graph.nodes(data=True)],
                            marker=dict(showscale=True, colorscale='YlGnBu', size=10),
                            textposition="bottom center", hoverinfo='text', hovertext=node_info)

    line_trace = go.Scatter(x=[x for sublist in [[pos[edge[0]][0], pos[edge[1]][0], None] for edge in kg.graph.edges()] for x in sublist],
                            y=[y for sublist in [[pos[edge[0]][1], pos[edge[1]][1], None] for edge in kg.graph.edges()] for y in sublist],
                            line=dict(width=2, color='#888'), mode='lines')

    fig = go.Figure(data=[line_trace, node_trace, edge_trace], layout=go.Layout(showlegend=False, hovermode='closest', margin=dict(b=0, l=0, r=0, t=0),
                                                                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                                                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    fig.show()


from components.models.LLM import LLM
import httpx
from openai import OpenAI

def extract_answer(text):
    answer_keyword = "回答:"
    start_index = text.find(answer_keyword)
    
    if start_index != -1:
        start_index += len(answer_keyword)
        return text[start_index:].strip()
    else:
        return None


openai_key = 'your key here'

client = OpenAI(
    api_key = openai_key,
)


# ### TKGT Prompt & Model


qr_prompt_extract_value_template="""
You are a helpful AI assistant that can help the user write a query based on the row and column values provided, in order to extract the attribute value of a character from the original text. You will only return the query text and will not provide any additional explanations or other text.

The retriever you are using is: {RetrieverName}

Here is the user's question:
- Role: {ROLE}
- Attribute: {FIELD}
- Relevant Background: {RELATED_CONTEXT}
- Question: What is the value of {FIELD}?
- Query:
"""

is_prompt_extract_value_template="""
You are a helpful information summarization assistant. You can extract useful information from the provided known information and rephrase it into a brief and precise summary, based on the row values and column values given by the user along with the corresponding original text.

Here is the user's question:
- Role: {ROLE}
- Attribute: {FIELD}
- Relevant Background: {RELATED_CONTEXT}
- Value Range: {SCOPE}
- Question: What is the value of {FIELD}?

Below is the known information:
- {KGREP}

Please extract useful information from the known information and rephrase it into a brief and precise summary:
- Summary:
"""

ie_prompt_extract_value_template="""
You are a helpful assistant for filling in table content. You can extract attribute values of a character from the original text based on the row and column values provided by the user.

Check if the provided paragraph contains the attribute value of the corresponding character. If not, answer 'Bad Information.'
If the relevant paragraph contains the attribute value of the character, answer with the value according to the given requirements.

Answer the user's question according to the examples provided below:

- {InContextExp1}

- {InContextExp2}

Here is the user's question:
- Role: {ROLE}
- Attribute: {FIELD}
- Relevant Background: {RELATED_CONTEXT}
- Value Range: {SCOPE}
- Question: What is the value of {FIELD}?
- Answer:
"""



qr_model = LLM(model_name = qr_model_selected, 
               device=cuda_device, 
               client=client, 
               sys_prompt=sys_prompt_qr)


is_model = LLM(model_name = is_model_selected, 
               device=cuda_device, 
               client=client, 
               sys_prompt=sys_prompt_is)


ie_model = LLM(model_name = ie_model_selected, 
               device=cuda_device, 
               client=client, 
               sys_prompt=sys_prompt_is)


file_path = '../../data/e2e/test.text'
lines = []
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        lines.append(line.strip())


file_path = '../../data/e2e/test.xlsx'
# Load data from the JSON file
table_data = pd.read_excel(file_path)
table_data = table_data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

RN = 'Hybrid Retriever: all-MiniLM-L12-v2 + BM25'
entitie_name = ['Restaurant']

cells = []

for i in tqdm(range(len(lines)), desc='Tables'):
    ### Construct a KG
    e2e_kg = KnowledgeGraph()
    
    text = lines[i].replace("\\n", "\n")
    reference_table = table_data.iloc[i, :]
    reference_table
    for entity in entitie_name:
        entity_columns = {}
        for key, value in fields.items():
            entity_columns[key] = None
        e2e_kg.add_entity(entity, entity_columns)
    
    while True:
        # Get search target
        search_entity = e2e_kg.get_search_entity()
        if not search_entity:
            break
        search_label = e2e_kg.get_random_unfilled_label(search_entity)
        if not search_label:
            break
        search_entity_name = e2e_kg.get_entity_name(search_entity)
        print(f"Retrieving {search_label} of {search_entity}")
        
        role = search_entity
        scope = fields[search_label]
        
        ie_question = ie_question_template.format(FIELD=search_label, CONTEXT=text, 
                                                  ARRT=ARRT, VALUE_RANGE=scope)
        
        inc_examples = incontext_docstore.retrieve(ie_question,
                                sparse_top_k = 5, 
                                dense_top_k = 5, 
                                join_top_k = 5, 
                                reranker_topk = 2)
        incontext_example1 = inc_examples[0].content
        incontext_example2 = inc_examples[1].content
        kg_rep = '{}信息: {}'.format(search_entity, e2e_kg.describe_entity(search_entity))
        is_prompt_instance = is_prompt_extract_value_template.format(RetrieverName=RN, ROLE=search_entity, FIELD=search_label, SCOPE=scope, RELATED_CONTEXT=text, KGREP = kg_rep)
        kg_is_raw = is_model.generate(is_prompt_instance, max_new_tokens=32)
        role_value_prompt = ie_prompt_extract_value_template.format(InContextExp1=incontext_example1, InContextExp2=incontext_example2, 
                                                                    ROLE=search_entity, FIELD=search_label, SCOPE=scope, 
                                                                    RELATED_CONTEXT=text+kg_is_raw)
        role_value_answer = reference_table[search_label]
        search_value = ie_model.generate(role_value_prompt, max_new_tokens=64)
        e2e_kg.update_entity(search_entity, search_label, search_value)
        cells.append({'pred': search_value, 'groundtruth':str(process_na(role_value_answer))})




# Function to replace empty strings, single spaces, and 'nan' with 'Bad Information'
def replace_bad_info(item):
    for key, value in item.items():
        if value in ['', ' ', 'nan', np.nan]:
            item[key] = 'Bad Information'
        elif key == 'pred':
            if 'Yes:' in value:
                item[key] = value.split('Yes:')[-1]
            elif 'Yes' in value and len(value)>=3:
                item[key] = value.split('Yes')[-1]
            elif 'Answer:' in value:
                item[key] = value.split('Answer:')[-1]
    return item


# Apply the function to each dictionary in the list
cells = [replace_bad_info(d) for d in cells]

from sklearn.metrics import precision_score, recall_score, f1_score
from sacrebleu import corpus_chrf
from bert_score import score
from sacrebleu import CHRF


preds = [d['pred'] for d in cells]
groundtruths = [d['groundtruth'] for d in cells]


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

