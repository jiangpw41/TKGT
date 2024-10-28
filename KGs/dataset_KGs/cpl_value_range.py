# kgs：序号从零开始

value_range = {
    "是否":["是", "否"],
    "字段原文" : str,
    "借贷关系角色" : ["出借人（原告）", "借款人（被告）", "担保人（被告）", "其他诉讼参与人"],
    "借款次数情况" : ["单笔借款", "完全不区分的多笔借款", "完全区分的多笔借款", "不全区分的多笔借款", "将利息计入本金的新借款"],
    "案件复杂情况" : ["普通借贷案件", "复杂借贷案件"],
    "代理人员角色类型" : ["委托代理人", "法人代表"],
    "字符串列表" : [str],
    "数值" : int,       # 从0开始
    "字符串" : str,
    "日期值" : str,       # 待定义
    "金额性质": [
        "本金",
        "利息",
        "逾期利息",
        "违约金"
    ],
    "起始日期类型": [
        "借款合同订立日",
        "借款实际交付日",
        "利息冲抵日",
        "起诉日",
        "借款合同订立日&借款实际交付日",
        "无息借款到期日",
        "本判决确定的给付之日",
        "立案日",
        "分期付款违约日",
        "重新确认债权债务之日"
    ],
    "截止日期类型": [
        "约定支付本息日",
        "起诉日",
        "实际履行完毕日",
        "暂算日",
        "诉状送达日",
        "本判决确定给付之日"
    ],
    "金额" : int,       #（元）
    "利率类型": [
        "年利率",
        "年利息",
        "月利率",
        "月利息",
        "日利率",
        "日利息",
        "中国人民银行同期同档次贷款基准利率",
        "贷款市场报价利率(LPR)",
        "中国人民银行同期同档次贷款基准利率的四倍",
        "贷款市场报价利率(LPR)的四倍",
        "同国家规定/司法保护上限",
        "借款额的占比",
        "约定的数额（固定数额）",
        "年固定分红",
        "月固定分红",
        "日固定分红"
    ],
    "率数值": str,          #"率类型": "年利率，是指借贷双方直接约定每年需支付的利息率，如“每年按照借款的24%支付利率”、“每年按照借款的0.24支付利率”，输入“24%”\n年利息，是指借贷双方直接约定每年需支付的利息总额，如“每年支付利息2000元”、“每年支付利息2千元”，输入“2000”\n月利率，是指借贷双方直接约定每月需支付的利息率，如“每月按照借款的2%支付利率”、“每月按照借款的0.02支付利率”、“两分利”，输入“2%”\n月利息，是指借贷双方直接约定每年需支付的利息总额，如“每月支付利息200元”、“每月支付利息两百元”，输入“200”\n日利率，是指借贷双方直接约定每月需支付的利息率，如“每日按照借款的0.2%支付利率”、“每日按照借款的千分之二支付利率”，输入“0.2%”\n日利息，是指借贷双方直接约定每日需支付的利息总额，如“每日支付利息1000元”、“每日支付利息一千元”，输入“1000”"
    "担保责任类型": [
        "连带保证责任",
        "一般保证责任",
        "拍卖担保物"
    ],
    "费用类型": [
        "催讨费",
        "差旅费",
        "律师费",
        "保全费"
    ],
    "借款用途": [
        "经营性借贷",
        "消费性借贷",
        "债权受让",
        "债务受让",
        "资金周转",
        "购房购车装修",
        "为他人借款",
        "投资款",
        "其他"
    ],
    "借款人与出借人关系类型": [
        "亲戚",
        "朋友",
        "同事",
        "经亲戚介绍",
        "经朋友介绍",
        "经同事介绍",
        "经第三方平台撮合",
        "房屋租赁关系",
        "同村村民",
        "邻居"
    ],
    "借款凭证类型": [
        "借条",
        "欠条",
        "借款合同",
        "口头",
        "收条",
        "咨询服务协议",
        "债权确认备忘录",
        "合伙协议"
    ],
    "交付方式类型": [
        "银行转账",
        "现金支付",
        "微信支付宝电子转账",
        "信用卡代刷",
        "转账",
        "打款",
        "直接交付第三人",
        "通过第三人交付",
        "通过第三人向第四人交付",
        "以利息计入本金方式交付"
    ],
    "约定程序性费用承担情况类型": [
        "出借人承担",
        "借款人承担",
        "共同承担",
        "违约方承担"
    ],
    "借款次数情况": [
        "单笔借款",
        "完全不区分的多笔借款",
        "完全区分的多笔借款",
        "不完全区分的多笔借款",
        "将利息计入本金的新借款"
    ],
    "约定情况": [
        "口头约定",
        "书面约定",
        "未约定"
    ],
    "案件复杂情况": [
        "普通借贷案件",
        "案情比较复杂",
        "P2P类案件",
        "明股实债"
    ],
    "起诉前后类型": [
        "起诉前",
        "起诉后"
    ],
    "约定还款方式类型": [
        "按月等额偿还",
        "按年等额偿还",
        "按半年等额偿还",
        "按季度等额偿还",
        "到期一次性偿还（到期还本/付息）",
        "期初一次性扣除（砍头息）",
        "按月偿还",
        "按年偿还",
        "按半年偿还",
        "按季度偿还"
    ],
    "已还款总体情况类型": [
        "本金全部未返还【无息借款】",
        "本金部分未返还【无息借款】",
        "本金全部返还、利息全部返还",
        "本金全部返还、利息部分返还",
        "本金全部返还、利息全部未返还",
        "本金部分返还、利息全部返还",
        "本金部分返还、利息部分返还",
        "本金部分返还、利息全部未返还",
        "本金全部未返还、利息全部返还",
        "本金全部未返还、利息部分返还",
        "本金全部未返还、利息全部未返还"
    ],
    "已还款金额性质": [
        "本金",
        "利息",
        "逾期利息",
        "违约金"
    ],
    "担保方式类型": [
        "抵押",
        "质押",
        "保证人"
    ],
    "担保人类型": [
        "个人担保",
        "一般公司企业担保",
        "担保公司担保"
    ],
    "法院对夫妻债务的认定": [
        "属于夫妻共同债务",
        "不属于夫妻共同债务"
    ],
    "法院对砍头息的认定": [
        "存在砍头息",
        "不存在砍头息"
    ],
    "法院对公司为股东担保的效力的认定": [
        "有效",
        "无效"
    ],
    "债权取得类型": [
        "债权受让",
        "债务受让"
    ],
    "法院对主体资格与合同效力的认定": [
        "主体资格使合同无效",
        "主体资格有瑕疵，但合同有效",
        "主体资格无瑕疵"
    ],
    "法院对职业放贷人的认定": [
        "构成职业放贷人",
        "不构成职业放贷人"
    ],
    "承担举证责任方": [
        "借款人",
        "出借人",
        "担保人",
        "法院"
    ],
    "法院对民事案件的处理程序": [
        "继续审理",
        "中止诉讼",
        "驳回起诉"
    ],
} 


special_issue = {
    "夫妻共同债务" : {
        "法院认定" : value_range["法院对夫妻债务的认定"],
        "法院说理原文":  value_range["字符串"],
    },
    "砍头息" : {
        "法院认定" : value_range["法院对砍头息的认定"],
        "法院说理原文":  value_range["字符串"],
    },
    "公司为股东担保" : {
        "法院认定" : value_range["法院对公司为股东担保的效力的认定"],
        "法院说理原文":  value_range["字符串"],
    },
    "债权/债务非原始取得" : {
        "债券取得类型" : value_range["法院对夫妻债务的认定"],
        "转让人" : value_range["字符串"],
        "继受人" : value_range["字符串"],
    },
   "出借人主体资格问题":{
        "法院认定" : value_range["法院对主体资格与合同效力的认定"],
        "说理原文" : value_range["字符串"],
    },
    "职业放贷人":{
        "法院认定" : value_range["法院对职业放贷人的认定"],
        "承担举证责任方" : value_range["承担举证责任方"],
        "说理原文" : value_range["字符串"],
    },
    "互联网平台责任":{
        "法院认定" : value_range["是否"],
        "说理原文" : value_range["字符串"],
    },
    "民刑交叉":{
        "法院处理程序" : value_range["法院对民事案件的处理程序"],
        "说理原文" : value_range["字符串"],
    },
    "利率调整、认定":{
        "说理原文" : value_range["字符串"],
    }
}

# 知识图谱架构与取值表
## 案件总体类属性
case_class = {
    "案号" : value_range["字符串"],
    "案件名称" : value_range["字符串"],
    "借款次数情况" : value_range["借款次数情况"],
    "案件复杂情况" : value_range["案件复杂情况"],
    "是否存在错判情形" : value_range["是否"],
    "是否存在判决书笔误" : value_range["是否"],
    "案件简要评述" : value_range["字符串"],
    "结案日期" : value_range["日期值"],                      # 非表必需
    "专题问题" : special_issue
}

case_value = {
    "class_reference":case_class,
    "案号" : None, 
    "案件名称" : None, 
    "借款次数情况" : None, 
    "案件复杂情况" : None, 
    "是否存在错判情形" : None, 
    "是否存在判决书笔误" : None, 
    "案件简要评述" : None, 
    "结案日期" : None,                    # 非表必需
    "专题问题" : None, 
}


#####################################################（Role）####################################################
court_class = {
    "姓名名称" : value_range["字符串"],                  # 非表必需
    "位置" : value_range["字符串"],                      # 非表必需
    "审判长" : value_range["字符串"],                    # 非表必需
    "书记员" : value_range["字符串"],                    # 非表必需
    "人民陪审员" : value_range["字符串列表"]              # 非表必需
}

court_value = {
    "class_reference":court_class,
    "法院名称" : None,                  # 非表必需
    "位置" : None,                      # 非表必需
    "审判长" : None,                    # 非表必需
    "书记员" : None,                    # 非表必需
    "人民陪审员" : None,             # 非表必需
}


agent_role_class = {
    "姓名名称" : value_range["字符串"],
    "出庭情况" : value_range["是否"],
    "角色类型" : value_range["代理人员角色类型"],
    "所属机构" : value_range["字符串"],                     # 非表必需
}

agent_role_value = {
    "class_reference":agent_role_class,
    "姓名名称" : None,
    "出庭情况" : None,
    "角色类型" : None,
    "所属机构" : None,                   # 非表必需
}


case_role_class = {
    "姓名名称": value_range["字符串"],
    "借贷关系角色" : value_range["借贷关系角色"],
    "同类角色序号" : value_range["数值"],
    "代理人" : [agent_role_class]
}

case_role_value = {
    "class_reference":case_role_class,
    "姓名名称": None,
    "借贷关系角色" : None,
    "同类角色序号" : None,
    "代理人" : None,
}


case_person_class = {
    "姓名名称": value_range["字符串"],
    "借贷关系角色" : value_range["借贷关系角色"],
    "同类角色序号" : value_range["数值"],
    "代理人" : [agent_role_class],
    "出庭情况" : value_range["是否"],
    "角色类型" : value_range["代理人员角色类型"],
    "所属机构" : value_range["字符串"], 
}

case_person_value = {
    "class_reference":case_person_class,
    "姓名名称": None,
    "借贷关系角色" : None,
    "同类角色序号" : None,
    "代理人" : None,
    "出庭情况" : None,
    "角色类型" : None,
    "所属机构" : None, 
}

Roles_class = {
    ## 法院角色：含人员
    "court_class" : court_class,

    ## 代理人角色
    "agent_role_class" : agent_role_class,

    ## 当事人角色：除了法院以外的借贷关系角色
    "case_role_class" : case_role_class,
}
####################################################（Thing）###########################################
# 日期类

start_date_class = {
    "日期数值":value_range["日期值"],
    "日期类型" :value_range["起始日期类型"]
}

end_date_class = {
    "日期数值":value_range["日期值"],
    "日期类型" : value_range["截止日期类型"]
}

# 利息率类
interest_rate_class = {
    "数值" : value_range["率数值"],
    "类型" : value_range["利率类型"]
}

# 需返回利息
required_interest_class = {
    "是否属于逾期利息类型" : value_range["是否"],
    "总额" : value_range["金额"],
    "计算起始日期" : [start_date_class],
    "计算截止日期" : [end_date_class],
    "利息率" : interest_rate_class
}

# 需返回违约金
required_damages_class = {
    "总额" : value_range["金额"],
    "计算起始日期" : [start_date_class],
    "计算截止日期" : [end_date_class],
    "违约金类型和数值" : interest_rate_class
}

# 担保责任情况类
guarantee_liability_class = {
    "承担保证责任的人或单位名称" : value_range["字符串"],
    "保证责任类型" : value_range["担保责任类型"]
}

# 债权实现费用类
debt_realization_costs_class = {
    "总额": value_range["金额"],
    "类型": value_range["费用类型"]
}

# 借款凭证类
voucher_class = {
    "名称" : value_range["字符串"],
    "类型" : value_range["借款凭证类型"],
    "出具时间" : value_range["日期值"],
    "所载内容" : value_range["字符串"],         # 只有原文，没有值
}

# 约定的借款金额类
agreed_lend_money_class = {
    "约定情况" : value_range["约定情况"],
    "实际发生时间" : value_range["日期值"],
    "金额" : value_range["金额"]
}
# 约定的还款日期或借款期限
agreed_return_data_class = {
    "约定情况" : value_range["约定情况"],
    "实际发生时间" : value_range["日期值"],
    "借款起始日期" : value_range["日期值"],
    "还款日期" : value_range["日期值"],
    "借款期限（月）": value_range["数值"],      # 以月为计数单位
}

# 约定的利息
agreed_interest_class = {
    "约定情况" : value_range["约定情况"],
    "实际发生时间" : value_range["日期值"],
    "约定的利率" : interest_rate_class
}

# 约定的违约金
agreed_damages_class = {
    "约定情况" : value_range["约定情况"],
    "实际发生时间" : value_range["日期值"],
    "约定的违约金类型和数值" : interest_rate_class
}

# 程序性费用的承担（律师费、诉讼费等）约定
agreed_procedure_cost_class = {
    "约定情况" : value_range["约定情况"],
    "约定程序性费用承担情况类型" : value_range["约定程序性费用承担情况类型"],
}

# 约定的还款方式
agreed_return_methods_class = {
    "约定情况" : value_range["约定情况"],
    "实际发生时间" : value_range["日期值"],
    "本金还款方式" : value_range["约定还款方式类型"],
    "利息还款方式" : value_range["约定还款方式类型"],
    "前述还款方式下每次还款总金额": value_range["金额"],      # 以月为计数单位
    "前述还款方式下每次还款日期": value_range["日期值"],      # 以月为计数单位
}

# 约定的担保
agreed_guarantee_class = {
    "约定情况" : value_range["约定情况"],
    "实际发生时间" : value_range["日期值"],
    "担保方式类型" : value_range["担保方式类型"],
    "担保范围" : value_range["字符串"],                 # 原文
    "担保期限（月）": value_range["金额"],              # 以月为计数单位
    "担保物当下状态": value_range["字符串"],                 # 原文
    "担保人类型": value_range["担保人类型"], 
    "保证责任类型": value_range["担保责任类型"], 
}

# 借款实际交付类
actual_delivery_class = {
    "金额" : value_range["金额"],
    "时间" : value_range["日期值"],
    "交付方式类型" : value_range["交付方式类型"],
    "对应的是第几笔借款" : value_range["数值"],
}

# 已还款类
repaid_class = {
    "时间" : value_range["日期值"],
    "金额" : value_range["金额"],
    "方式" : value_range["交付方式类型"],
    "金额性质" : value_range["金额性质"],
    "对应的是第几笔借款" : value_range["数值"],
    "已还款金额所冲抵利息至哪一日" : value_range["日期值"],
}

Thing_class = {
    "start_date_class" : start_date_class,

    "end_date_class" : end_date_class,

    "interest_rate_class" : interest_rate_class,

    "required_interest_class" : required_interest_class,

    "required_damages_class" : required_damages_class,

    "guarantee_liability_class" : guarantee_liability_class,

    "debt_realization_costs_class" : debt_realization_costs_class,

    "voucher_class" : voucher_class,

    "agreed_lend_money_class" : agreed_lend_money_class,

    "agreed_return_data_class" : agreed_return_data_class,

    "agreed_interest_class" : agreed_interest_class,

    "agreed_damages_class" : agreed_damages_class,

    "agreed_procedure_cost_class" : agreed_procedure_cost_class,

    "agreed_return_methods_class" : agreed_return_methods_class,

    "agreed_guarantee_class" : agreed_guarantee_class,

    "actual_delivery_class" : actual_delivery_class,

    "repaid_class" : repaid_class
}


####################################################（Event）###########################################
# 有两种类型的取值：
#   （1）来自value_range字典的取值，修改自数据集采集规范
#   （2）来自Thing_class字典取值，对一些专属概念进行了类封装以复用，类中取值依旧来自value_range字典
# 诉讼请求类
request_class = {
    "是否变更诉讼请求" : value_range["是否"],
    "需返回本金总额" : value_range["金额"],
    "需返回利息" : [Thing_class["required_interest_class"]],
    "需返回逾期利息" : [Thing_class["required_interest_class"]],
    "需返回违约金" : [Thing_class["required_damages_class"]],
    "是否要求承担担保责任" :[Thing_class["guarantee_liability_class"]],     # 为空则不要求，否则列表形式
    "需返回债权实现费用" : Thing_class["debt_realization_costs_class"]
}

# 借款事件类
borrow_class = {
    # 借款事实
    "借款目的与用途" : value_range["借款用途"],
    "借款人与出借人关系类型" : value_range["借款人与出借人关系类型"],
    "担保人的姓名或单位名称" : value_range["字符串"],
    "借款人与担保人关系类型" : value_range["借款人与出借人关系类型"],
    "意思表示日" : value_range["日期值"],
    "借款次数" : value_range["数值"],
    "借款次数情况" : value_range["借款次数情况"],
    "是否有借款凭证" : [Thing_class["voucher_class"]],
    # 约定事实
    "约定的借款金额" : [Thing_class["agreed_lend_money_class"]],
    "约定的还款日期或借款期限" : [Thing_class["agreed_return_data_class"]],
    "约定的利息" : [Thing_class["agreed_interest_class"]],
    "约定的逾期利息" : [Thing_class["agreed_interest_class"]],
    "约定的违约金" : [Thing_class["agreed_damages_class"]],
    "管辖约定情况" : value_range["约定情况"],
    "仲裁约定情况" : value_range["约定情况"],
    "程序性费用的承担（律师费、诉讼费等）约定" : Thing_class["agreed_procedure_cost_class"],
    "约定的还款方式" : [Thing_class["agreed_return_methods_class"]],
    "约定的担保" : [Thing_class["agreed_guarantee_class"]],
    # 交付与还款事实
    "借款实际交付" : [Thing_class["agreed_guarantee_class"]],
    "已还款总体情况类型" : value_range["已还款总体情况类型"],
    "已还款" : [Thing_class["repaid_class"]],
}