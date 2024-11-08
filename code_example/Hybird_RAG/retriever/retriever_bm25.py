from rank_bm25 import BM25Okapi
import heapq
from typing import List
import jieba
import numpy as np

from llama_index.retrievers.bm25 import BM25Retriever       # !pip install llama-index-retrievers-bm25

"""持久化

bm25_retriever = BM25Retriever.from_persist_dir( "/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/retriever/bm25" )
bm25_retriever.persist("/home/jiangpeiwen2/jiangpeiwen2/TKGT/Hybird_RAG/retriever/bm25")
from_persist_dir(path: str, **kwargs: Any) -> BM25Retriever
"""
def chinese_tokenizer( text: str) -> List[str]:
    return list(jieba.cut(text))


class Llamaindex_BM25_Retriever( ):
    def __init__(self, index, topk = 2):
        docstore = index.docstore
        self.topk = topk
        self.bm25_retriever =  BM25Retriever.from_defaults(
            docstore=docstore, similarity_top_k=topk, verbose=True,
            tokenizer=chinese_tokenizer,
            language="zh"
        )

    def retrieve( self, query):
        return self.bm25_retriever.retrieve( query )

class Rank_BM25_Retriever( ):
    def __init__(self, node_list, similarity_top_k = 2, score = 0.7):
        self.topk = similarity_top_k
        self.score = score
        self.text_list = self.from_nodes_to_list( node_list )
        corpus = [ chinese_tokenizer( sentence ) for sentence in self.text_list]
        try:
            self.retriever = BM25Okapi( corpus ) if len(corpus) > 0 else None
        except:
            raise Exception(corpus)
        
    
    def from_nodes_to_list( self, nodes_list ):
        ret_list = []
        for node in nodes_list:
            ret_list.append( node.text )
        return ret_list
    
    def retrieve( self, query):
        tokenized_query = chinese_tokenizer( query )
        if self.retriever==None:
            return []
        doc_scores = self.retriever.get_scores( tokenized_query )
        top_k_values, top_k_indices = self.find_top_k_elements(doc_scores, self.topk)

        max_abs_val = np.max(np.abs(top_k_values))  
        normalized_top_k_values = top_k_values / max_abs_val
        ret = []
        for i in range( len( normalized_top_k_values)):
            sentence = self.text_list[ top_k_indices[i] ]
            score = normalized_top_k_values[i]
            if score>= self.score:
                ret.append( {"text": sentence, "score": score})
        return ret

    def find_top_k_elements( self, array, topk):  
        # 使用一个列表来存储元素及其索引的元组  
        indexed_array = [(value, index) for index, value in enumerate(array)]  
        
        # 使用 heapq.nlargest 找到前 k 个最大的元素及其索引  
        top_k_elements = heapq.nlargest(topk, indexed_array, key=lambda x: x[0])  
        
        # 提取值和索引  
        top_k_values = [element[0] for element in top_k_elements]  
        top_k_indices = [element[1] for element in top_k_elements]  
        
        return top_k_values, top_k_indices