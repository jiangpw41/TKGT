import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go  
import matplotlib

# Configure matplotlib to use a font that supports Chinese characters
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # or 'Microsoft YaHei'
matplotlib.rcParams['axes.unicode_minus'] = False  # Ensures that negative signs display correctly


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

    def update_entity(self, entity_id, updates):
        if entity_id in self.graph:
            self.graph.nodes[entity_id].update(updates)
        else:
            raise KeyError(f"No entity found with ID {entity_id}")

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
        self.graph.add_edge(entity1, entity2, **attributes)

    

def visualize_knowledge_graph(kg):
    pos = nx.spring_layout(kg.graph)  # positions for all nodes
    labels = {node: ', '.join([f"{key}: {data[key]}" for key in data]) for node, data in kg.graph.nodes(data=True)}
    nx.draw(kg.graph, pos, labels=labels, with_labels=True, node_color='skyblue', node_size=2000, edge_color='k', linewidths=1, font_size=15)
    edge_labels = {(u, v): ', '.join([f"{key}: {data[key]}" for key in data if key in ['relationship', 'since']]) for u, v, data in kg.graph.edges(data=True)}
    nx.draw_networkx_edge_labels(kg.graph, pos, edge_labels=edge_labels)
    plt.show()
    


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

    
    
