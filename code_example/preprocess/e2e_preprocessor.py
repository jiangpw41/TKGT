import pandas as pd
import os
import sys
from tqdm import tqdm
import concurrent
from concurrent.futures import ProcessPoolExecutor
import shutil

# Event-Oriented
_ROOT_PATH = os.path.abspath(__file__)
for i in range(2):
    _ROOT_PATH = os.path.dirname( _ROOT_PATH )
sys.path.insert(0, _ROOT_PATH)
from utils import read_text_to_list, create_logger


logger = create_logger( "preprocess_log", os.path.join(_ROOT_PATH, "preprocess/preprocess.log"))
_DATA_PATH = os.path.join( _ROOT_PATH, "raw/e2e")
_SAVE_PATH = os.path.join( _ROOT_PATH, "data/e2e/original")
if not os.path.exists(_SAVE_PATH):  
    # 如果目录不存在，则创建它  
    os.makedirs(_SAVE_PATH)
    logger.info( "Preprocess: have created path of E2E.")

# 从表格用AI模型生成的
_col_name = [
    'Name',                   # 餐厅名，理论上字符串无限，['The vaults', 'The cambridge blue', 'The eagle', 'The mill', 'Loch fyne', 'Bibimbap house', 'The rice boat', 'The wrestlers', 'Aromi', 'The phoenix', 'Browns cambridge', 'Taste of cambridge', 'Cocum', 'The dumpling tree', 'The punter', 'The golden curry', 'Alimentum', 'Midsummer house', 'Blue spice', 'Strada', 'The waterman', 'Zizzi', 'Green man', 'Clowns', 'Giraffe', 'The olive grove', 'The twenty two', 'The cricketers', 'Wildwood', 'The golden palace', 'The plough', 'Cotto', 'Fitzbillies', 'Travellers rest beefeater']
    'Price range',            # 价格范围，6选1['More than £30', 'Cheap', 'Less than £20', '£20-25', 'Moderate', 'High']
    'Customer rating',        # 用户评价：6选1['5 out of 5', 'Low', 'Average', '3 out of 5', '1 out of 5', 'High']
    'Near',                   # 附近标识（地点），理论上字符串无限，['Café adriatic', 'Café brazil', 'Burger king', 'The sorrento', 'The rice boat', 'Clare hall', 'Raja indian cuisine', 'Café rouge', 'Yippee noodle bar', 'The portland arms', 'All bar one', 'Express by holiday inn', 'The bakers', 'Café sicilia', 'Avalon', 'The six bells', 'Ranch', 'Crowne plaza hotel', 'Rainbow vegetarian café']
    'Food',                   # 食物类型：7选1['Japanese', 'French', 'English', 'Fast food', 'Italian', 'Indian', 'Chinese']
    'Area',                   # 地区：2选1 ['Riverside', 'City centre']
    'Family friendly'         # 是否家庭友好：2选1['Yes', 'No']
] 

def multi_process( processor, task_list, _type ):
    # 所有使用多进程工具的函数，必须将迭代对象及其index作为函数参数的前两位
    splited_task_list = [None]*len(task_list)
    with ProcessPoolExecutor() as executor:
        future_to_item = {}
        for j, item in enumerate(task_list):
            future_to_item[executor.submit(processor, _type, item, j)] = j 
        with tqdm(total=len(future_to_item), desc=f"Rotowire_{_type}") as pbar:
            for future in concurrent.futures.as_completed(future_to_item): 
                future.result()
                pbar.update(1)

def convert_rotowore_to_table():
    datasets = ["train.data", "valid.data", "test.data"]
    value_dict = { key:[] for key in _col_name}
    # 遍历子数据集
    dict_col = { _col_name[i]:i for i in range( len(_col_name )) }
    for dataset in datasets:
        tables = read_text_to_list( os.path.join(_DATA_PATH, dataset) )
        total = []
        # 遍历每行
        for i in tqdm(range(len(tables)), desc=f"Preprocess E2E: processing {dataset}"):
            table = list(filter(None, tables[i].split(" <NEWLINE> ") ))
            temp = [None for _ in range( len(_col_name) )]
            for item in table:
                item = item[1:-1].split(" | ")
                if len(item)!=2:
                    print(f"item wrong {dataset} {i}")
                attr = item[0].strip()
                value = item[1].strip()
                temp[dict_col[attr]] = value
            total.append( temp )
        # 使用ExcelWriter对象写入Excel文件
        prefix = dataset.split(".")[0]
        total = pd.DataFrame(total, columns=_col_name)
        total.to_excel(os.path.join(_SAVE_PATH, f"{prefix}.xlsx"))
    for files in [ "test.text",  "train.text",  "valid.text"]:
        _from_path = os.path.join( _DATA_PATH, files)
        _to_path = os.path.join( _SAVE_PATH, files)
        shutil.copy2( _from_path, _to_path)

def value_type( ):
    datasets = ["train.data", "valid.data", "test.data"]
    value_dict = { key:[] for key in _col_name}
    for dataset in datasets:
        tables = read_text_to_list( os.path.join(_DATA_PATH, dataset) )
        for i in range(len(tables)):
            table = list(filter(None, tables[i].split(" <NEWLINE> ") ))
            for item in table:
                item = item[1:-1].split(" | ")
                if len(item)!=2:
                    print(f"item wrong {dataset} {i}")
                attr = item[0].strip()
                value = item[1].strip()
                if value not in value_dict[attr]:
                    value_dict[attr].append( value )
    print(value_dict)

if __name__ == "__main__":
    # value_type()
    convert_rotowore_to_table()