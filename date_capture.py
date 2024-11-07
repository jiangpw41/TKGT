import re
from typing import List

import os
import sys
import re


class TextCapture():
    """
    针对一个句子：捕获一个句子中指定匹配格式/符号的数据，并获取该上下文。
    """
    def __init__(self, text: str, match_word, _context_length = 10, _orient = "all" ):
        self.text = text                                        # 要匹配的句子
        self.match_word = match_word                            # 匹配模式或符号
        self.context_length = _context_length
        self.orient = _orient

        if isinstance( match_word, re.Pattern):                 # 正则匹配
            self.matched_words = self.match_word_capture_re()
        else:
            raise Exception(f"当前不支持除正则匹配外的其他方式")
    
    def match_word_capture_re( self ):
        """正则匹配"""
        pattern_role = self.match_word
        matched_words = re.findall(pattern_role, self.text)
        return matched_words

    def get_context(self, symbol):
        """返回一个字符串在文中的内容：输出字符串列表"""
        pattern = re.compile(re.escape(symbol))                  # 编译正则表达式，使用非贪婪匹配来找到符号的位置  
        matches = [match.start() for match in pattern.finditer( self.text)]           # 查找所有符号的位置  
        contexts = []                                                           # 存储结果的列表  
        # 遍历每个匹配的位置  
        for match_index in matches:  
            # 计算上下文的起始和结束位置  
            start_index = max(0, match_index - self.context_length)  
            end_index = match_index + self.context_length + len(symbol)  # 加上符号的长度和额外的上下文长度  
            
            # 获取上下文内容  
            context = self.text[start_index:end_index]  
            # 将上下文内容添加到结果列表中  
            contexts.append(context)  
        
        return contexts  

class ParagraphSplit( ):
    """对一段文本而言"""
    def __init__(self, doc, _sep = [ "。", "；"]):
        self.seps = _sep
        self.sentence_doc = self.sentence_splitter( doc )

    def sentence_splitter( self, texts:list, index = 0) -> List[str]:
        """将一个长段落根据句号、分号进行递归分割
        index：当前使用的sep的索引
        texts：要分割的文本对象，以列表形式传入
        """
        if index < len( self.seps ):                                 # 如果还有分隔符可以用
            sep = self.seps[index]
        else:                                                       # 否则原样返回
            return texts
    
        ret_list = []
        for line in texts:
            lines = line.split( sep )
            for line in lines:
                line = line.strip()
                if line != "":
                    ret_list.append( line )
        return self.sentence_splitter( ret_list, index+1)

class CplParagraphSplitSimple( ParagraphSplit ):
    """对一篇CPL文章分成三部分，每部分是最小字句的列表"""
    def __init__(self, 
                 doc,
                 _seps = [ "。", "；"]      # 文章级别分隔符
                  ):
        super().__init__( doc, _seps)
        # 分为字句
        self.sentence_doc = self.cpl_sentence_splitter( doc )
        
    def cpl_sentence_splitter( self, dicts ):
        """CPL将一篇ruled_text分割为句子级别"""
        new_dicts = {
            '原告': [], 
            '被告': [],
            '法院': [],
        }
        for key in dicts.keys():
            part_list = dicts[key]
            new_dicts[key] = self.sentence_splitter( part_list )
        return new_dicts


class CplParagraphSplit( CplParagraphSplitSimple ):
    """对一篇CPL文章分成三部分，每部分是最小字句的列表"""
    def __init__(self, 
                 doc, 
                 type_class,                # 实例化每个句子的类
                 context_length = 10,       # 实例化每个句子类需要的上下文情况
                 orient = "all",
                 _seps = [ "。", "；"]      # 文章级别分隔符
                  ):
        super().__init__( doc, _seps)
        self.type_class = type_class
        self.context_length = context_length
        self.orient = orient
        # 对每个字句进行实例化
        self.map_dict = self.capture_instantiate()

    def capture_instantiate( self ):
        """对全文每个Part的每个句子，都进行self.type_class实例化并存为字典"""
        dict = {}
        # 遍历三个角色
        for key in self.sentence_doc:
            dict[key] = []
            sent_lit = self.sentence_doc[key]
            # 遍历每个角色的所有字句
            for sent in sent_lit:
                dict[key].append( self.type_class( sent, self.context_length, self.orient ) )
        return dict

############################################### 日期 #############################################################################
class DateTextCapture( TextCapture ):
    """
    针对一个句子：捕获一个句子中所有年-月-日格式的数据，并根据上下文区分哪些是起始、截止、普通日期
    """
    def __init__(self, text: str, context_length = 10, orient = "all"):
        self.match_word = re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日")
        super().__init__( text, self.match_word, context_length, orient)
        self.start_date_dict = {}
        self.end_date_dict = {}
        self.normal_date_dict = {}
        self.all_time_capture()
    
    def all_time_capture( self ):
        date_set = set()
        for tup in self.matched_words:
            date_set.add( f"{tup[0]}年{tup[1]}月{tup[2]}日")
        for date_str in date_set:
            contexts = self.get_context( date_str )
            for context in contexts:
                if "自"+date_str in context or date_str+"起" in context:
                    # 起始日期
                    if date_str not in self.start_date_dict:
                        self.start_date_dict[ date_str ] = []
                    self.start_date_dict[ date_str ].append( context )
                elif "至"+date_str in context or date_str+"截止" in context or date_str+"止" in context:
                    # 截止日期
                    if date_str not in self.end_date_dict:
                        self.end_date_dict[ date_str ] = []
                    self.end_date_dict[ date_str ].append( context )
                else:
                    # 普通日期
                    if date_str not in self.normal_date_dict:
                        self.normal_date_dict[ date_str ] = []
                    self.normal_date_dict[ date_str ].append( context )

class CplDocumentDateTextCapture( CplParagraphSplit ):
    """对一篇文章而言"""
    def __init__(self, doc, context_length = 10, orient = "all", _seps = [ "。", "；"]):
        super().__init__( doc, DateTextCapture, context_length, orient, _seps)

    def get_attr_context_dict( self, entity, attr) -> List[dict]:
        """指定实体和属性，返回所有句子中的日期数据及其相关的上下文字典"""
        ret = []
        sub_list = self.map_dict[entity]            # 获得本文该对象名下所有含有日期的句子的字典：sent：instance
        # 遍历每个句子，获取日期字典
        for line in sub_list:
            text_capture = line                     # 句子对应的日期字符串字典
            if "起始" in attr:
                date_dict = text_capture.start_date_dict
            elif "截止" in attr:
                date_dict = text_capture.end_date_dict
            elif ("约定" in attr and "还款" in attr) or "实际交付时间" in attr or "已还款时间" in attr:
                date_dict = text_capture.normal_date_dict
            
            ret.append( date_dict )
        return ret
    
    def get_related_context( self , entity, attr)-> List[dict]:
        """对该部分的所有字句都进行基于entity和attr的判断，返回对应的上下文"""
        part_dict_list = self.get_attr_context_dict( entity, attr )
        # 遍历每个句子存放该篇文档针对entity实体的attr的属性的句子列表
        ret = []                                    
        for i in range( len(part_dict_list) ):
            date_dict = part_dict_list[i]           # 获取针对一行的所有日期数据
            flag = 0
            # 遍历当前句子中所有日期格式的数据：获取数据对应的上下文列表，
            for date in date_dict.keys():
                if flag == 1:                       # 若已经验证通过，提前退出
                    break
                contexts = date_dict[date]
                if len(contexts)==0:
                    continue
                else:
                    # 遍历列表判断是否符合要求
                    for context in contexts:
                        # 对不同的日期数据进行分类讨论
                        if "返回违约金" in attr and ("违约" in context or "率" in context or "起至" in context):
                            flag = 1
                            break
                        elif "返回利息" in attr and ("息" in context or "率" in context):
                            flag = 1
                            break
                        elif "约定的还款日期" in attr and ( "还" in context or "偿" in context or "限" ):
                            flag = 1
                            break
                        elif "实际交付时间" in attr and  ( "转" in context or "付" in context or "收" in context or "借" in context):
                            flag = 1
                            break
                        elif "已还款时间" in attr and ( ("还" in context or "偿" in context) and "已" in context):
                            flag = 1
                            break
            if flag == 1:
                ret.append( self.sentence_doc[entity][i] )
        return ret

############################################ 金额 #########################################
class MoneyTextCapture( TextCapture ):
    """
    针对一个句子：捕获一个句子中所有xx元格式的数据
    """
    def __init__(self, text: str, context_length = 10, orient = "all"):
        self.match_word = re.compile(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:万)?元')
        super().__init__( text, self.match_word, context_length, orient)
        self.money_dict = {}
        self.all_money_capture()
    
    # 获取一个句子所有金额要素及其上下文
    def all_money_capture( self ):
        for money in self.matched_words:
            contexts = self.get_context( money ) 
            if money not in self.money_dict:
                self.money_dict[ money ] = contexts
            else:
                self.money_dict[ money ].extend( contexts )

class CplDocumentMoneyTextCapture( CplParagraphSplit ):
    """（元）"""
    def __init__(self, doc, context_length = 10, orient = "all", _seps = [ "。", "；"]):
        super().__init__( doc, MoneyTextCapture, context_length, orient, _seps)

    def get_attr_context_dict( self, entity) -> List[dict]:
        """指定实体和属性，返回所有句子中的日期数据及其相关的上下文字典"""
        ret = []
        sub_list = self.map_dict[entity]            # 获得本文该对象名下所有含有日期的句子的字典
        # 遍历每个句子，获取金额字典
        for i in range(len(sub_list)):
            text_capture = sub_list[ i ]            # 句子对应的金额字符串字典
            money_dict = text_capture.money_dict
            ret.append( money_dict )
        return ret
    
    def get_related_context( self , entity, attr)-> List[dict]:
        """对该部分的所有字句都进行基于entity和attr的判断，返回对应的上下文"""
        part_dict_list = self.get_attr_context_dict( entity )
        # 遍历每个句子存放该篇文档针对entity实体的attr的属性的句子列表
        ret = []                                    
        for i in range( len(part_dict_list) ):
            date_dict = part_dict_list[i]           # 获取针对一行的所有金额数据
            flag = 0
            # 遍历当前句子中所有金额格式的数据：获取数据对应的上下文列表，
            for date in date_dict.keys():
                if flag == 1:                       # 若已经验证通过，提前退出
                    break
                contexts = date_dict[date]
                if len(contexts)==0:
                    continue
                else:
                    # 遍历列表判断是否符合要求
                    for context in contexts:
                        if len(context.strip()) > 0:
                            # 对不同的日期数据进行分类讨论
                            if "返回本金总额" in attr and ("还" in context or "本金"):
                                flag = 1
                                break
                            elif "返回利息总额" in attr and ("利息" in context):
                                flag = 1
                                break
                            elif "返回违约金总额" in attr and ( "违约" in context or "罚" in context ):
                                flag = 1
                                break
                            elif "约定的借款金额" in attr and ( "借" in context ):
                                flag = 1
                                break
                            elif "借款实际交付金额" in attr and ( "转" in context or "付" in context or "收到" in context or "借出" in context):
                                flag = 1
                                break
                            elif "已还款金额" in attr and ( ("还" in context or "偿" in context or "收到" in context ) and "已" in context):
                                flag = 1
                                break
            if flag == 1:
                ret.append( self.sentence_doc[entity][i] )
        return ret

############################################ 比例 #########################################
class RatioTextCapture( TextCapture ):
    """
    针对一个句子：捕获一个句子中所有xx%格式的数据
    """
    def __init__(self, text: str, context_length = 10, orient = "all"):
        self.match_word = re.compile( r'\d{1,2}(\.\d{1,2})?%' )
        super().__init__( text, self.match_word, context_length, orient)
        self.dict = {}
        self.all_capture()
    
    def all_capture( self ):
        for money in self.matched_words:
            if len( money.strip() )>0:
                contexts = self.get_context( money ) 
                if money not in self.dict:
                    self.dict[ money ] = contexts
                else:
                    self.dict[ money ].extend( contexts )

class CplDocumentRatioTextCapture( CplParagraphSplit ):
    """%"""
    def __init__(self, doc, context_length = 10, orient = "all", _seps = [ "。", "；"]):
        super().__init__( doc, RatioTextCapture, context_length, orient, _seps)

    def get_attr_context_dict( self, entity) -> List[dict]:
        """指定实体和属性，返回所有句子中的比例数据及其相关的上下文字典"""
        ret = []
        sub_list = self.map_dict[entity]            # 获得本文该对象名下所有含有日期的句子的字典
        # 遍历每个句子，获取金额字典
        for line in sub_list:
            text_capture = line         # 句子对应的金额字符串字典
            dict = text_capture.dict
            ret.append( dict )
        return ret
    
    def get_related_context( self , entity, attr)-> List[dict]:
        """对该部分的所有字句都进行基于entity和attr的判断，返回对应的上下文"""
        part_dict_list = self.get_attr_context_dict( entity )
        # 遍历每个句子存放该篇文档针对entity实体的attr的属性的句子列表
        ret = []                                    
        for i in range( len(part_dict_list) ):
            date_dict = part_dict_list[i]           # 获取针对一行的所有金额数据
            flag = 0
            # 遍历当前句子中所有金额格式的数据：获取数据对应的上下文列表，
            for date in date_dict.keys():
                if flag == 1:                       # 若已经验证通过，提前退出
                    break
                contexts = date_dict[date]
                if len(contexts)==0:
                    continue
                else:
                    # 遍历列表判断是否符合要求
                    for context in contexts:
                        # 对不同的日期数据进行分类讨论
                        if "返还利息率数值" in attr and ("息" in context or "率" in context):
                            flag = 1
                            break
                        elif "返还违约金数值" in attr and ("违约" in context or "罚" in context or "息" in context or "率" in context):
                            flag = 1
                            break
                        elif "约定的利率数值" in attr and ( "利" in context or "率" in context or "约定" in context):
                            flag = 1
                            break
                        elif "约定的逾期利率数值" in attr and ( "利" in context or "率" in context or "约定" in context):
                            flag = 1
                            break
                        elif "约定的违约金数值" in attr and ( "违约" in context or "罚" in context or "约定" in context or "息" in context or "率" in context):
                            flag = 1
                            break
            if flag == 1:
                ret.append( self.sentence_doc[entity][i] )
        return ret
    

if __name__=="__main__":
    _MODE = "test"
    if _MODE == "test":
        predict_lists, prompt_lists, label_lists, texts, core_ruled_text, entity_lists = load_mat( _MODE )
    
    core_text = core_ruled_text[0]
    ratio_doc = CplDocumentRatioTextCapture( core_text )
    #money_doc = CplDocumentMoneyTextCapture( core_text )
    #date_doc = CplDocumentDateTextCapture( core_text )
    ratio_doc.get_related_context( "法院", "初始约定的利率数值（百分比或元）")
    print("sss")