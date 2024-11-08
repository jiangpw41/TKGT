from collections import OrderedDict
from math import e

__all__=["e2e_kg_schema"]

_e2e_value_range_old = {
    'String_Name' : str,
    'Price range' : ['More than £30', 'Cheap', 'Less than £20', '£20-25', 'Moderate', 'High'],            # 价格范围，6选1
    'Customer rating' : ['5 out of 5', 'Low', 'Average', '3 out of 5', '1 out of 5', 'High'],        # 用户评价：6选1
    'Food' : ['Japanese', 'French', 'English', 'Fast food', 'Italian', 'Indian', 'Chinese'],                   # 食物类型：7选1
    'Area' : ['Riverside', 'City centre'],                                                              # 地区：2选1 
    'Family friendly' : ['Yes', 'No']                                                                   # 是否家庭友好：2选1
}

_e2e_value_range = {
    'String_Name' : str,
    'Price range' : ['Cheap', 'Moderate', 'High'],            # 价格范围，6选1
    'Customer rating' : ['Low', 'Average', 'High'],        # 用户评价：6选1
    'Food' : ['Japanese', 'French', 'English', 'Fast food', 'Italian', 'Indian', 'Chinese'],                   # 食物类型：7选1
    'Area' : ['Riverside', 'City centre'],                                                              # 地区：2选1 
    'Family friendly' : ['Yes', 'No']                                                                   # 是否家庭友好：2选1
}

# Table columns and value range
_col_name_value = OrderedDict({
    'Name' : _e2e_value_range['String_Name'],                                                                                    # 餐厅名，理论上字符串无限，数据集有限
    'Price range' : _e2e_value_range['Price range'],        # 价格范围，6选1
    'Customer rating' : _e2e_value_range['Customer rating'],         # 用户评价：6选1
    'Near' : _e2e_value_range['String_Name'],                                                                                    # 附近标识（地点），理论上字符串无限，数据集有限
    'Food' : _e2e_value_range['Food'],          # 食物类型：7选1
    'Area' : _e2e_value_range['Area'],                                                            # 地区：2选1
    'Family friendly' : _e2e_value_range['Family friendly']                                                                 # 是否家庭友好：2选1
})

kg_schema = {
    "intro" : "It's a Knowledge Graph of the resturant, each graph contains only one resturant entity and seven attributes.",
    "entity_type" : "single_entity",        # "single_entity", or "multi_entity"
    "event_type" : "static",        # 完全静态如E2E和Rotowire的属性"static", 属性类化可多次可迭代成整体的"dynamic"
    "entity":{
        "Resturant":{
            "number": (1,1),     # 左右一样表示固定数量，左小右大表示闭区间取值范围，左大右小表示>=
            "intro" : "餐馆基本评价",
            "predicate" : "'s",
            "attributes":_col_name_value
        }
    },
    "relation":{}
}