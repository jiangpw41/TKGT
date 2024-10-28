import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from numpy import isin
import plotly.graph_objects as go  
from typing import Dict, List

DEBUG_MODE = False
# Configure matplotlib to use a font that supports Chinese characters
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # or 'Microsoft YaHei'
matplotlib.rcParams['axes.unicode_minus'] = False  # Ensures that negative signs display correctly





class KnowledgeGraph():
    def __init__(self, schema, language="EN"):
        self.graph = nx.DiGraph()
        self.language = language
        self.domain_intro = schema["intro"]
        
        self.entity_type_info = schema["entity"]
        self.edge_type_info = schema["relation"]
       # 为方便查找，记录该图中所有同一类型的不同实例的ID
        self.instance_num = {}
        for key in self.entity_type_info.keys():
            number = self.entity_type_info[key]["number"]
            self.instance_num[key] = []
    
    ########################################## 增 ##########################################
    # 将self.entity_type_info嵌套列表变为空值字典结构，获取entity的空的知识图谱结构（有键，但值为None）
    def iter_get_kg_structure( self, dicts ):
        """
        输入：字典
        输出：字典
        """
        ret = {}
        for key, value in dicts.items():
            if isinstance( value, List):
                if isinstance( value[0], dict):                     # 列表中嵌套字典，说明是可迭代对象
                    ret[key] = {}
                    ret[key][1] = self.iter_get_kg_structure( value[0] )
                else:                                               # 列表中其他数据类型，说明是选项
                    ret[key] = {
                        "scope": value,
                        "value": None
                    }
            elif isinstance( value, dict):
                ret[key] = self.iter_get_kg_structure( value )     # 不是列表而直接是字典，说明是多级结构
            else:
                ret[key] = {
                        "scope": value,
                        "value": None
                    }                                     # 不是列表
        return ret
    
    # 向图中添加实体空结构（只有名字）：实体以类型+编号作为唯一性ID，需要检查当前数量
    def add_empty_entity(self, entity_type, entity_name):
        # First Column信息，只有实体类型和名称
        if DEBUG_MODE:
            print( f"构建{entity_type}的空结构。{entity_type}的基本情况如下：")
            print( f"数量：{self.entity_type_info[entity_type]['number']}" )
            print( f"介绍：{self.entity_type_info[entity_type]['intro']}" )
        
        entity_info = self.iter_get_kg_structure( self.entity_type_info[entity_type]["attributes"] )
        _name = "Name" if self.language=="EN" else "姓名名称"

        entity_info[_name]["value"] = entity_name
        if entity_type not in self.entity_type_info:
            raise Exception(f"Type {entity_type} not belongs to this graph of {self.entity_type_info}!")
        number = self.entity_type_info[entity_type]["number"]
        # 唯一性实体
        if number[0] == number[1]:
            entity_id = entity_type
            if self.graph.has_node( entity_type ):
                raise Exception(f"Type {entity_type} is a singleton and already exists!")
            else:
                self.graph.add_node( entity_id , **entity_info )
                self.instance_num[entity_type].append( entity_id )
                if DEBUG_MODE:
                    print( f"成功添加唯一性实体 {entity_type}，属性：{self.graph._node[entity_type]}")
        # 如果是有限范围且当前数量已满，则报错
        elif number[0] <= number[1] and len(self.instance_num[entity_type])==number[1]:
            raise Exception(f"Type {entity_type}'s number has already reached the maximum limit of {number[1]}!")
        # 否则添加实体
        else:
            entity_id = entity_type + f"_{ str( len(self.instance_num[entity_type])+1 ) }"
            self.instance_num[entity_type].append( entity_id )
            self.graph.add_node( entity_id , **entity_info )
            if DEBUG_MODE:
                print( f"成功添加实体 {entity_type}的第{len(self.instance_num[entity_type])}个实例，属性：{self.graph._node[entity_id]}")
    
    def add_relationship(self, entity1, entity2, attributes):
        """
        add directed relationship from entity1 to entity2
        """
        self.graph.add_edge(entity1, entity2, **attributes)
        if DEBUG_MODE:
            print( f"成功添加实体 {entity1} 与实体 {entity2} 的关系 {attributes}！")

    ########################################## 删 ##########################################
    # 删除实体
    def delete_entity(self, node_ids ):
        if isinstance(node_ids, str):
            self.graph.remove_node(node_ids)
            print(f"Node {node_ids} deleted!")
        elif isinstance(node_ids, List):
            self.graph.remove_nodes_from(node_ids)
            print(f"Nodes {node_ids} deleted!")
        else:
            raise Exception(f"Error: wrong node id format {node_ids}")
        
    # 删除关系
    def delete_relation(self, edges ):
        if isinstance(edges, tuple):
            self.graph.remove_node(edges)
            print(f"Edge {edges} deleted!")
        elif isinstance(edges, List):
            self.graph.remove_nodes_from(edges)
            print(f"Edges {edges} deleted!")
        else:
            raise Exception(f"Error: wrong node id format {edges}")
    
    ########################################## 查 ##########################################
    # 查询点和边的属性信息kg.graph._node["Defendant_1"]
    def get_info(self, query=None, single=True, node=True):
        "query为ID"
        if node:
            if single:
                if not isinstance(query, str):
                    raise Exception(f"String expected!")
                return self.graph._node[ query ]
            else:
                return self.graph._node
        else:
            if single:
                if not isinstance(query, tuple):
                    raise Exception(f"Tuple expected!")
                return self.graph.get_edge_data( query[0], query[1] )
            else:
                return self.graph.edges(data=True)
  
    # 返回所有点实例的未填充属性
    def get_unfilled_labels(self):
        unfilled = {}
        for node_id, data in self.graph.nodes(data=True):
            missing_labels = {label: val for label, val in data.items() if val is None}
            if missing_labels:
                unfilled[node_id] = missing_labels
        return unfilled
    
    # 点和边存在性检查
    def exist_check(self, query, node=True ):
        if node:
            if not isinstance(query, str):
                raise Exception(f"String expected!")
            return self.graph.has_node(query)
        else:
            if not isinstance(query, tuple):
                raise Exception(f"Tuple expected!")
            return self.graph.has_edge( query[0], query[1] )
    
    ########################################## 改 ##########################################
    # 修改标签值
    def update_entity(self, entity_id, label, label_value):
        """
        Update the value of label for entity
        """
        if entity_id in self.graph:
            if label in self.graph.nodes[entity_id]:
                self.graph.nodes[entity_id][label]["value"] = label_value
            else:
                raise KeyError(f"Label '{label}' does not exist for entity '{entity_id}'.")
        else:
            raise KeyError(f"No entity found with ID '{entity_id}'.")

    ######################################## 算法应用 ##########################################
    # 获取下一个抽取实体
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

    # 获取改抽取实体的标签
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

    # 描述KG全局
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

    # 描述实体
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

    # 可视化
    def visualize_knowledge_graph( self ):
        pos = nx.spring_layout(self.graph)  # positions for all nodes
        labels = {node: ', '.join([f"{key}: {data[key]}" for key in data]) for node, data in self.graph.nodes(data=True)}
        nx.draw(self.graph, pos, labels=labels, with_labels=True, node_color='skyblue', node_size=2000, edge_color='k', linewidths=1, font_size=15)
        edge_labels = {(u, v): ', '.join([f"{key}: {data[key]}" for key in data if key in ['relationship', 'since']]) for u, v, data in self.graph.edges(data=True)}
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        
        plt.show()

    def visualize_knowledge_graph_interactive(self):
        pos = nx.kamada_kawai_layout(self.graph)
        # For edges
        edge_x, edge_y, edge_hovertext = [], [], []
        for edge in self.graph.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append((x0 + x1) / 2)
            edge_y.append((y0 + y1) / 2)
            edge_hovertext.append('<br>'.join([f"{key}: {value}" for key, value in edge[2].items()]))

        edge_trace = go.Scatter(x=edge_x, y=edge_y, text=edge_hovertext,
                                mode='markers', hoverinfo='text',
                                marker=dict(size=1, color='rgba(0,0,0,0)'))

        # For nodes
        node_x = [pos[node][0] for node in self.graph.nodes()]
        node_y = [pos[node][1] for node in self.graph.nodes()]
        node_info = ['<br>'.join([f"{key}: {value}" for key, value in data.items()]) for node, data in self.graph.nodes(data=True)]
        node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text',
                                text=[data.get('name', 'Unnamed Entity') for node, data in self.graph.nodes(data=True)],
                                marker=dict(showscale=True, colorscale='YlGnBu', size=10),
                                textposition="bottom center", hoverinfo='text', hovertext=node_info)

        line_trace = go.Scatter(x=[x for sublist in [[pos[edge[0]][0], pos[edge[1]][0], None] for edge in self.graph.edges()] for x in sublist],
                                y=[y for sublist in [[pos[edge[0]][1], pos[edge[1]][1], None] for edge in self.graph.edges()] for y in sublist],
                                line=dict(width=2, color='#888'), mode='lines')

        fig = go.Figure(data=[line_trace, node_trace, edge_trace], layout=go.Layout(showlegend=False, hovermode='closest', margin=dict(b=0, l=0, r=0, t=0),
                                                                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                                                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        fig.show()


class DomainKnowledgeGraph( KnowledgeGraph ):
    def __init__(self, schema, language="EN"):
        super().__init__(schema, language=language)  # 调用父类的构造函数
        self.entity_type = schema["entity_type"]
        self.event_type = schema["event_type"]
    
    def str_scope( self, scope):
        if isinstance( scope, list):
            if self.language == "EN":
                options = ", ".join(scope)
            elif self.language == "ZH":
                options = "，".join(scope)
            return f"[{options}]"
        else:
            return str(scope)
    
    # 查询一个实体类的所有对象的名称，返回以字符串形式
    def get_objects( self, entity ):
        # 获取该实体类型所有对象的名称
        names = []
        name_ = "Name" if self.language=="EN" else "姓名名称"
        for entity_num in self.instance_num[entity]:
            names.append( self.get_info( query=entity_num, single=True, node=True)[name_]["value"] )
        if len(names) == 1 and names[0]==None:
            entity_answer = "<NOT FOUND>"
        else:
            if self.language == "ZH":
                entity_answer = "、".join( names )
            else:
                entity_answer = ", ".join( names )
        return entity_answer
    
    # 迭代，每次返回一个当前实体的属性target_attr, 取值范围scopes, 以及实例在该属性上的真实标签answer 
    def nested_iterator( self, entity_attr_info, part_mode):  
        def _recursive_yield(prefix, dicts):  
            for key, value in dicts.items():
                """传入是字典
                如果类型是字符串、整数等，说明到底；
                如果是列表
                    列表中是字符串、整数，也到底
                    列表中是字典，说明是可迭代嵌套对象，并以整数标号
                如果是字典：
                    说明是不可迭代的嵌套
                """
                if isinstance(value, dict):
                    new_prefix = prefix+f"<SPLIT>{key}" if prefix!="" else key
                    if len(value.keys())==2 and "scope" in value.keys() and "value" in value.keys():   # 触底，返回值
                        answer = value["value"] if value["value"]!=None else "<NOT FOUND>"
                        if part_mode=="all":
                            yield new_prefix, self.str_scope(value["scope"]), self.str_scope(answer)
                        elif part_mode=="name" and key in ["Name", "姓名名称"]:
                            yield new_prefix, self.str_scope(value["scope"]), self.str_scope(answer)
                        elif part_mode=="cell" and key not in ["Name", "姓名名称"]:
                            yield new_prefix, self.str_scope(value["scope"]), self.str_scope(answer)
                    else:                                                                           # 字典后面要么为1（可多次的属性类），要么直接是多个键值对
                        yield from _recursive_yield(new_prefix, value)
                else:
                    raise Exception( f"对象的属性值类型不合法！")

        # 开始递归生成  
        yield from _recursive_yield("", entity_attr_info)  
    
    # 返回迭代器
    def get_attr_iter( self, entity_num, part_mode ):
        """
        part_mode: 指示迭代什么要素，可以all（e2e），name（FirstColumn），cell（DataCell）
        """
        attr_info = self.graph._node[entity_num]
        iterator = self.nested_iterator(attr_info, part_mode) 
        return iterator
    
    def add_from_tuple( self, tuple_list, multi_entity, if_train):
        entity_list = []
        attri_relation = []
        if multi_entity:        
            for item in tuple_list:
                if len(item) == 2:
                    if "）_" in item[0]:
                        item = ( item[0].split("_")[0], item[1])
                    entity_list.append( item )
                elif len(item) == 3:
                    attri_relation.append( item )
                else:
                    raise Exception(f"add_from_tuple函数不接收{len(item)}元组")
        else:
            entity_list = [ (list(self.entity_type_info.keys() )[0], None)]
            for item in tuple_list:
                attri_relation.append( (entity_list[0][0], item[0], item[1]) )
        
        for item in entity_list:
            self.add_empty_entity(item[0], item[1])
        
        all_nodes = self.get_info( query=None, single=False, node=True)
        for item in attri_relation:
            name, field, field_value = item
            if multi_entity:
                for entity_num in all_nodes.keys():
                    _name = all_nodes[entity_num]["Name"] if self.language=="EN" else all_nodes[entity_num]["姓名名称"]
                    if _name["value"] == name:
                        self.update_entity( entity_num, field, field_value)
                        break
            else:
                if if_train:
                    self.update_entity( name, field, field_value)

    def add_from_no_tuple( self, multi_entity, if_train):
        entity_type_list = list(self.entity_type_info.keys() )
        for entity_type in entity_type_list:
            self.add_from_tuple( {(entity_type, None)}, multi_entity, if_train)