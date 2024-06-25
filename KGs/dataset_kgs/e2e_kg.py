from collections import OrderedDict
import os
import sys

_ROOT_PATH = os.path.abspath(__file__)
for i in range(4):
    _ROOT_PATH = os.path.dirname( _ROOT_PATH )
sys.path.insert(0, _ROOT_PATH)
from utils import KnowledgeGraph

e2e_value_range = {
    'String_Name' : str,
    'Price range' : ['More than £30', 'Cheap', 'Less than £20', '£20-25', 'Moderate', 'High'],            # 价格范围，6选1
    'Customer rating' : ['5 out of 5', 'Low', 'Average', '3 out of 5', '1 out of 5', 'High'],        # 用户评价：6选1
    'Food' : ['Japanese', 'French', 'English', 'Fast food', 'Italian', 'Indian', 'Chinese'],                   # 食物类型：7选1
    'Area' : ['Riverside', 'City centre'],                   # 地区：2选1 
    'Family friendly' : ['Yes', 'No']         # 是否家庭友好：2选1
}

# Table columns and value range
_col_name_value = OrderedDict({
    'Name' : e2e_value_range['String_Name'],                                                                                    # 餐厅名，理论上字符串无限，数据集有限
    'Price range' : e2e_value_range['Price range'],        # 价格范围，6选1
    'Customer rating' : e2e_value_range['Customer rating'],         # 用户评价：6选1
    'Near' : e2e_value_range['String_Name'],                                                                                    # 附近标识（地点），理论上字符串无限，数据集有限
    'Food' : e2e_value_range['Food'],          # 食物类型：7选1
    'Area' : e2e_value_range['Area'],                                                            # 地区：2选1
    'Family friendly' : e2e_value_range['Family friendly']                                                                 # 是否家庭友好：2选1
})
'''
e2e_kg = KnowledgeGraph()
e2e_kg.add_entity('entity1', { key:None for key in _col_name_value})
get_unfilled_labels = e2e_kg.get_unfilled_labels()
print(get_unfilled_labels)
'''