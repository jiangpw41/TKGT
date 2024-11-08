import yaml
import os

_ROOT_PATH = os.path.abspath(__file__)
for i in range(1):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)

with open( os.path.join( _ROOT_PATH, 'config.yaml'), 'r') as f:
    config_data = yaml.safe_load(f)
        
with open( os.path.join( _ROOT_PATH, 'prompt_templates.yaml'), 'r') as f:
    prompt_templates = yaml.safe_load(f)

    
__all__ = [
    'config_data',
    'prompt_templates'
]