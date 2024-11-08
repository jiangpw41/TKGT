import os
import sys
from tqdm import tqdm
import argparse

_ROOT_PATH = os.path.abspath(__file__)
for i in range(2):
    _ROOT_PATH = os.path.dirname(_ROOT_PATH)
sys.path.insert(0, _ROOT_PATH)

from KGs.cores.entity_single import single_entity_main
from KGs.cores.entity_multiple import multiple_entity_main
from KGs.cores.event_static import static_event_main



def main_cores_all( dataset_name, if_static ):
    if dataset_name == "e2e":
        single_entity_main( dataset_name )
    elif dataset_name in ["cpl", "rotowire"]:
        multiple_entity_main( dataset_name )
        if if_static:
            static_event_main( dataset_name )


if __name__=="__main__":
    """
    parser = argparse.ArgumentParser(description="Run script with external arguments")
    parser.add_argument('--dataset_name', type=str, required=True, help='数据集名')
    parser.add_argument('--if_static', type=int, required=True, help='属性是否是固定的，1为固定')
    args = parser.parse_args()
    if_static = False if args.if_static==0 else True
    dataset_name = args.dataset_name
    """
    dataset_name = "cpl"
    if_static = True
    
    main_cores_all( dataset_name, if_static )