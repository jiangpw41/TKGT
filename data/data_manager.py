from tqdm import tqdm
import pandas as pd
import pickle
import json
import os
import sys
import random
random.seed(42)

_ROOT_PATH = os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) )
sys.path.insert( 0, _ROOT_PATH)
from config_loader import config_data
from utils import load_data, save_data
from data.dataset_specific import load_e2e, load_rotowire, load_cpl

def data_split( data, train_test_ratio, indices ):
    total_length = len(indices)

    train_length = int(total_length * train_test_ratio[0])  # 70%  
    
    train = []
    test = []
    for i in range( total_length ):
        index = indices[i]
        if i<train_length:
            train.append( data[index] )
        else:
            test.append( data[index] )
    
    return train, test

def data_save_four( train_texts, test_texts, train_tables, test_tables, data_dir ):
    save_data( train_tables, os.path.join(data_dir, f"train.pickle"))
    save_data( test_tables, os.path.join(data_dir, f"test.pickle"))
    save_data( train_texts, os.path.join(data_dir, "train.text"))
    save_data( test_texts, os.path.join(data_dir, "test.text"))


class DataManager():
    def __init__(self, dataset_name, part="all", resplit=False):
        """
        part: "all", "train", "test", "application"
        """
        self.dataset_name = dataset_name
        self.part = part
        self.resplit = resplit

        self.data_dir = os.path.join( _ROOT_PATH, f"data/{dataset_name}")
        try:
            self.datasets_info = config_data["DATASET_MANAGE"][dataset_name]
        except KeyError:
            print(f"数据集名'{dataset_name}'不存在.")
        self.train_test_ratio = config_data["DATASET_MANAGE"]["train_test_ratio"]
        self.ruled = self.datasets_info["ruled"]
        self.pair = self.datasets_info["pair"]
        self.all_data = None
    
    #（1）检查路径并决定重新处理还是直接加载
    def exist_file_check( self ):
        original = True
        if not os.path.exists( os.path.join( self.data_dir, "original")):
            print(f"源文件夹original在{self.data_dir}下不存在！")
            original = False
        
        if self.pair:
            count = 4
            for suffix in [".text", ".pickle"]:
                for prefix in ["train", "test"]:
                    file_name = prefix+suffix
                    if not os.path.exists( os.path.join( self.data_dir, file_name)):
                        print(f"处理完毕的文件{file_name}不存在！")
                        count -= 1
        else:
            count = 1
            if not os.path.exists( os.path.join( self.data_dir, "application.text")):
                print(f"处理完毕的文件application.text不存在！")
                count -= 1
        processed = False if count==0 else True

        if original:
            if not processed:
                print(f"{self.data_dir}目录下存在源文件夹但不存在处理完毕的数据，需要进行处理！")
                return "Process"
            else:
                print(f"{self.data_dir}目录下存在源文件夹，且存在处理完毕的数据，直接加载！")
                return "Load"
        else:
            if processed:
                Warning( f"警告：{self.data_dir}目录下存在处理完毕的数据，但不存在源文件夹，直接进行加载！")
                return "Load"
            else:
                raise Exception( f"错误：{self.data_dir}目录下既不存在处理完毕的数据，也不存在源文件夹！")
    
    def get_shuffle_index( self, texts ):
        total_length = len(texts)
        indices = list(range(total_length))
        random.shuffle(indices)
        return indices

    #（2）重新处理
    def process(self):
        # 加载原始数据集
        if self.dataset_name == "e2e":
            texts, tables = load_e2e( self.data_dir, load_data)
            indices = self.get_shuffle_index( texts, tables )
            train_text, test_text = data_split( texts, self.train_test_ratio, indices)
            train_table, test_table = data_split( tables, self.train_test_ratio, indices )
            data_save_four( train_text, test_text, train_table, test_table, self.data_dir )
        elif self.dataset_name == "rotowire":
            texts, tables = load_rotowire( self.data_dir, load_data)
            indices = self.get_shuffle_index( texts )
            train_text, test_text = data_split( texts, self.train_test_ratio, indices )
            train_first_team, test_first_team = data_split( tables["FirstColumn"]["Team"], self.train_test_ratio, indices )
            train_first_player, test_first_player = data_split( tables["FirstColumn"]["Player"], self.train_test_ratio, indices )
            train_cell_team, test_cell_team = data_split( tables["DataCell"]["Team"], self.train_test_ratio, indices )
            train_cell_player, test_player= data_split( tables["DataCell"]["Player"], self.train_test_ratio, indices )
            train_table = {
                "FirstColumn": {
                    "Team": train_first_team,
                    "Player": train_first_player
                },
                "DataCell": {
                    "Team": train_cell_team,
                    "Player": train_cell_player
                }
            }
            test_table = {
                "FirstColumn": {
                    "Team": test_first_team,
                    "Player": test_first_player
                },
                "DataCell": {
                    "Team": test_cell_team,
                    "Player": test_player
                }
            }
            data_save_four( train_text, test_text, train_table, test_table, self.data_dir )
        elif self.dataset_name == "cpl":
            texts, tables = load_cpl( self.data_dir, load_data)
            indices = self.get_shuffle_index( texts, tables )
            train_text, test_text = data_split( texts, self.train_test_ratio, indices )
            train_first, test_first = data_split( tables["FirstColumn"], self.train_test_ratio, indices )
            train_cell, test_cell = data_split( tables["DataCell"], self.train_test_ratio, indices )
            train_table = {
                "FirstColumn": train_first,
                "DataCell": train_cell
            }
            test_table = {
                "FirstColumn": test_first,
                "DataCell": test_cell
            }
            data_save_four( train_text, test_text, train_table, test_table, self.data_dir )
        save_data( indices, os.path.join(self.data_dir, "index.pickle" ))
        print(f"{self.data_dir}目录下分割数据处理完毕且已保存！")
        
    #（3）直接加载
    def load( self ):
        if self.part == "all":
            train_texts = load_data( os.path.join( self.data_dir, "train.text"), "text")
            test_texts = load_data( os.path.join( self.data_dir, "test.text"), "text")
            train_tables = load_data( os.path.join( self.data_dir, "train.pickle"), "pickle")
            test_tables = load_data( os.path.join( self.data_dir, "test.pickle"), "pickle")
            return ( train_texts, test_texts, train_tables, test_tables )
        elif self.part == "train":
            train_texts = load_data( os.path.join( self.data_dir, "train.text"), "text")
            train_tables = load_data( os.path.join( self.data_dir, "train.pickle"), "pickle")
            return ( train_texts, train_tables )
        elif self.part == "test":
            test_texts = load_data( os.path.join( self.data_dir, "test.text"), "text")
            test_tables = load_data( os.path.join( self.data_dir, "test.pickle"), "pickle")
            return ( test_texts, test_tables )
        elif self.part == "application":
            application_texts = load_data( os.path.join( self.data_dir, "application.text"), "text")
            return application_texts


    def main(self):
        # （1）检查路径下是否已经存在准备好的数据，如果是的，直接加载；否则，全部重新处理该数据集
        check_result = self.exist_file_check()
        if check_result == "Process":
            self.process()
        return self.load()  # text, table || train, test

if __name__=="__main__":
    # data_manager = DataManager( "e2e" )   # \
    data_manager = DataManager( "rotowire")   # \
    # data_manager = DataManager( "cpl" )   # 
    data = data_manager.main()
    print("s")