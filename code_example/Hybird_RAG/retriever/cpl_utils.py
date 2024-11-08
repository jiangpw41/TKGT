from tqdm import tqdm
import sys
import os
from llama_index.core.schema import TextNode
from llama_index.core import StorageContext
from llama_index.core import KeywordTableIndex
from llama_index.core import load_index_from_storage
from copy import deepcopy
from tqdm import tqdm

from llama_index.core import Settings, Document, load_index_from_storage

_ROOT_PATH = os.path.abspath(__file__)
for i in range(3):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert(0, _ROOT_PATH)
from Hybird_RAG.retriever.utils_retriever import load_or_persist





# 向index的关键字索引添加cpl每个字段指定的关键字
def add_keywords( keyword_index, keywords):
    
    add_dict = {}
    for j in range(len(keyword_index.storage_context.docstore.docs)):
        text = keyword_index.storage_context.docstore.docs[ str(j) ].text
        for keyword in keywords:
            if keyword in text:
                if keyword not in add_dict:
                    add_dict[ keyword ] = set()
                add_dict[ keyword ].add( str(j))
    add_dict_not = {}
    for key in add_dict.keys():
        if key not in keyword_index.index_struct.table:
            add_dict_not[key] = add_dict[key]
        else:
            keyword_index.index_struct.table[key].update( add_dict[key] )
    keyword_index.index_struct.table.update( add_dict_not )
    return keyword_index

# 从核心文本中构建Nodes:id为编号,text为文本，同时返回node属于哪部分的映射用于关键字索引

def get_node_list( ruled_text ):
    part_map = {
        "原告":[],
        "被告":[],
        "法院":[],
    }
    nodes = []
    for key in ruled_text.keys():
        list_ = ruled_text[key]
        for j in range(len(list_)):
            metadata={ "角色": key}
            ids = str( len(nodes) )
            node = TextNode( text=list_[j], id_=  ids, metadata=metadata)
            nodes.append( node )
            part_map[key].append( ids )
    return nodes, part_map


def get_nodes_list( ruled_core_list ):
    map_list = []
    nodes_list = []
    for i in range( len(ruled_core_list) ):
        part_map = {
            "原告":[],
            "被告":[],
            "法院":[],
        }
        ruled_text = ruled_core_list[i]
        nodes = []
        for key in ruled_text.keys():
            list_ = ruled_text[key]
            for j in range(len(list_)):
                metadata={ "角色": key}
                ids = str( len(nodes) )
                node = TextNode( text=list_[j], id_=  ids, metadata=metadata)
                nodes.append( node )
                part_map[key].append( ids )
        nodes_list.append( nodes )
        map_list.append( part_map )
    return nodes_list, map_list

"""
documents = Document( text=text, id_="0")
parser = SentenceSplitter( chunk_size=200, chunk_overlap=10)
nodes = parser.get_nodes_from_documents([documents])
nodes_list, map_list = get_nodes_list( ruled_core_list )
"""
# 构建KeywordTableIndex，并将角色索引加入关键词表
def construct_keyword_index_store( nodes, maps):
    storage_context = StorageContext.from_defaults()
    storage_context.docstore.add_documents(nodes)           # 保存nodes中的文本，storage_context.docstore.docs
    keyword_index = KeywordTableIndex(nodes, storage_context=storage_context)
    keyword_index.index_struct.table.update( maps )         # keyword_index.index_struct.table查看索引
    keywords = get_cpl_keyword()
    keyword_index = add_keywords( keyword_index, keywords)
    
    return keyword_index


if __name__=="__main__":
    # 加载embedding模型和llm
    
    part = "train"
    """
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    embed_model = HuggingFaceEmbedding(
        model_name= os.path.join( _ROOT_PATH, "Hybird_RAG/retriever/embed_model/sentence-transformer")
    )

    Settings.embed_model = embed_model
    llm = HuggingFaceLLM(
        model_name="/home/jiangpeiwen2/jiangpeiwen2/LlamaIndex/model/chatglm3-6b",
        tokenizer_name="/home/jiangpeiwen2/jiangpeiwen2/LlamaIndex/model/chatglm3-6b",
        model_kwargs={"trust_remote_code":True},
        tokenizer_kwargs={"trust_remote_code":True}
    )
    #设置全局的llm属性，这样在索引查询时会使用这个模型。
    Settings.llm = llm
    """
    ruled_core_list = get_ruled_core_cpl( part )
    nodes_list, map_list = get_nodes_list( ruled_core_list )
    keyword_index_list = []
    for i in tqdm( range( len(nodes_list) ), desc=f"持久化keyword index"):
        keyword_index = construct_keyword_index_store( nodes_list[i], map_list[i])
        keyword_index_list.append( keyword_index )
        path = os.path.join( _ROOT_PATH, f"Hybird_RAG/retriever/persist_store/cpl/{part}/{i}" )
        load_or_persist( path, keyword_index)

    keywords = get_cpl_keyword(  )