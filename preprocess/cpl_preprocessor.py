import os
import sys 
import pandas as pd
import json
import numpy as np
from tqdm import tqdm

_ROOT_PATH = os.path.abspath(__file__)
for i in range(2):
    _ROOT_PATH = os.path.dirname( _ROOT_PATH )
sys.path.insert(0, _ROOT_PATH)
from utils import SingletonLogger, _PUNCATUATION_EN, _PUNCATUATION_ZH, load_data, multi_process, read_docx
from preprocess.CPL_Processor.excel_reader import get_DataCell, get_FirstColumn


class CPL_Preprocessor():
    def __init__( self ):
        self.logger = SingletonLogger.get_logger( "preprocess_log_CPL", os.path.join(_ROOT_PATH, "preprocess/CPL_Processor/preprocess.log"))
        self.raw_data_path = os.path.join( _ROOT_PATH, "raw/CPL")
        self.twice_name = [ "FirstCollection", "SecondCollection" ]
        self.type_name = [ "doc", "excel"]
        self.target_doc_path = [ os.path.join( self.raw_data_path, f"{self.twice_name[0]}/{self.type_name[0]}"), os.path.join( self.raw_data_path, f"{self.twice_name[1]}/{self.type_name[0]}")]
        self.target_excel_path = [ os.path.join( self.raw_data_path, f"{self.twice_name[0]}/{self.type_name[1]}"), os.path.join( self.raw_data_path, f"{self.twice_name[1]}/{self.type_name[1]}")]
        self.save_path = os.path.join( _ROOT_PATH, "data/cpl")
    
    # 从文本获取法庭名
    def get_all_court_name(self, text_list ):
        court_name = {}
        no_name = []
        for i in range(len(text_list)):
            splits = text_list[i].split("\\n")
            flag=0
            for j in range(9):
                if "法院" in splits[j]:
                    name = splits[j]
                    if "审理法院：" in name:
                        name = name[5:]
                    elif "民事判决书" in name:
                        name = name[:-5]
                    elif "中华人民共和国" in name:
                        name = name[7:]
                    court_name[i] = name
                    flag=1
                    break
            if flag==0:
                no_name.append( i )
        court_name[561] = "浙江省温州市中级人民法院"
        court_name[562] = "安徽省合肥市中级人民法院"
        court_name[793] = "浙江省温州市中级人民法院"
        return court_name

    # 添加法庭名，为第一次采集增加一行
    def unify(self, text_table_pair, court_name):
        twice = [ "FirstCollection", "SecondCollection"]
        none = []
        count = 0
        error = []
        table_dict = {}
        new_table_dict = {
            0:[],
            1:[]
        }
        for i in range(2):
            table_dict[i] = []
            row = 20 if i ==0 else 22
            start_row = 10 if i==0 else 12
            doc_dir_name, excel_dir_name = f"{self.raw_data_path}/{twice[i]}/doc", f"{self.raw_data_path}/{twice[i]}/excel"
            for j in tqdm( range(len(text_table_pair[i])), desc=f"Processing {i}"):
                # 路径与读取表格
                pair = text_table_pair[i][j]
                doc_name, excel_name = pair[0], pair[1]
                excel_path = os.path.join( excel_dir_name, excel_name)
                table = pd.read_excel(excel_path, header=None)
                # 添加法院名
                if table.iloc[start_row,7]!="法院":
                    none.append(excel_path)
                else:
                    table.iloc[start_row,8] = court_name[count]
                    count +=1

                # 为首次采集添加一行
                if table.iloc[row,1] !="【诉讼请求原文】【法院认为及判决结果原文】":
                    error.append((i, j))
                else:
                    if i==0:
                        length = len(table.iloc[row])
                        new_row = {}
                        for k in range(length):
                            if k == 1:
                                new_row[k] = "是否变更诉讼请求"
                            else:
                                new_row[k]=np.nan
                        new_row = pd.DataFrame([new_row])
                        df = pd.concat([table.iloc[:row+1], new_row, table.iloc[row+1:]]).reset_index(drop=True)
                        table = df
                df = table.iloc[row-10:].reset_index(drop=True)
                new_table_dict[i].append( df )
                df = df.dropna(how='all')
                df = df.drop(columns=[2,3,4,5,6])
                # 原路返回保存
                row = 0
                for i in range( len(df) ):
                    if df.iloc[i,1] == "【诉讼请求原文】【法院认为及判决结果原文】":
                        row = i
                        break
                new_table = pd.concat([df.iloc[:1], df.iloc[row:]]).reset_index(drop=True)
                new_table.to_excel(excel_path, index=False)

    # 对文件名列表根据标号排序
    def get_sorted_file_names( self, file_list, target_path ):
        split_list = []
        for i in range(len(file_list)):
            temp = file_list[i].split(".")
            temp[0] = int(temp[0])
            split_list.append( temp )
        split_list_sorted = sorted(split_list, key=lambda x: x[0])
        for i in range(len(split_list_sorted)):
            split_list_sorted[i][0] = str(split_list_sorted[i][0])
            split_list_sorted[i] = ".".join(split_list_sorted[i])
        # check the sorted filename list
        for i in range(len(split_list_sorted)):
            if not os.path.exists(os.path.join(target_path,split_list_sorted[i] )):
                print(f"Some problems on {i}")
        return split_list_sorted
    
    # 获取文本、表格对
    def get_file_pairs( self, doc_list, excel_list, index ):
        sorted_excel_list = self.get_sorted_file_names(excel_list, self.target_excel_path[index])
        sorted_doc_list = self.get_sorted_file_names(doc_list, self.target_doc_path[index] )
        text_data_pairs = []
        for i in range( len(sorted_doc_list) ):
            if( sorted_doc_list[i].endswith(".docx")):
                text_data_pairs.append( (sorted_doc_list[i], sorted_excel_list[i]) )
        return text_data_pairs

    # 过滤出703份表格数据
    def excel_filter(self, text_table_pair, table_list):
        total_pairs = []
        for i in range(2):
            for j in range(len(text_table_pair[i])):
                total_pairs.append( text_table_pair[i][j])
        
        # 过滤其中147份没有原告姓名的（说明不是单次单笔）
        filter_pairs = []
        filter_tables = []
        non_single = []
        # 法院列2，原告列5，被告列8，担保11，其他14
        for i in range(len(table_list)):
            table = table_list[i]
            if not pd.isna(table.iloc[0, 6]):                   # 原告姓名与字段分开的638
                filter_pairs.append( total_pairs[i] )
                filter_tables.append( table_list[i] )
            else:
                string_name = table.iloc[0, 5].split("：")      # 没有原告姓名的147
                if string_name[1]=="":
                    non_single.append((i, total_pairs[i]))
                else:
                    # 原告姓名与字段一个格子的65
                    filter_pairs.append( total_pairs[i] )
                    filter_tables.append( table_list[i] )
        return filter_pairs, filter_tables, non_single

    # 处理文本
    def docx_processor(self, text_table_pair):
        count_total = 0
        error_reading_total = 0
        text_list = []
        name_list = []
        for i in range(2):                                                              # 第一次、第二次采集
            task_list = []
            for j in range(len(text_table_pair[i])):                                    # 每次采集的每个.docx文件
                file_name = text_table_pair[i][j][0]
                name_list.append( file_name )                                           # 文件名列表
                task_list.append( os.path.join(self.target_doc_path[i], file_name) )    # 拼接为完整路径用于多进程任务
            text_list_part, error_reading, count = multi_process( read_docx, task_list, "CPL: docs reading." )
            text_list.extend(text_list_part)                                            # 将两次处理完毕的结果extend到一起
            count_total += count                                                        # 总数量
            error_reading_total += error_reading                                        # 无效读取数量
        with open( os.path.join(self.save_path, 'text'), 'w') as file:                  # 逐行写入
            for i in range(len(text_list)):
                line = text_list[i]
                line = line.replace(" ", "").replace("\u3000", "").replace("\n\n\n", "\n").replace("\n\n", "\n").replace("\n", "\\n") # 特殊字符串清洗
                for p in range( len(_PUNCATUATION_EN) ):                                # 英字符转中
                    line = line.replace(_PUNCATUATION_EN[p], _PUNCATUATION_ZH[p])
                file.write(name_list[i]+"###"+line + '\n')                              # 文件名拼接在最前
                text_list[i] = line
        self.logger.info( f"Have written {count_total} to data/CPL/all_data successfully !!!!")
        return text_list

    # 合并703份
    def excel_merge(self, text_table_pair):
        # 列数较为统一：{17: 844, 20: 5, 23: 1}
        # 行数相对集中：{219: 812, 228: 2, 220: 4, 231: 3, 234: 3, 226: 2, 223: 7, 225: 4, 227: 2, 221: 1, 233: 3, 244: 1, 255: 1, 247: 1, 230: 2, 222: 1, 274: 1}
        # 顺序读取850份干净版数据和pairs
        table_list = []
        for i, twice in enumerate(self.twice_name):
            for j in tqdm( range( len(text_table_pair[i])), desc=f"Filtering {i}"):
                file_name = text_table_pair[i][j][1]
                path = os.path.join( self.raw_data_path, f"{twice}/excel/{file_name}")
                table = pd.read_excel(path)
                table_list.append( table )
        filter_pairs, filter_tables, non_single = self.excel_filter(text_table_pair, table_list)        # 703份单次单笔借贷
        return filter_pairs, filter_tables, non_single, table_list
    
    # 从表格中获取entity名称
    def get_names_from_excel( self, table ):
        role_map = {
            "出借人（原告）姓名或名称": (0, "出借人（原告）"),
            "借款人（被告）姓名或名称": (1, "借款人（被告）"),
            "担保人（被告）姓名或名称": (2, "担保人（被告）"),
            "【其他诉讼参与人】姓名或名称": (3, "其他诉讼参与人")
            }
        # 除了法院，其他都有“：”：[703, 695, 121, 55]
        count = [0, 0, 0, 0]
        ret = []
        for j in range(2, len(table.iloc[0]), 3 ):
            if j ==2:
                ret.append( ("法院", table.iloc[0, j+1]))
            else:
                fields = table.iloc[0, j].split("：")
                filed_name = role_map[fields[0]][1]
                field_index = role_map[fields[0]][0]
                if fields[1]!="":
                    # 说明名字和字段在一起了
                    ret.append( (filed_name, fields[1]))
                    count[field_index] +=1
                elif not pd.isna(table.iloc[0, j+1]):
                    # 如果名字不在一起但在后一格
                    ret.append( (filed_name, table.iloc[0, j+1]))
                    count[field_index] +=1
        return ret, count
    
    # 处理表格
    def excel_processor( self, filter_tables, json_data):
        new_table_list = {}
        new_table_split_index_list = {}
        for i in tqdm( range(len(filter_tables)), desc=f"Constructing json"):
            entity = json_data[str(i)]
            table = filter_tables[i]

            single_dict = {}
            single_dict[ "first_column"] = get_FirstColumn( entity )
            single_dict[ "data_cell"], split_index = get_DataCell( single_dict[ "first_column"], table)
            new_table_list[i] = single_dict
            new_table_split_index_list[i] = split_index
        save_path = os.path.join(self.save_path, "tables_703.json")
        with open(save_path, "w", encoding="utf-8" ) as f:
            json.dump( new_table_list, f, ensure_ascii=False, indent=4)
        return new_table_list, new_table_split_index_list
    
    def resave_text(self, non_single):
        load_path = os.path.join(self.save_path, "text")
        save_path = os.path.join(self.save_path, "text_703")
        # 测试文本和数据路径
        texts = []
        with open(load_path, 'r', encoding='utf-8') as file:
            for line in file:
                texts.append(line.strip())
        non_single_index = []
        for i in range(len(non_single)):
            non_single_index.append(non_single[i][0])
        
        with open( save_path, 'w') as file:
            for i in range(len(texts)):
                if i not in non_single_index:
                    file.write(texts[i]+ '\n')

    # 获取文本表格对，修改原始文本
    def main(self):
        
        docx_list = [ os.listdir(_path) for _path in self.target_doc_path ]                             # [391-70=321, 459-77=382] 850-147=703
        excel_list = [ os.listdir(_path) for _path in self.target_excel_path ]
        text_table_pair = [ self.get_file_pairs( docx_list[i], excel_list[i], i) for i in range(2) ]    # 根据标号两两配对
        self.logger.info( f"Get Text-Table-Path pairs with length of {len(text_table_pair[0])+len(text_table_pair[1])}. Processing them to be training data...." )
        # text_list = self.docx_processor( text_table_pair)
        """处理并原地保存excel表格，只在第一次使用
        court_name = self.get_all_court_name( text_list )
        self.unify(text_table_pair, court_name)
        """
        filter_pairs, filter_tables, non_single, table_list = self.excel_merge( text_table_pair )
        # self.resave_text(non_single)
        """
        # 获取实体名称
        first_columns = { }
        no_beigao = []
        total_count = [0, 0, 0, 0]
        for i in range( len(filter_tables)):
            table = filter_tables[i]
            ret = {}
            first_columns[i], count = self.get_names_from_excel( table )
            for k in range(4):
                if count[k]>0:
                    total_count[k]+=1
                if k==1 and count[k]==0:
                    no_beigao.append(i)
        """
        # 但是还得经过人工: 只有三个角色：{0: {1: 703}, 1: {1: 703}, 2: {1: 568, 2: 124, 3: 11}}
        with open( os.path.join( _ROOT_PATH, "data/cpl/original/entity_name_703.json"), "r", encoding="utf-8") as f:
            json_data = json.load(f)
        new_table_list, new_table_split_index_list = self.excel_processor( filter_tables, json_data)
        return new_table_list, new_table_split_index_list, text_table_pair, non_single

if __name__=="__main__":
    preprocessor = CPL_Preprocessor()
    new_table_list, new_table_split_index_list = preprocessor.main()