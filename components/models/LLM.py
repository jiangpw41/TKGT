import numpy as np
import pandas as pd
import argparse, httpx, docx2txt, os, time
import torch
import jieba
from tqdm import tqdm
from openai import OpenAI
import concurrent.futures
from pathlib import Path
from typing import Annotated, Union, Optional, Tuple, Union, List, Callable, Dict, Any
import typer
from peft import AutoPeftModelForCausalLM, PeftModelForCausalLM
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)
from transformers.generation.utils import LogitsProcessorList, StoppingCriteriaList, GenerationConfig, ModelOutput
from transformers.generation.logits_process import LogitsProcessor

ModelType = Union[PreTrainedModel, PeftModelForCausalLM]
TokenizerType = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]
app = typer.Typer(pretty_exceptions_show_locals=False)

timeout_limit = 30
SYS_PROMPT = {"role": "system", "content": "You are a helpful assistant."}

class InvalidScoreLogitsProcessor(LogitsProcessor):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        if torch.isnan(scores).any() or torch.isinf(scores).any():
            scores.zero_()
            scores[..., 5] = 5e4
        return scores

def sending_prompt_gpt_4(client, prompt):
    try:
        completion = client.chat.completions.create(
          model=MODEL_NAME,
          messages=[
            #{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
          ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Warning: {e} was raised during excuting {prompt}")
        return None

def sending_prompt_gpt(model_name, client, prompt):
    try:
        completion = client.chat.completions.create(
          model=model_name,
          messages=[
            #{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
          ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Warning: {e} was raised during excuting {prompt}")
        return None


def append_history(prompt, response, prev_history = [SYS_PROMPT]):
    prompt_pair = [{"role": "user", "content": prompt},
            {"role": "assistant", "content": response}]
    history = prev_history + prompt_pair
    return history

def build_message(prompt, history = [SYS_PROMPT]):
    history.append({"role": "user", "content": prompt})
    return history

def sending_prompt_with_history_gpt_4(client, prompt, history):
    global MODEL_NAME
    try:
        completion = client.chat.completions.create(
          model=MODEL_NAME,
          messages=build_message(prompt, history)
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Warning: {e} was raised during excuting {prompt}")
        return None


def sending_prompt_with_history_gpt(model_name, client, prompt, history):
    try:
        completion = client.chat.completions.create(
          model=model_name,
          messages=build_message(prompt, history)
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Warning: {e} was raised during excuting {prompt}")
        return None


def _resolve_path(path: Union[str, Path]) -> Path:
    return Path(path).expanduser().resolve()

def load_model_and_tokenizer(model_dir: Union[str, Path]) -> tuple[ModelType, TokenizerType]:
    model_dir = _resolve_path(model_dir)
    if (model_dir / 'adapter_config.json').exists():
        model = AutoPeftModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device_map='auto'
        )
        tokenizer_dir = model.peft_config['default'].base_model_name_or_path
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device_map='auto'
        )
        tokenizer_dir = model_dir
    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_dir, trust_remote_code=True
    )
    return model, tokenizer

@torch.inference_mode()
def model_generate_iter(model, tokenizer, query: str, history: List[Dict] = None, role: str = "user",
        max_new_tokens: int = 1024, num_beams=1, do_sample=True, top_p=0.8, device='cuda:0', temperature=0.8, logits_processor=None,
        **kwargs):
        if history is None:
            history = []
        if logits_processor is None:
            logits_processor = LogitsProcessorList()
        logits_processor.append(InvalidScoreLogitsProcessor())
        gen_kwargs = {"max_new_tokens": max_new_tokens, "num_beams": num_beams, "do_sample": do_sample, "top_p": top_p,
                      "temperature": temperature, "logits_processor": logits_processor, **kwargs}
        inputs = tokenizer.build_chat_input(query, history=history, role=role)
        inputs = inputs.to(device)
        eos_token_id = [tokenizer.eos_token_id, tokenizer.get_command("<|user|>"),
                        tokenizer.get_command("<|observation|>")]
        outputs = model.generate(**inputs, **gen_kwargs, eos_token_id=eos_token_id)
        outputs.to('cpu')    
        outputs = outputs.tolist()[0][len(inputs["input_ids"][0]):-1]
        inputs.to('cpu')
        
        response = tokenizer.decode(outputs)
        history.append({"role": role, "content": query})
        response, history = model.process_response(response, history)
        return response, history, inputs, outputs

def llama3_pipeline_generate(pipeline, prompt, history, max_new_tokens=2048, do_sample=True, temperature=0.1, top_p=0.9):
    messages=build_message(prompt, history)
    terminators = [
        pipeline.tokenizer.eos_token_id,
        pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    outputs = pipeline(
        messages,
        max_new_tokens=max_new_tokens,
        eos_token_id=terminators,
        do_sample=do_sample,
        temperature=temperature,
        top_p=top_p,
    )
    return outputs[0]["generated_text"][-1]

class LLM:
    """
    LLM Model Class,
    * Currently support models: ChatGLM3 (Original & LLaMaFactory Continued Tuned) & GPT series models. To use LLaMaFactory tuned model, just replace your model_name to the     model endpoint that LLaMaFactory store the model in.
    """
    def __init__(self, model_name, device, client, finetuned=False, sys_prompt=SYS_PROMPT):
        self.model_name = model_name
        self.model = None
        self.pipeline = None
        self.tokenizer = None
        self.device = device
        self.ft_model = finetuned
        if self.model_name != "gpt-4-turbo" and self.model_name != "gpt-3.5-turbo" and self.model_name != "gpt-3.5-turbo-16k" and self.model_name != "gpt-4o":
            self.load_model()
        self.sys_prompt = sys_prompt
        self.history = [self.sys_prompt]
        self.client = client
        
    def reset_chat(self):
        self.history = [self.sys_prompt]

    def load_model(self):
        if 'llama3' in self.model_name:
            self.load_llama3_pipeline()
        if self.ft_model:
            self.load_ft_model()
        else:
            self.load_pretrained_model(self.model_name)

    def load_pretrained_model(self, model_dir):
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_dir, trust_remote_code=True)
        self.model.to(self.device)

    def load_llama3_pipeline(self, model_dir):
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=model_dir,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device=self.device,
        )
    
    def load_ft_model(self, model_dir):
        self.model, self.tokenizer = load_model_and_tokenizer(model_dir)
            
    def generate_gpt(self, prompt):
        response = sending_prompt_with_history_gpt(self.model_name, self.client, prompt, self.history)
        self.history = append_history(prompt, response, self.history)
        return response
    
    def generate_llama3(self, prompt):
        llama3_pipeline_generate(self.pipeline, prompt, self.history)
        self.history = append_history(prompt, response, self.history)
        return response
            
            
    def generate_glm(self, prompt, max_new_tokens):
        response, history, inputs, outputs = model_generate_iter(self.model, self.tokenizer, prompt, self.history, device=self.device, max_new_tokens=max_new_tokens)
        self.history = history
        return response

    def generate(self, prompt, max_new_tokens=1024):
        if self.model_name == "gpt-4-turbo" or self.model_name == "gpt-3.5-turbo" or self.model_name == "gpt-3.5-turbo-16k" or self.model_name == "gpt-4o":
            return self.generate_gpt(prompt)
        elif 'glm' in self.model_name:
            return self.generate_glm(prompt, max_new_tokens=max_new_tokens)
        elif 'llama3' in self.model_name:
            return self.generate_llama3(prompt)
            