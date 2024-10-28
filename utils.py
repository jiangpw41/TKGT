import logging
import json
import pickle
import pandas as pd
import random



from tqdm import tqdm
import concurrent
from concurrent.futures import ProcessPoolExecutor

# Configure matplotlib to use a font that supports Chinese characters


_PUNCATUATION_EN = [',', '.', ';', '?', '!', '…', ":", '"', '"', "'", "'", "(", ")", ]
_PUNCATUATION_ZH = ['，', '。', '；', '？', '！', '......', "：",  '“', '”', '‘', '’', '（', '）', '《', '》', '【', '】', '[', ']', '、', "\\n"]


import random
random.seed(42)
def get_shuffle_index( datas ):
    total_length = len(datas)
    indices = list(range(total_length))
    random.shuffle(indices)
    return indices

def multi_process( processor, task_list, task_description, *args ):
    # 所有使用多进程工具的函数，必须将迭代对象及其index作为函数参数的前两位
    splited_task_list = [None]*len(task_list)
    error_reading = 0
    count = 0
    with ProcessPoolExecutor() as executor:
        future_to_item = {}
        for j, item in enumerate(task_list):
            future_to_item[executor.submit(processor, item, j, *args)] = j 
        with tqdm(total=len(future_to_item), desc=f"Preprocess {task_description}") as pbar:
            for future in concurrent.futures.as_completed(future_to_item): 
                line = future.result()
                count += 1
                if line=={} or line=="":
                    error_reading += 1
                splited_task_list[ future_to_item[future]] = future.result()
                pbar.update(1)
    return splited_task_list, error_reading, count

def online_local_chat( query, index=0 ):
    """将下面两行放置到环境中
    import redis
    import pickle
    redis_communication = redis.StrictRedis(host='localhost', port=6379, db=0)

    from vllm import LLM, SamplingParams
    model_dir = "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/Baichuan2-7B-Chat"
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
    llm = LLM(
        model=model_dir,
        trust_remote_code=True,
        dtype='float16',
        gpu_memory_utilization=0.9,
        seed = 32,
    )   # 必须使用模型支持列表中的模型名
    print(f"LLM Inderence start!")

    task = ["静夜思全文", "天气怎么样"]
    outputs = llm.generate(task, sampling_params, use_tqdm=False)
    ret = []
    for output in outputs:
        ret.append( output.outputs[0].text )
    """
    redis_communication.rpush('Tasks', pickle.dumps( (index, query) ))
    while True:
        message = redis_communication.lpop('Response')
        if message!=None:
            index, ret = pickle.loads(message)
            return (index, ret)

#####################################################数据加载保存#################################################

def save_data( data, path ):
    type = path.split(".")[-1]
    if type == "text":
        with open( path, 'w') as file:
            for i in range(len(data)):
                line = data[i]
                file.write(line + '\n')
    elif type == "json":
        with open( path, "w", encoding="utf-8") as f:
            json.dump( data, f,  ensure_ascii=False, indent=4)
    elif type == "pickle":
        with open( path, "wb") as f:
            pickle.dump( data, f )
    else:
        raise Exception(f"{type}类型数据目前无法使用save_data保存")

def load_data( path, type, header_None=False, sheet_name=False):
    if type == "text":
        texts = []
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                texts.append(line.strip())
        return texts
    elif type == "json":
        with open( path, "r", encoding="utf-8") as f:
            datas = json.load( f)
        return datas
    elif type == "pickle":
        with open( path, "rb") as f:
            datas = pickle.load( f)
        return datas
    elif type == "excel":
        if header_None:
            if sheet_name:
                return pd.read_excel( path, header=None, sheet_name=sheet_name )
            else:
                return pd.read_excel( path, header=None )
        else:
            if sheet_name:
                return pd.read_excel( path, sheet_name=sheet_name)
            else:
                return pd.read_excel( path)

def read_text_to_list( path ):
    with open(path, 'r') as file:  
        lines = file.readlines()
    strings_read = []
    for line in lines:
        if line.endswith("\n"):
            line = line[:-1]
        strings_read.append( line )
    return strings_read

class CustomError(Exception):  
    def __init__(self, message, logger):  
        super().__init__(message)  
        if logger:  
            logger.error(message)

############################################日志工具###################################################

def create_logger( log_name, save_path_name, level=1 ):
    # Ceate and determine its level
    levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
    logger = logging.getLogger(log_name)
    logger.setLevel( levels[level] )  
    
    # Create a FileHandler for writing log files 
    file_handler = logging.FileHandler( save_path_name, encoding='utf-8' )  
    file_handler.setLevel( levels[level] )  
    
    # Create a StreamHandler for outputting to the console  
    console_handler = logging.StreamHandler()  
    console_handler.setLevel( levels[level] )  
    
    # Define the output format of the handler 
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    file_handler.setFormatter(formatter)  
    console_handler.setFormatter(formatter)  
    
    # Add Handler to Logger
    logger.addHandler(file_handler)  
    logger.addHandler(console_handler)  

    return logger

class SingletonLogger:  
    _instances = {}  
    @classmethod  
    def get_logger(cls, log_name, save_path_name, level=1):  
        if log_name not in cls._instances:  
            levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]  
            logger = logging.getLogger(log_name)  
            logger.setLevel(levels[level])  
  
            file_handler = logging.FileHandler(save_path_name, encoding='utf-8')  
            file_handler.setLevel(levels[level])  
  
            console_handler = logging.StreamHandler()  
            console_handler.setLevel(levels[level])  
  
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
            file_handler.setFormatter(formatter)  
            console_handler.setFormatter(formatter)  
  
            logger.addHandler(file_handler)  
            logger.addHandler(console_handler)  
  
            cls._instances[log_name] = logger  
  
        return cls._instances[log_name]