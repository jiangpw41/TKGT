
from tqdm import tqdm
import sys
import os
import json

def load_tokenizer( _LLM_PATH, vocal_file ):
    sys.path.insert(0, _LLM_PATH)
    from tokenization_chatglm import SPTokenizer
    return SPTokenizer( os.path.join(_LLM_PATH, vocal_file))

def read_text_to_list( path ):
    with open(path, 'r') as file:  
        lines = file.readlines()
    strings_read = []
    for line in lines:
        if line.endswith("\n"):
            line = line[:-1]
        strings_read.append( line )
    return strings_read

def trim_( to ):
    if( to[0]== '▁' ):
        to = to[1:]
    elif( to[0].startswith('▁') ):
        to[0] = to[0][1:]
    return to

def layer_aware_split(original_string:str, separators:list, tokenizer):  
    '''
    Recursivily, turning the str into a m-dimension list
    param original_string: string
    param separators: [[],[],[]], n-dimension separator list, with same level within the list while priority given to order between lists.
    '''
    _SPECIAL_SEPARATOR = "<SJTU_IEEE_LAW>"
    original_string = original_string.replace(" ","")
    if len(separators)==0 or len(original_string)==0:
        return original_string
    
    sep_list = separators[0]
    rest_sep = separators[1:]

    # Firstly, split a string into a list of substrings
    for separator in sep_list:  
        original_string = original_string.replace(separator, _SPECIAL_SEPARATOR )
    splited = list(filter(None,original_string.split(_SPECIAL_SEPARATOR) ))
    # Secondly, recursive processing of substrings in lis
    if(len(rest_sep)>0):
        ret = []
        for i in range(len(splited)):
            ret.append( layer_aware_split(splited[i], rest_sep, tokenizer) )
        return ret
    else:
        # Sentence
        if( len(splited)==1 ):
            return trim_(tokenizer.tokenize(splited[0]))
        else:
            ret = []
            for sent in splited:
                ret.append( trim_(tokenizer.tokenize( sent ) ) )
            return ret
        

if __name__=="__main__":
    original_string = '安徽省合肥市包河区人民法院\\n民 事 判 决 书\\n(2016)皖0111民初3584号\\n原告：卢江平，男，1975年5月24日出生，汉族，住浙江省东阳市，\\n委托代理人：张学奇，安徽里奇律师事务所律师。\\n被告：刘维辉，男，1977年3月22日出生，汉族，住安徽省合肥市包河区，\\n委托代理人：沈国松，北京盈科（合肥）律师事务所律师。\\n委托代理人：唐婷婷，北京盈科（合肥）律师事务所实习律师。\\n原告卢江平诉被告刘维辉民间借贷纠纷一案，本院于2016年3月29日立案受理。依法由审判员方业泉适用简易程序公开开庭进行了审理。原告卢江平的委托代理人张学奇，被告刘维辉的委托代理人沈国松到庭参加诉讼。本案现已审理终结。\\n原告卢江平诉称:被告自2013年10月起，以经营周转为由向原告借款。后原告分别于2013年10月10日向被告汇款630500元、于2014年4月21日向被告汇款291000元，合计921500元。2015年5月12日，因被告无法按期偿还借款，经双方对账，被告于当日向原告出具借条一张，载明欠原告707100元借款，限于2015年6月30日之前付清。还款到期后，被告拒绝偿还借款。请求法院判令被告向原告偿还借款707100元、利息22921.66元（从2015年7月1日起按同期银行6个月贷款利率计算至起诉之日，后续按照年息4.35%的标准计算至实际还款之日止），两项合计730021.66元；本案诉讼费用由被告承担。\\n被告刘维辉辩称：被告虽然出具了707100元的借条，但没有实际收到借款，原告也未提交转账凭证。请求法院驳回原告的全部诉讼请求。\\n经审理查明：被告刘维辉因缺少周转资金于2013年10月向原告卢江平提出借款，原告通过其配偶王来菊的银行卡于2013年10月10日转账支付被告630500元、于2014年4月21日转账支付被告291000元，合计921500元。经双方对账，被告于2015年5月12日向原告出具一份借条，内容为：今借到卢江平现金柒拾万零柒仟壹佰元整，此款限在2015年6月30日前付清。借条载明的还款期限届满后，被告没有归还借款。此后，原告催讨借款无果，遂于2016年3月29日向本院提起诉讼。\\n上述事实，有原告及其配偶王来菊的身份证复印件，原告结婚证复印件，借条，银行转账凭条，以及原、被告当庭陈述的内容等证实。\\n本院认为：被告刘维辉借原告卢江平人民币707100元，有借条、银行转账凭条佐证，本院予以确认。被告出具的借条约定了还款期限，未约定利息，故双方之间是定期无息借贷。被告未按约定期限归还借款是违约行为，应承担违约责任，因此，被告除应及时付清借款本金，还应支付原告逾期利息。原告请求被告按同期银行6个月贷款利率支付利息，符合法律规定，本院予以支持。据此，依照《中华人民共和国民法通则》第九十条，《中华人民共和国合同法》第二百零六条、第二百零七条之规定，判决如下：\\n被告刘维辉于本判决生效后十日内偿还原告卢江平借款本金707100元，并支付逾期利息（以707100元为基数，自2015年7月1日起按照同期银行六个月贷款利率计算至借款本金付清之日止）。\\n如果未按本判决指定的期间履行给付金钱义务，应当依照《中华人民共和国民事诉讼法》第二百五十三条之规定，加倍支付迟延履行期间的债务利息。\\n案件受理费11100元，减半收取5550元，由被告刘维辉负担。\\n如不服本判决，可在判决书送达之日起十五日内，向本院递交上诉状，并按对方当事人的人数提出副本，上诉于安徽省合肥市中级人民法院。\\n审判员\u3000\u3000方业泉\\n二〇一六年六月二十二日\\n书记员\u3000\u3000奚雨杭\\n附：本案适用的相关法律条文\\n《中华人民共和国民法通则》\\n第九十条合法的借贷关系受法律保护。\\n《中华人民共和国合同法》\\n第二百零六条借款人应当按照约定的期限返还借款。对借款期限没有约定或者约定不明确，依照本法第六十一条的规定仍不能确定的，借款人可以随时返还；贷款人可以催告借款人在合理期限内返还。\\n第二百零七条借款人未按照约定的期限返还借款的，应当按照约定或者国家有关规定支付逾期利息。'
    separators = [["诉称：", "辩称：", "经审理查明：",  "本院认为：", "判决如下：", "如不服本判决，"], ["\\n"], ["。"]]
    #ret = layer_aware_split(original_string, separators)
    print( tokenization("你好"))