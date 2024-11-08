

from llama_index.core import Settings, Document, load_index_from_storage
from llama_index.core.schema import TextNode 
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import StorageContext
# from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import KeywordTableIndex
from llama_index.core.retrievers import KeywordTableSimpleRetriever, VectorIndexRetriever     # 所有retrievers中只有一个keyword相关的
from llama_index.core import VectorStoreIndex
import os
from tqdm import tqdm
import sys
import os
import re
from typing import List

from modelscope.models import Model
from modelscope.pipelines import pipeline
# Version less than 1.1 please use TextRankingPreprocessor
from modelscope.preprocessors import TextRankingTransformersPreprocessor
from modelscope.utils.constant import Tasks


################################################### 全局变量设置与本地导入 #######################################################

_ROOTR_PATH = os.path.abspath(__file__)
for _ in range(3):
    _ROOTR_PATH = os.path.dirname( _ROOTR_PATH )
sys.path.insert(0, _ROOTR_PATH)

from utils import load_data
from Hybird_RAG.retriever.retriever_bm25 import Llamaindex_BM25_Retriever, Rank_BM25_Retriever
from date_capture import CplParagraphSplitSimple
from Hybird_RAG.retriever.TextsLoader import CplDataLoader
from Hybird_RAG.retriever.cpl_utils import get_node_list
from Hybird_RAG.retriever.retriever_keyword_rule import CplKeywordRuleRetriever



"""
llm = HuggingFaceLLM(
    model_name="/home/jiangpeiwen2/jiangpeiwen2/LlamaIndex/model/chatglm3-6b",
    tokenizer_name="/home/jiangpeiwen2/jiangpeiwen2/LlamaIndex/model/chatglm3-6b",
    model_kwargs={"trust_remote_code":True},
    tokenizer_kwargs={"trust_remote_code":True}
)
"""
#设置全局的llm属性，这样在索引查询时会使用这个模型。



################################################### 类定义 #######################################################
class CPL_Hybrid_Retriever( ):
    def __init__(self, ruled_text, attr_type, entity_type, max_ratio = 0.1, 
                ban_list = [ 1, 0, 1, 1, 0],
                topk = 2,
                score = 0.7,
                gpu_id = 0
                ):
        """
        ruled_text: 一份cpl的规则处理数据
        attr_type: 针对每个文档的每个字段
        entity_type: 每个角色
        max_ratio：混合检索返回的句子数量占全部句子数的最大比例，默认为0.1
        ban_list：对应下面五个检索器，为1表示使用，0表示不使用
        topk: 每个auto检索器返回的数量
        score: 门槛值
        """
        self.gpu_id = gpu_id
        os.environ["CUDA_VISIBLE_DEVICES"]  = str(gpu_id)
        embed_model = HuggingFaceEmbedding(
            model_name="/home/jiangpeiwen2/jiangpeiwen2/LlamaIndex/model/sentence-transformer"
        )
        Settings.embed_model = embed_model
        Settings.llm = None

        self.attr_type = attr_type
        self.text_list = ruled_text
        self.entity_type = entity_type
        self.ban_list = ban_list
        self.topk = topk
        self.score = score
        nodes_list, vector_index, keyword_index = self.prepare()
        self.topk_total = 2    #max(2, int( max_ratio* len(nodes_list) ))                 # 最大可返回的句子数量，最少两个
        # 五个检索器实例化
        self.rule_keyword_retriever = CplKeywordRuleRetriever( ruled_text )
        #self.keyword_retriever = KeywordTableSimpleRetriever(index=keyword_index, similarity_top_k = self.topk)
        self.vector_retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=self.topk, score = self.score)
        self.rank_bm25_retriever = Rank_BM25_Retriever( nodes_list, similarity_top_k=self.topk, score = self.score)
        #self.llamaindex_bm25_retriever = Llamaindex_BM25_Retriever( vector_index)

        # rerank
        self.reranker = pipeline(task=Tasks.text_ranking, model='damo/nlp_rom_passage-ranking_chinese-base', model_revision='v1.1.0')  # 
        # 检索结果：为了更好控制分为两部分
        self.auto_results_list = None
        self.rule_results_list = None
    
    def type_filter(self, nodes_list):
        ret_nodes = []
        for node in nodes_list:
            flag = 0
            if self.attr_type == "date":
                pattern_date = re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日")
                matched_words_date = re.findall(pattern_date, node.text)
                if len( matched_words_date )>0:
                    flag = 1
            elif self.attr_type == "money":
                pattern_yuan = re.compile(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:万)?元')
                matched_words_yuan = re.findall(pattern_yuan, node.text)
                if len( matched_words_yuan )>0:
                    flag = 1
            elif self.attr_type == "ratio" and "%" in node.text:
                flag = 1
            
            if flag==1:
                ret_nodes.append( node )
        return ret_nodes

    def prepare( self ):
        doc = CplParagraphSplitSimple( self.text_list )
        totol_nodes_list, map_list = get_node_list( doc.sentence_doc )
        nodes_list = []
        indexes = map_list[ self.entity_type ]
        try:
            nodes_list = [ totol_nodes_list[ int(index) ] for index in indexes ]
        except:
            raise Exception( indexes )
        storage_context = StorageContext.from_defaults()
        nodes_list = self.type_filter( nodes_list )
        storage_context.docstore.add_documents(nodes_list)
        keyword_index = KeywordTableIndex(nodes_list, storage_context=storage_context)
        vector_index = VectorStoreIndex(nodes_list, storage_context=storage_context)
        return nodes_list, vector_index, keyword_index
    
    def llama_index_results_append( self, sub_results, rule_results_list, auto_results_list):
        for i in range(len(sub_results)):
            if sub_results[i].text not in rule_results_list and sub_results[i].text not in auto_results_list:
                auto_results_list.append( sub_results[i].text )
        return auto_results_list

    def hybrid_retrieve( self, query, entity, attr):
        os.environ["CUDA_VISIBLE_DEVICES"]  = str(self.gpu_id)
        auto_results_list = []
        rule_results_list = []
        if self.ban_list[0]:
            rule_keyword_results = self.rule_keyword_retriever.retrieve( entity, attr )     # cpl规则keyword检索
            rule_results_list.extend( rule_keyword_results )
        if self.ban_list[1]:
            keyword_results = self.keyword_retriever.retrieve( query )                      # llama-index的keyword检索接口，效果不太好
            auto_results_list = self.llama_index_results_append( keyword_results, rule_results_list, auto_results_list)
        if self.ban_list[2]:
            vector_results = self.vector_retriever.retrieve( query )                        # 向量检索
            auto_results_list = self.llama_index_results_append( vector_results, rule_results_list, auto_results_list)
        if self.ban_list[3]:
            rank_bm25_results = self.rank_bm25_retriever.retrieve( query )                  # rank bm25
            for i in range(len(rank_bm25_results)):
                if rank_bm25_results[i]["text"] not in auto_results_list:
                    auto_results_list.append( rank_bm25_results[i]["text"] )
        if self.ban_list[4]:
            llamaindex_bm25_results = self.llamaindex_bm25_retriever.retrieve( query )      # llama-index的 bm25接口，效果不太好
            auto_results_list = self.llama_index_results_append( llamaindex_bm25_results, rule_results_list, auto_results_list)
        self.auto_results_list = auto_results_list
        self.rule_results_list = rule_results_list
        return self.re_rank( query )
    
    @classmethod
    def top_k_indices( cls, nums, k):
        if not isinstance(nums, list) or not all(isinstance(x, (int, float)) for x in nums):
            raise ValueError("nums 必须是一个浮点数列表")
        if not isinstance(k, int) or k <= 0:
            raise ValueError("k 必须是一个正整数")
        sorted_indices = sorted(range(len(nums)), key=lambda i: nums[i], reverse=True)
        return sorted_indices[: min(k, len(nums))]
    
    def get_rerank_top( self, results_list, results_list_rerank, topk=2):
        indexs = CPL_Hybrid_Retriever.top_k_indices( results_list_rerank, topk)
        ret_list = []
        for i in range( len(indexs) ):
            ret_list.append( results_list[indexs[i]]  )
        return ret_list
    
    def re_rank( self, query ):
        auto_inputs = {
            'source_sentence': [query],
            'sentences_to_compare': self.auto_results_list
        }
        rule_inputs = {
            'source_sentence': [query],
            'sentences_to_compare': self.rule_results_list
        }
        auto_results_list_rerank = self.reranker(input=auto_inputs)['scores'] if len(self.auto_results_list)>0 else []
        rule_results_list_rerank = self.reranker(input=rule_inputs)['scores'] if len(self.rule_results_list)>0 else []
        auto_results = self.get_rerank_top( self.auto_results_list, auto_results_list_rerank, self.topk_total)
        rule_results = self.get_rerank_top( self.rule_results_list, rule_results_list_rerank, 2)
        ret = []
        ret.extend(rule_results)
        ret.extend(auto_results)
        return ret
                
    
    @classmethod
    def cpl_batch_process( cls, part = "test"):
        cpl_data = CplDataLoader( "cpl", "text_ruled.json", part )
        tests = cpl_data.rule_texts
        return tests