from llama_index.core import StorageContext
from llama_index.core import load_index_from_storage
from llama_index.core.retrievers import KeywordTableSimpleRetriever     # 所有retrievers中只有一个keyword相关的
from llama_index.core import KeywordTableIndex
from tqdm import tqdm

import os
import sys
from collections import OrderedDict

_ROOT_PATH = os.path.abspath(__file__)
for _ in range(3):
    _ROOT_PATH = os.path.dirname( _ROOT_PATH )
sys.path.insert(0, _ROOT_PATH)


# 持久化或加载Index
def load_or_persist( path, keyword_index=None):
    """
    path: 该文档对应的索引存放的目录名
    keyword_index: 索引本体
    """
    if keyword_index == None:
        storage_context = StorageContext.from_defaults(persist_dir=path)
        index = load_index_from_storage(storage_context)
        return index
    else:
        keyword_index.storage_context.persist( persist_dir=path )

# 加载全部persist的index
def get_persist_index( length=203 ):
    ret = []
    for i in tqdm( range( length ), desc=f"加载持久化keyword index"):
        path =  f"/home/jiangpeiwen2/jiangpeiwen2/HybirdRetriever/persist_store/{i}"
        ret.append( load_or_persist( path) )
    return ret

