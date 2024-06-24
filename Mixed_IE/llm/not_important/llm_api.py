import redis
import pickle
import torch.multiprocessing as mp

import torch
from modelscope import snapshot_download, AutoModelForCausalLM, AutoTokenizer,GenerationConfig

import gc
'''
python -m vllm.entrypoints.openai.api_server \
--model /home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/ChatGLM3-6B/ZhipuAI/chatglm3-6b \
--served-model-name chatglm3-6b \
--trust-remote-code
python -m vllm.entrypoints.openai.api_server --model /home/user/Model/Qwen1.5-0.5B --served-model-name Qwen1.5-0.5B
'''

_DEVICE = "cuda:5"

model_dir = "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/Baichuan2-7B-Chat"


redis_communication.delete('Tasks')
redis_communication.delete('Response')
def model_API( task ):
    '''
    cd /home/jiangpeiwen2/jiangpeiwen2/text-kgs-table/componets/mix_ie/api
    conda activate baichuan
    python3 baichuan_api.py
    '''
    redis_communication.delete('Tasks')
    redis_communication.delete('Response')
    redis_communication.rpush('Tasks', pickle.dumps( task ))
    if task!="STOP":
        while True:
            message = redis_communication.lpop('Response')
            if message!=None:
                ret = pickle.loads(message)
                print(f"Waiting......")
                return ret


def Inferece( ):
    redis_communication = redis.StrictRedis(host='localhost', port=6379, db=0)
    tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True, torch_dtype=torch.float16)
    model = AutoModelForCausalLM.from_pretrained(model_dir, trust_remote_code=True, torch_dtype=torch.float16).to(_DEVICE)
    model.generation_config = GenerationConfig.from_pretrained(model_dir)
    model.eval()
    print(f"LLM Inderence start!")
    messages = []
    while True:
        message = redis_communication.lpop('Tasks')
        if message!=None:
            task = pickle.loads(message)
            if task=="STOP":
                print(f"LLM Inderence quit!" )
                break
            elif task=="<CLEAN>":
                messages = []
                print("History has been cleaned!")
                continue
            messages.append({"role": "user", "content": task})
            response = model.chat(tokenizer, messages)
            # messages.append({'role': 'assistant', 'content': response})
            redis_communication.rpush('Response', pickle.dumps( response ))
            del response
            gc.collect()
'''
def llm_API( task ):
    redis_communication = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_communication.rpush('Tasks', pickle.dumps( task ))
    while True:
        message = redis_communication.lpop('Response')
        if message!=None:
            ret = pickle.loads(message)
            print(f"Waiting......")
            return ret
'''

if __name__=="__main__":
    with mp.Manager() as manager:
        mains = mp.Process(target=Inferece, args=())
        mains.start()
        mains.join()