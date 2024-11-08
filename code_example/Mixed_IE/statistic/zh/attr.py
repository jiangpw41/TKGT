'''
注释：案件角色实例、案件要素字段
1.对于一组案件要素：法院、原告方、被告方有各自的陈述角度，一般是当事人双方各自陈述诉求、阐述事实、列举证据，法院则作为裁判第三方对上述所有信息进行真实有效性分析和认定
2.Row_Name：原则上，在每个案件实例中，五类角色都可多个实例，事实上，只有后三个角色可能会有多个实例。多个实例的时候，第二个开始在结尾增加1开始的编号（即第一个实例无编号）
3.Value_Type：大部分变量取值都有原文依据，少部分取值就是原文本身。
4.Columns_Field：一个案件的基本要素，分为案件角色实例相关信息、诉讼请求信息、事实理由信息、专题问题四部分
因此，表格为三维，第一个维度是角色实例，第二个维度是取值类型，第三个维度是案件要素字段。
“字段原文”类型默认为从原文摘取的字符串，“变量取值”则各自有不同的取值类型、范围定义，两者共享其他两个维度，故只列出“变量取值”情况。
一个字段如果只需要原文，那么“变量取值”部分使用 value_range["字段原文"]
'''
import sys
import os
sys.path.insert(0, os.path.dirname( os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__) )))))
from kgs.dataset_kgs.CPL_kg import value_range, case_class, Roles_class, Thing_class, request_class, borrow_class

CPL_Table_Basic = [
    "案号",
    "案件名称",
    "借款次数情况",
    "案件复杂情况",
    "是否存在错判情形",
    "是否存在判决书笔误",
    "案件简要评述",
    "结案日期",
]

CPL_Table_Case = {
    "Row_Name" : [
        "法院",
        "出借人（原告）", 
        "借款人（被告）", 
        "担保人（被告）", 
        "其他诉讼参与人"
    ],
    "Value_Type" : [
        "字段原文",
        "变量取值",
    ],
    "Columns_Field" : {
        # 角色实例信息：法院可以没有该类信息
        "姓名名称" : value_range["字符串"],
        "相关诉讼参与人1姓名" : value_range["字符串"],
        "相关诉讼参与人1出庭情况" : value_range["是否"],
        "相关诉讼参与人2姓名" : value_range["字符串"],
        "相关诉讼参与人2出庭情况" : value_range["是否"],
        "相关诉讼参与人3姓名" : value_range["字符串"],
        "相关诉讼参与人3出庭情况" : value_range["字符串"],

        # 诉讼请求：围绕原告诉讼请求，被告可能辩称，法院则可能驳回、支持等
        "是否变更诉讼请求" : value_range["是否"],
        "需返回本金总额" : value_range["金额"],
        "需返回利息" : [Thing_class["required_interest_class"]],
        "需返回逾期利息" : [Thing_class["required_interest_class"]],
        "需返回违约金" : [Thing_class["required_damages_class"]],
        "是否要求承担担保责任" :[Thing_class["guarantee_liability_class"]],     # 为空则不要求，否则列表形式
        "需返回债权实现费用（起诉前）" : Thing_class["debt_realization_costs_class"],
        "需返回债权实现费用（起诉后）" : Thing_class["debt_realization_costs_class"],

        # 借款事件：含各方对借款事实信息、约定事实信息、交付与还款事实信息的陈述
            # 借款事实信息
        "借款目的与用途" : value_range["借款用途"],
        "借款人与出借人关系类型" : value_range["借款人与出借人关系类型"],
        "担保人的姓名或单位名称" : value_range["字符串"],
        "借款人与担保人关系类型" : value_range["借款人与出借人关系类型"],
        "意思表示日" : value_range["日期值"],
        "借款次数" : value_range["数值"],
        "借款次数情况" : value_range["借款次数情况"],
        "是否有借款凭证" : [Thing_class["voucher_class"]],
            # 约定事实信息
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
            # 交付与还款事实信息
        "借款实际交付" : [Thing_class["agreed_guarantee_class"]],
        "已还款总体情况类型" : value_range["已还款总体情况类型"],
        "已还款" : [Thing_class["repaid_class"]],

        # 专题问题：案件文本中关于特殊问题的部分
        "夫妻共同债务": value_range["法院对夫妻债务的认定"],
        "砍头息" : value_range["法院对砍头息的认定"],
        "公司为股东担保" : value_range["法院对公司为股东担保的效力的认定"],
        "债权/债务非原始取得" : value_range["法院对夫妻债务的认定"],
        "出借人主体资格问题" : value_range["法院对主体资格与合同效力的认定"],
        "职业放贷人" : value_range["法院对职业放贷人的认定"],
        "互联网平台责任" : value_range["是否"],
        "民刑交叉" : value_range["法院对民事案件的处理程序"],
        "利率调整、认定" : value_range["字段原文"],
    }
}