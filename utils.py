import logging
import networkx as nx
import json
import pickle
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import random


from tqdm import tqdm
import concurrent
from concurrent.futures import ProcessPoolExecutor

# Configure matplotlib to use a font that supports Chinese characters
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # or 'Microsoft YaHei'
matplotlib.rcParams['axes.unicode_minus'] = False  # Ensures that negative signs display correctly


_PUNCATUATION_EN = [',', '.', ';', '?', '!', '…', ":", '"', '"', "'", "'", "(", ")", ]
_PUNCATUATION_ZH = ['，', '。', '；', '？', '！', '......', "：",  '“', '”', '‘', '’', '（', '）', '《', '》', '【', '】', '[', ']', '、', "\\n"]

def multi_process( processor, task_list, task_description, *args ):
    # 所有使用多进程工具的函数，必须将迭代对象及其index作为函数参数的前两位
    splited_task_list = [None]*len(task_list)
    error_reading = 0
    count = 0
    with ProcessPoolExecutor() as executor:
        future_to_item = {}
        for j, item in enumerate(task_list):
            future_to_item[executor.submit(processor, item, j, *args)] = j 
        with tqdm(total=len(future_to_item), desc=f"Preprocess {task_description}") as pbar:
            for future in concurrent.futures.as_completed(future_to_item): 
                line = future.result()
                count += 1
                if line=={} or line=="":
                    error_reading += 1
                splited_task_list[ future_to_item[future]] = future.result()
                pbar.update(1)
    return splited_task_list, error_reading, count

def create_logger( log_name, save_path_name, level=1 ):
    # Ceate and determine its level
    levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
    logger = logging.getLogger(log_name)
    logger.setLevel( levels[level] )  
    
    # Create a FileHandler for writing log files 
    file_handler = logging.FileHandler( save_path_name, encoding='utf-8' )  
    file_handler.setLevel( levels[level] )  
    
    # Create a StreamHandler for outputting to the console  
    console_handler = logging.StreamHandler()  
    console_handler.setLevel( levels[level] )  
    
    # Define the output format of the handler 
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    file_handler.setFormatter(formatter)  
    console_handler.setFormatter(formatter)  
    
    # Add Handler to Logger
    logger.addHandler(file_handler)  
    logger.addHandler(console_handler)  

    return logger

def visualize_knowledge_graph(kg):
    pos = nx.spring_layout(kg.graph)  # positions for all nodes
    labels = {node: ', '.join([f"{key}: {data[key]}" for key in data]) for node, data in kg.graph.nodes(data=True)}
    nx.draw(kg.graph, pos, labels=labels, with_labels=True, node_color='skyblue', node_size=2000, edge_color='k', linewidths=1, font_size=15)
    edge_labels = {(u, v): ', '.join([f"{key}: {data[key]}" for key in data if key in ['relationship', 'since']]) for u, v, data in kg.graph.edges(data=True)}
    nx.draw_networkx_edge_labels(kg.graph, pos, edge_labels=edge_labels)
    
    plt.show()

def visualize_knowledge_graph_interactive(kg):
    pos = nx.kamada_kawai_layout(kg.graph)  # Optimal layout for visibility

    # For edges
    edge_x = []
    edge_y = []
    edge_hovertext = []  # List to store hover text for each edge

    for edge in kg.graph.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append((x0 + x1) / 2)  # Middle of the edge for the text
        edge_y.append((y0 + y1) / 2)
        # Format the hover text for the edges
        edge_hovertext.append('<br>'.join([f"{key}: {value}" for key, value in edge[2].items()]))

    # Invisible edge traces for better hover interaction
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        text=edge_hovertext,
        mode='markers',
        hoverinfo='text',
        marker=dict(size=1, color='rgba(0,0,0,0)'),  # Invisible markers
        hoverlabel=dict(namelength=-1))

    # For nodes
    node_x = [pos[node][0] for node in kg.graph.nodes()]
    node_y = [pos[node][1] for node in kg.graph.nodes()]
    node_info = ['<br>'.join([f"{key}: {value}" for key, value in data.items()]) for node, data in kg.graph.nodes(data=True)]

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[data['name'] for node, data in kg.graph.nodes(data=True)],
        marker=dict(showscale=True, colorscale='YlGnBu', size=10, color=[], line_width=2),
        textposition="bottom center",
        hoverinfo='text',
        hovertext=node_info)

    # Line trace for visible edges
    line_x = []
    line_y = []
    for edge in kg.graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        line_x.extend([x0, x1, None])
        line_y.extend([y0, y1, None])
    line_trace = go.Scatter(
        x=line_x, y=line_y,
        line=dict(width=2, color='#888'),
        mode='lines',
        hoverinfo='none')

    fig = go.Figure(data=[line_trace, node_trace, edge_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=0),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.show()


def save_data( data, path ):
    type = path.split(".")[-1]
    if type == "text":
        with open( path, 'w') as file:
            for i in range(len(data)):
                line = data[i]
                file.write(line + '\n')
    elif type == "json":
        with open( path, "w", encoding="utf-8") as f:
            json.dump( data, f,  ensure_ascii=False, indent=4)
    elif type == "pickle":
        with open( path, "wb") as f:
            pickle.dump( data, f )
    else:
        raise Exception(f"{type}类型数据目前无法使用save_data保存")

def load_data( path, type, header_None=False, sheet_name=False):
    if type == "text":
        texts = []
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                texts.append(line.strip())
        return texts
    elif type == "json":
        with open( path, "r", encoding="utf-8") as f:
            datas = json.load( f)
        return datas
    elif type == "pickle":
        with open( path, "rb") as f:
            datas = pickle.load( f)
        return datas
    elif type == "excel":
        if header_None:
            if sheet_name:
                return pd.read_excel( path, header=None, sheet_name=sheet_name )
            else:
                return pd.read_excel( path, header=None )
        else:
            if sheet_name:
                return pd.read_excel( path, sheet_name=sheet_name)
            else:
                return pd.read_excel( path)

def read_text_to_list( path ):
    with open(path, 'r') as file:  
        lines = file.readlines()
    strings_read = []
    for line in lines:
        if line.endswith("\n"):
            line = line[:-1]
        strings_read.append( line )
    return strings_read

class CustomError(Exception):  
    def __init__(self, message, logger):  
        super().__init__(message)  
        if logger:  
            logger.error(message)


class SingletonLogger:  
    _instances = {}  
    @classmethod  
    def get_logger(cls, log_name, save_path_name, level=1):  
        if log_name not in cls._instances:  
            levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]  
            logger = logging.getLogger(log_name)  
            logger.setLevel(levels[level])  
  
            file_handler = logging.FileHandler(save_path_name, encoding='utf-8')  
            file_handler.setLevel(levels[level])  
  
            console_handler = logging.StreamHandler()  
            console_handler.setLevel(levels[level])  
  
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
            file_handler.setFormatter(formatter)  
            console_handler.setFormatter(formatter)  
  
            logger.addHandler(file_handler)  
            logger.addHandler(console_handler)  
  
            cls._instances[log_name] = logger  
  
        return cls._instances[log_name]


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