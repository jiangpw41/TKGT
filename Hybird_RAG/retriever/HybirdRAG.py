import os
import sys
from collections import OrderedDict

_ROOT_PATH = os.path.abspath(__file__)
for _ in range(3):
    _ROOT_PATH = os.path.dirname( _ROOT_PATH )
sys.path.insert(0, _ROOT_PATH)
from data.data_manager import data_split

def HybirdRAG_v1( ):
    return ""


if __name__=="__main__":
    HybirdRAG_v1( )