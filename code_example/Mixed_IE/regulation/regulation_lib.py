import re

'''
正则匹配规则
re.compile(r'清单\\n', re.DOTALL)
re.compile(r'(\d{4})(.{1,20})号', re.DOTALL)
()表示捕获组(只有捕获组才会被findall()返回)。例如(.*?)用于匹配任意数量的任何字符，但尽量少地匹配（即非贪婪匹配）
    如果你想要得到整个匹配项，包括捕获组和非捕获组的部分，你可以不使用捕获组，或者使用 re.finditer() 方法，它可以返回 Match 对象，你可以通过 Match 对象的 group(0) 或 group() 方法来获取整个匹配项。
(好|是)表示或者:
    text = "你好，你是我的朋友。"  
    pattern = re.compile(r'你(好|是)')  
    for match in pattern.finditer(text):  
        print(match.group(0))  # 输出：'你好' 和 '你是'


^表示字符串开头，$表示结尾
\d表示数字，等价于字符集[0-9]
. 匹配除了换行符之外的任何字符（在默认模式下）
* 匹配前面的子模式零次或多次。
+ 表示前面的字符或子表达式必须出现一次或多次
? 
    匹配零次或一次：问号可以用于指定前面的字符或子表达式可以出现零次或一次。例如，正则表达式a?b可以匹配字符串“b”、“ab”和“aab”中的“b”或“ab”。
    非贪婪匹配：当问号跟在量词（如*、+、?或{n}）后面时，使该量词变为非贪婪模式，即尽量少地匹配字符。
    非捕获组：在括号开头的地方加上问号和冒号（?:），可以创建一个非捕获组。这个组只用于分组而不会被捕获，主要用于控制分组的优先级或在重复匹配中避免生成不必要的捕获组。例如，正则表达式(?:abc)+可以匹配字符串“abc”、“abcabc”等，但不会生成捕获组。
{0:3}或{4}表示限定前一个字符的个数，如.{四个任意字符}

[]字符集，如[a-z]， [a-zA-Z0-9]，[\u4e00-\u9fa5]中文字符集，re.compile(r'(\d{4})([\u4e00-\u9fa5]{1,20})号', re.DOTALL)
re.DOTALL表示不换行
'''

# 创建一个小的字符集来匹配年份、月份和日期  
year_chars = r'一二三四五六七八九十〇O零'  
month_chars = r'元一二三四五六七八九十'  
day_chars = month_chars  

regulations = {
    "Block" : [ 
        re.compile(r'(\d{4})(.{1,20})号\\n', re.DOTALL),       # 案号匹配，全部
        re.compile(r'\\n附(.{0,30})(\\n|：)', re.DOTALL),        # 附录部分分隔符
        re.compile(r'清单\\n', re.DOTALL)                   # 一个匹配
        ],
    "Subblock":[
        re.compile( r'，(男|女)(，|。)'),                    # Total: 851, zero 325, multi 500
        re.compile( r'审理终结。'),                       # Total: 851, zero 64, multi 0
        re.compile(r'(原告|申请人)(.{2,20})(提起诉讼|诉称|请求|申请)', re.DOTALL),     # 第一块
        re.compile(r'^原告(.*?)诉讼请求', re.DOTALL),                     # 第一块
        re.compile(r'^(?!.*。).*$'),                    # 不存在句号的单独句子
        re.compile(r'^(?!.*，).*$'),                    # 不存在逗号号的单独句子
        re.compile(r'^[^。]*。$') ,                      # 只存在句尾一个句号的句子
        re.compile(r'^.{0,10}：(.*)$') ,        # 句子中冒号前最多是个字符
        "如不服本判决",                      # Total: 851, zero 27, multi 0
        "判决如下：",                         # Total: 851, zero 21, multi 0
        "事实和理由：",                        # Total: 851, zero 661, multi 0
    ],
    "Element" : [
        re.compile(rf'([{year_chars}]+年)([{month_chars}]+月)([{day_chars}]+日)(\\n|\\)') ,              # 末尾年月日匹配，Total: 851, zero 0, multi 0
        re.compile(r'\d{4}年'),
        re.compile(r'([1-9]|1[0-2])月')
    ]
}
    
_SEPARATORS = [ 
    [
        regulations["Block"][0], 
        regulations["Block"][1],
        regulations["Block"][2],
        regulations["Element"][0]
    ], 
    [
        regulations["Subblock"][1],
        regulations["Subblock"][2],
        regulations["Subblock"][5],
        regulations["Subblock"][6],
        regulations["Subblock"][7],
        regulations["Subblock"][4],
        
    ] 
]
