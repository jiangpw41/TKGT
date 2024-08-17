import os
os.getcwd()

import sys, os
sys.path.append('/data/zhaozibo/TKGT')
import numpy as np
import pandas as pd
from components.kgs.dataset_kgs.e2e_kg import *
from utils import visualize_knowledge_graph_interactive, KnowledgeGraph, visualize_knowledge_graph
from components.retriever.DocData import *

from components.kgs.dataset_kgs.e2e_rotowire_field import fields_list_rotowire, fields_list_e2e
from components.kgs.dataset_kgs.CPL_field import fields_list_CPL
import json
from tqdm import tqdm

part = "train"
file_path = f'../../data/e2e/{part}.text'

# Reading the file line by line and storing each line in a list
lines = []
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        lines.append(line.strip())

fields = fields_list_e2e['Table1']['Fields']
fields

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

part = 'train'
table_data = pd.read_excel(f"../../data/e2e/{part}.xlsx")
table_data = table_data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

example_list = []

ARRT = 'Restaurant'

for i in tqdm(range(len(lines)), desc='tables'):
    context = lines[i]
    row = table_data.iloc[i,:]
    for key, value in fields.items():
        attribute = key
        value_range = value
        answer = row[key]
        ie_example = ie_example_template.format(FIELD=attribute, CONTEXT=context, ARRT=ARRT, VALUE_RANGE=value_range, ANSWER=answer)
        example_list.append(ie_example)

incontext_docstore = DocStore(preprocessor=preprocessor, doc_data = SplittedList2Doc(example_list))
incontext_docstore.init_retriever()
incontext_docstore.create_pipeline()

ft_data = []

for i in tqdm(range(len(lines)), desc='tables'):
    i = 0
    context = lines[i]
    row = table_data.iloc[i,:]
    
    for key, value in fields.items():
        attribute = key
        value_range = value
        answer = row[key]
        ie_question = ie_question_template.format(FIELD=attribute, CONTEXT=context, ARRT=ARRT, VALUE_RANGE=value_range)
        # extract example
        inc_examples = incontext_docstore.retrieve(ie_question,
                                sparse_top_k = 5, 
                                dense_top_k = 5, 
                                join_top_k = 5, 
                                reranker_topk = 2)
        inc_example1 = inc_examples[0].content
        inc_example2 = inc_examples[1].content
        ft_question = ie_prompt_extract_role_name_e2e_template.format(EXAMPLE1=inc_example1, EXAMPLE2=inc_example2, FIELD=attribute, RELATED_CONTEXT=context, ROLE=ARRT, VALUE_RANGE=value_range)
        if pd.isna(answer):
            answer = 'Bad Information'
        ft_data.append({"instruction": "Given the context, extract the information", "input": ft_question, "output": str(answer)})

# Specify the filename
ft_data_path = "../../ftdata"
filename = 'e2e_ie_train.json'
file_path = os.path.join(ft_data_path, filename)
# Open the file in write mode
with open(file_path, 'w') as json_file:
    json.dump(ft_data, json_file)


inc_data_path = "../../incdata"
filename = 'e2e_ie_inc.json'
file_path = os.path.join(inc_data_path, filename)

# Write the list to the JSON file
with open(file_path, 'w') as json_file:
    json.dump(example_list, json_file)
