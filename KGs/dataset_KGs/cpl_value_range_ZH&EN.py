# kgs：序号从零开始

value_range = {
    "是否yes_or_no":["是yes", "否no"],
    "字段原文source_text" : str,
    "借贷关系角色lending_relationship_role" : ["出借人（原告）lender", "借款人（被告）borrower", "担保人（被告）guarantor", "其他诉讼参与人others"],
    "借款次数情况lending_frequency_type" : ["单笔借款single_loan", "完全不区分的多笔借款undistinguished_multiple_loans", "完全区分的多笔借款distinguished_multiple_loans", "不全区分的多笔借款partially_distinguished_multiple_loans", "将利息计入本金的新借款rollover_of_loan_with_interest_capitalized"],
    "案件复杂情况case_complexity" : ["普通借贷案件ordinary", "复杂借贷案件complex"],
    "代理人员角色类型agent_role" : ["委托代理人authorized_agent", "法人代表legal_representative"],
    "字符串列表string_list_format" : [str],
    "数值numerical_format" : int,       # 从0开始
    "字符串string_format" : str,
    "日期值date_format" : str,       # 待定义
    "金额性质amounts_type": [
        "1=本金principal;",
        "2=利息interest;",
        "3=逾期利息overdue_interest;",
        "4=违约金liquidated_damages"
    ],
    "起始日期类型start_date_type": [
        "1=借款合同订立日;loan_agreement_establishment_date",
        "2=借款实际交付日;actual_loan_delivery_date",
        "3=利息冲抵日;interest_offset_date",
        "4=起诉日filing_suit_date",
        "1&2loan_agreement_establishment_date_and_actual_loan_delivery_date",
        "5=无息借款到期日interest_free_loan_maturity_date",
        "6=本判决确定的给付之日court_determined_payment_date",
        "7=立案日case_filing_date",
        "8=分期付款违约日installment_payments_date",
        "9=重新确认债权债务之日reconfirm_creditor_debtor_relationship_date"
    ],
    "截止日期类型end_date_type": [
        "1=约定支付本息日;stipulated_date_for_the_payment_of_principal_and_interest",
        "2=起诉日;filing_suit_date",
        "3=实际履行完毕日 actual_date_of_full_performance",
        "4=暂算日temporarily_calculated_date",
        "5=诉状送达日complaint_served_date",
        "6=本判决确定给付之日court_determined_payment_date"
    ],
    "金额amounts" : int,       #（元）
    "利率类型interest_type": [
        "1=年利率;annual_interest_rate",
        "2=年利息;annual_interest_amount",
        "3=月利率;monthly_interest_rate",
        "4=月利息;monthly_interest_amount",
        "5=日利率daily_interest_rate",
        "6=日利息daily_interest_amount",
        "7=中国人民银行同期同档次贷款基准利率pbc_lpr",
        "8=贷款市场报价利率(LPR)lpr",
        "9=中国人民银行同期同档次贷款基准利率的四倍pbc_lpr_4x",
        "10=贷款市场报价利率(LPR)的四倍lpr_4x",
        "11=同国家规定/司法保护上限limits_of_national_regulations_or_judicial_protection",
        "12=借款额的占比proportion_of_loan_amount",
        "13=约定的数额（固定数额）agreed_or_fixed_amount",
        "14=年固定分红annual_fixed_dividend",
        "15=月固定分红monthly_fixed_dividend",
        "16=日固定分红daily_fixed_dividend"
    ],
    "率数值rate_numerical_format": str,          #"率类型": "1=年利率，是指借贷双方直接约定每年需支付的利息率，如“每年按照借款的24%支付利率”、“每年按照借款的0.24支付利率”，输入“24%”;\n2=年利息，是指借贷双方直接约定每年需支付的利息总额，如“每年支付利息2000元”、“每年支付利息2千元”，输入“2000”;\n3=月利率，是指借贷双方直接约定每月需支付的利息率，如“每月按照借款的2%支付利率”、“每月按照借款的0.02支付利率”、“两分利”，输入“2%”;\n4=月利息，是指借贷双方直接约定每年需支付的利息总额，如“每月支付利息200元”、“每月支付利息两百元”，输入“200”;\n5=日利率，是指借贷双方直接约定每月需支付的利息率，如“每日按照借款的0.2%支付利率”、“每日按照借款的千分之二支付利率”，输入“0.2%”;\n6=日利息，是指借贷双方直接约定每日需支付的利息总额，如“每日支付利息1000元”、“每日支付利息一千元”，输入“1000”;"
    "担保责任类型guarantee_responsibility_type": [
        "1=连带保证责任；joint_liability",
        "2=一般保证责任；general_liability",
        "3=拍卖担保物secured_auction_collateral"
    ],
    "费用类型fee_type": [
        "1=催讨费;collection_fee",
        "2=差旅费;travel_fee",
        "3=律师费attorney_fee",
        "4=保全费preservation_fee"
    ],
    "借款用途loan_purposes_type": [
        "1=经营性借贷;business",
        "2=消费性借贷;consumer",
        "3=债权受让；right_assignment",
        "4=债务受让；debt_assignment",
        "5=资金周转；capital_turnover",
        "6=购房购车装修；purchase_house_car_renovation",
        "7=为他人借款；loan_for_others",
        "8=投资款；investment",
        "9=其他；"
    ],
    "借款人与出借人关系类型borrower_and_lender_relationship_type": [
        "1=亲戚;relatives",
        "2=朋友;friends",
        "3=同事;colleagues",
        "4=经亲戚介绍;introduced_by_relatives",
        "5=经朋友介绍;introduced_by_friends",
        "6=经同事介绍introduced_by_colleagues",
        "7=经第三方平台撮合matched_by_third_party_platform",
        "8=房屋租赁关系house_rental_relationship",
        "9=同村村民fellow_villagers",
        "10=邻居neighbors"
    ],
    "借款凭证类型loan_voucher_type": [
        "1=借条;iou_jietiao",
        "2=欠条;debt_acknowledgement_qiantiao",
        "3=借款合同;loan_contract",
        "4=口头oral",
        "5=收条receipt_shoutiao",
        "6=咨询服务协议consulting_service_agreement",
        "7=债权确认备忘录debt_confirmation_memorandum",
        "8=合伙协议partnership_agreement"
    ],
    "交付方式类型delivery_type": [
        "1=银行转账;bank_transfer",
        "2=现金支付;cash_payment",
        "3=微信支付宝电子转账;wechat_alipay_electronic_transfer",
        "4=信用卡代刷credit_card_payment_on_behalf",
        "5=转账transfer_zhuanzhang",
        "6=打款remittance_dakuan",
        "7=直接交付第三人direct_delivery_to_third_party",
        "8=通过第三人交付delivery_through_third_party",
        "9=通过第三人向第四人交付delivery_from_third_party_to_fourth_party",
        "以利息计入本金方式交付delivery_with_interest_included_in_principal"
    ],
    "约定程序性费用承担情况类型agreement_on_procedural_fee_burden_type": [
        "1=出借人承担；lender_bear",
        "2=借款人承担；borrower_bear",
        "3=共同承担jointly_bear",
        "4=违约方承担defaulting_party_bear"
    ],
    "借款次数情况lending_frequency_type": [ ##lxb##和第7行重复了
        "单笔借款single_loan",
        "完全不区分的多笔借款undistinguished_multiple_loans",
        "完全区分的多笔借款distinguished_multiple_loans",
        "不完全区分的多笔借款partially_distinguished_multiple_loans",
        "将利息计入本金的新借款rollover_of_loan_with_interest_capitalized"
    ],
    "约定情况agreed_form": [
        "1=口头约定oral_agreement",
        "2=书面约定written_agreement",
        "3=未约定unspecified_agreement"
    ],
    "案件复杂情况case_complexity": [
        "普通借贷案件ordinary",
        "案情比较复杂complex",
        "P2P类案件p2p",
        "明股实债nominal_shares_with_actual_debt"
    ],
    "起诉前后类型before_or_after_filing": [
        "起诉前before_filing_suit",
        "起诉后after_filing_suit"
    ],
    "约定还款方式类型agreed_repayment_type": [
        "1=按月等额偿还equal_monthly_repayment",
        "2=按年等额偿还equal_annual_repayment",
        "3=按半年等额偿还equal_semi_annual_repayment",
        "4=按季度等额偿还equal_quarterly_repayment",
        "5=到期一次性偿还（到期还本/付息）lump_sum_repayment_at_maturity",
        "6=期初一次性扣除（砍头息）initial_onetime_deduction_kantouxi",
        "7=按月偿还monthly_repayment",
        "8=按年偿还annual_repayment",
        "9=按半年偿还semi_annual_repayment",
        "10=按季度偿还quarterly_repayment"
    ],
    "已还款总体情况类型repayment_type": [
        "1=本金全部未返还【无息借款】principal_fully_unreturned_of_interest_free_loan",
        "2=本金部分未返还【无息借款】principal_partially_unreturned_of_interest_free_loan",
        "3=本金全部返还、利息全部返还principal_fully_returned_and_interest_fully_returned",
        "4=本金全部返还、利息部分返还principal_fully_returned_and_interest_partially_returned",
        "5=本金全部返还、利息全部未返还principal_fully_returned_and_interest_fully_unreturned",
        "6=本金部分返还、利息全部返还principal_partially_returned_and_interest_fully_returned",
        "7=本金部分返还、利息部分返还principal_partially_returned_and_interest_partially_returned",
        "8=本金部分返还、利息全部未返还principal_partially_returned_and_interest_fully_unreturned",
        "9=本金全部未返还、利息全部返还principal_fully_unreturned_and_interest_fully_returned",
        "10=本金全部未返还、利息部分返还principal_fully_unreturned_and_interest_partially_returned",
        "11=本金全部未返还、利息全部未返还principal_fully_unreturned_and_interest_fully_unreturned"
    ],
    "已还款金额性质amounts_type": [  ##lxb##"已还款金额性质"和"金额性质"一致，是否删去?
        "1=本金principal;",
        "2=利息interest;",
        "3=逾期利息overdue_interest;",
        "4=违约金liquidated_damages"
    ],
    "担保方式类型guarantee_method_type": [
        "1=抵押;mortgage",
        "2=质押;pledge",
        "3=保证人suretyship"
    ],
    "担保人类型suretyship_type": [
        "1=个人担保;personal",
        "2=一般公司企业担保;general_corporate",
        "3=担保公司担保guarantee_company"
    ],
    "法院对夫妻债务的认定court_recognition_of_marital_debt": [
        "1=属于夫妻共同债务;yes",
        "2=不属于夫妻共同债务no"
    ],
    "法院对砍头息的认定court_recognition_of_clipping_interest": [
        "1=存在砍头息;yes",
        "2=不存在砍头息no"
    ],
    "法院对公司为股东担保的效力的认定court_recognition_of_guarantee_effectiveness_for_shareholders_by_company": [
        "1=有效;yes",
        "2=无效no"
    ],
    "债权取得类型creditor_right_acquisition_type": [
        "1=债权受让；right_assignment",
        "2=债务受让debt_assignment"
    ],
    "法院对主体资格与合同效力的认定court_recognition_of_subject_qualification_and_contract_validity": [
        "1=主体资格使合同无效；subject_qualification_renders_contract_invalid",
        "2=主体资格有瑕疵，但合同有效；subject_qualification_defective_but_contract_valid",
        "3=主体资格无瑕疵。subject_qualification_without_defect"
    ],
    "法院对职业放贷人的认定court_recognition_of_professional_lender": [
        "1=构成职业放贷人；yes",
        "2=不构成职业放贷人no"
    ],
    "承担举证责任方party_bearing_burden_of_proof": [
        "1=借款人；borrower",
        "2=出借人lender",
        "3=担保人；guarantor",
        "4=法院court"
    ],
    "法院对民事案件的处理程序court_handle_procedure": [
        "1=继续审理;continue_hearing",
        "2=中止诉讼;suspend_litigation",
        "3=驳回起诉reject_lawsuit"
    ],
} 


special_issue = {
    "夫妻共同债务marital_debt" : {
        "法院认定court_hold" : value_range["法院对夫妻债务的认定court_recognition_of_marital_debt"],
        "法院说理原文court_hold_text":  value_range["字符串string_format"],
    },
    "砍头息clipping_interest" : {
        "法院认定court_hold" : value_range["法院对砍头息的认定court_recognition_of_clipping_interest"],
        "法院说理原文court_hold_text":  value_range["字符串string_format"],
    },
    "公司为股东担保company_guarantee_for_shareholder" : {
        "法院认定court_hold" : value_range["法院对公司为股东担保的效力的认定court_recognition_of_guarantee_effectiveness_for_shareholders_by_company"],
        "法院说理原文court_hold_text":  value_range["字符串string_format"],
    },
    "债权/债务非原始取得creditor_debtor_rights_acquisition" : {
        "债权取得类型creditor_right_acquisition_type" : value_range["债权取得类型creditor_right_acquisition_type"],  #此处应该是"债权取得类型",原来是"券""法院对夫妻债务的认定"
        "转让人transferor_name" : value_range["字符串string_format"],
        "继受人transferee_neme" : value_range["字符串string_format"],
    },
   "出借人主体资格问题lender_subject_qualification":{
        "法院认定court_hold" : value_range["法院对主体资格与合同效力的认定court_recognition_of_subject_qualification_and_contract_validity"],
        "说理原文court_hold_text" : value_range["字符串string_format"],
    },
    "职业放贷人professional_lender":{
        "法院认定court_hold" : value_range["法院对职业放贷人的认定court_recognition_of_professional_lender"],
        "承担举证责任方party_bearing_burden_of_proof" : value_range["承担举证责任方party_bearing_burden_of_proof"],
        "说理原文court_hold_text" : value_range["字符串string_format"],
    },
    "互联网平台责任internet_platform_responsibility":{
        "法院认定court_hold" : value_range["是否yes_or_no"],
        "说理原文court_hold_text" : value_range["字符串string_format"],
    },
    "民刑交叉civil_and_criminal_intersection":{
        "法院处理程序court_handle_procedure" : value_range["法院对民事案件的处理程序court_handle_procedure"],
        "说理原文court_hold_text" : value_range["字符串string_format"],
    },
    "利率调整、认定interest_rate_adjust_and_determine":{
        "说理原文court_hold_text" : value_range["字符串string_format"],
    }
}

# 知识图谱架构与取值表
## 案件总体类属性
case_class = {
    "案号case_id" : value_range["字符串string_format"],
    "案件名称case_name" : value_range["字符串string_format"],
    "借款次数情况lending_frequency_type" : value_range["借款次数情况lending_frequency_type"],
    "案件复杂情况case_complexity" : value_range["案件复杂情况case_complexity"],
    "是否存在错判情形wrong_judgment" : value_range["是否yes_or_no"],
    "是否存在判决书笔误clerical_error" : value_range["是否yes_or_no"],
    "案件简要评述brief_case_review" : value_range["字符串string_format"],
    "结案日期case_closure_date" : value_range["日期值date_format"],                      # 非表必需
    "专题问题special_issue" : special_issue
}

#####################################################（Role）####################################################
court_class = {
    "姓名名称name" : value_range["字符串string_format"],                  # 非表必需
    "位置location" : value_range["字符串string_format"],                      # 非表必需
    "审判长presiding_judge" : value_range["字符串string_format"],                    # 非表必需
    "书记员clerk" : value_range["字符串string_format"],                    # 非表必需
    "人民陪审员people_assessor" : value_range["字符串列表string_list_format"]              # 非表必需
}

agent_role_class = {
    "姓名名称name" : value_range["字符串string_format"],
    "出庭情况attendance_at_court_hearing" : value_range["是否yes_or_no"],
    "角色类型agent_role" : value_range["代理人员角色类型agent_role"],
    "所属机构work_unit" : value_range["字符串string_format"],                     # 非表必需
}

case_role_class = {
    "姓名名称name": value_range["字符串string_format"],
    "借贷关系角色lending_relationship_role" : value_range["借贷关系角色lending_relationship_role"],
    "同类角色序号same_case_role_id" : value_range["数值numerical_format"],
    "代理人agent" : [agent_role_class]
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
date_class = {
    "日期数值date":value_range["日期值date_format"],
    "起始日期或截止日期start_or_end_date" : ["起始日期start_date", "截止日期end_date"],    ##lxb##是不是少了value_range[]?
    "日期类型date_type" : [ value_range["起始日期类型start_date_type"], value_range["截止日期类型end_date_type"]],
}

# 利息率类
interest_rate_class = {
    "数值rate_numerical" : value_range["率数值rate_numerical_format"],
    "类型interest_type" : value_range["利率类型interest_type"]
}

# 需返回利息
required_interest_class = {
    "是否属于逾期利息类型overdue_interest" : value_range["是否yes_or_no"],
    "总额total_amounts" : value_range["金额amounts"],
    "计算起始日期start_date_of_calculation" : [date_class],
    "计算截止日期end_date_of_calculation" : [date_class],
    "利息率interest_rate" : interest_rate_class
}

# 需返回违约金
required_damages_class = {
    "总额total_amounts" : value_range["金额amounts"],
    "计算起始日期start_date_of_calculation" : [date_class],
    "计算截止日期end_date_of_calculation" : [date_class],
    "违约金类型和数值types_and_amounts_of_liquidated_damages" : interest_rate_class
}

# 担保责任情况类
guarantee_liability_class = {
    "承担保证责任的人或单位名称assuming_guarantee_responsibility_name" : value_range["字符串string_format"],
    "保证责任类型guarantee_responsibility_type" : value_range["担保责任类型guarantee_responsibility_type"]
}

# 债权实现费用类
debt_realization_costs_class = {
    "总额total_amounts": value_range["金额amounts"],
    "类型fee_type": value_range["费用类型fee_type"]
}

# 借款凭证类
voucher_class = {
    "名称name" : value_range["字符串string_format"],
    "类型loan_voucher_type" : value_range["借款凭证类型loan_voucher_type"],
    "出具时间issuance_date" : value_range["日期值date_format"],
    "所载内容voucher_content_text" : value_range["字符串string_format"],         # 只有原文，没有值
}

# 约定的借款金额类
agreed_lend_money_class = {
    "约定情况agreed_form" : value_range["约定情况agreed_form"],
    "实际发生时间occurrence_date" : value_range["日期值date_format"],
    "金额amounts" : value_range["金额amounts"]
}
# 约定的还款日期或借款期限
agreed_return_data_class = {
    "约定情况agreed_form" : value_range["约定情况agreed_form"],
    "实际发生时间occurrence_date" : value_range["日期值date_format"],
    "借款起始日期loan_start_date" : value_range["日期值date_format"],
    "还款日期repayment_date" : value_range["日期值date_format"],
    "借款期限（月）loan_term_month": value_range["数值numerical_format"],      # 以月为计数单位
}

# 约定的利息
agreed_interest_class = {
    "是否属于逾期利息类型overdue_interest" : value_range["是否yes_or_no"],
    "约定情况agreed_form" : value_range["约定情况agreed_form"],
    "实际发生时间occurrence_date" : value_range["日期值date_format"],
    "约定的利率agreed_interest" : interest_rate_class
}

# 约定的违约金
agreed_damages_class = {
    "约定情况agreed_form" : value_range["约定情况agreed_form"],
    "实际发生时间occurrence_date" : value_range["日期值date_format"],
    "约定的违约金类型和数值agreed_types_and_amounts_of_liquidated_damages" : interest_rate_class
}

# 程序性费用的承担（律师费、诉讼费等）约定
agreed_procedure_cost_class = {
    "约定情况agreed_form" : value_range["约定情况agreed_form"],
    "约定程序性费用承担情况类型agreement_on_procedural_fee_burden_type" : value_range["约定程序性费用承担情况类型agreement_on_procedural_fee_burden_type"],
}

# 约定的还款方式
agreed_return_methods_class = {
    "约定情况agreed_form" : value_range["约定情况agreed_form"],
    "实际发生时间occurrence_date" : value_range["日期值date_format"],
    "本金还款方式principal_repayment_type" : value_range["约定还款方式类型agreed_repayment_type"],
    "利息还款方式interest_repayment_type" : value_range["约定还款方式类型agreed_repayment_type"],
    "前述还款方式下每次还款总金额amount_per_repayment": value_range["金额amounts"],      # 以月为计数单位
    "前述还款方式下每次还款日期repayment_date_each_time": value_range["日期值date_format"],      # 以月为计数单位
}

# 约定的担保
agreed_guarantee_class = {
    "约定情况agreed_form" : value_range["约定情况agreed_form"],
    "实际发生时间occurrence_date" : value_range["日期值date_format"],
    "担保方式类型guarantee_method_type" : value_range["担保方式类型guarantee_method_type"],
    "担保范围guarantee_scope" : value_range["字符串string_format"],                 # 原文
    "担保期限（月）guarantee_term_month": value_range["金额amounts"],              # 以月为计数单位
    "担保物当下状态collateral_current_condition": value_range["字符串string_format"],                 # 原文
    "担保人类型suretyship_type": value_range["担保人类型suretyship_type"],
    "保证责任类型guarantee_responsibility_type": value_range["担保责任类型guarantee_responsibility_type"],
}

# 借款实际交付类
agreed_guarantee_class = {   ##lxb##这个应该是loan_actual_delivery_class?
    "金额amounts" : value_range["金额amounts"],
    "时间occurrence_date" : value_range["日期值date_format"],
    "交付方式类型delivery_type" : value_range["交付方式类型delivery_type"],
    "对应的是第几笔借款corresponding_loan_sequence_number" : value_range["数值numerical_format"],
}

# 已还款类
repaid_class = {
    "时间occurrence_date" : value_range["日期值date_format"],
    "金额amounts" : value_range["金额amounts"],
    "方式delivery_typ" : value_range["交付方式类型delivery_type"],
    "金额性质amounts_type" : value_range["金额性质amounts_type"],
    "对应的是第几笔借款corresponding_loan_sequence_number" : value_range["数值numerical_format"],
    "已还款金额所冲抵利息至哪一日interest_offset_by_repaid_amount_up_to_which_day" : value_range["日期值date_format"],
}

Thing_class = {
    "date_class" : date_class,

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

    "agreed_guarantee_class" : agreed_guarantee_class, ##lxb##这个应该是"loan_actual_delivery_class" : loan_actual_delivery_class

    "repaid_class" : repaid_class
}


####################################################（Event）###########################################
# 有两种类型的取值：
#   （1）来自value_range字典的取值，修改自数据集采集规范
#   （2）来自Thing_class字典取值，对一些专属概念进行了类封装以复用，类中取值依旧来自value_range字典
# 诉讼请求类
request_class = {
    "是否变更诉讼请求amend_litigation_request" : value_range["是否yes_or_no"],
    "需返回本金总额total_principal_to_be_returned" : value_range["金额amounts"],
    "需返回利息total_interest_to_be_returned" : [Thing_class["required_interest_class"]],
    "需返回逾期利息total_overdue_interest_to_be_returned" : [Thing_class["required_interest_class"]],
    "需返回违约金total_liquidated_damages_to_be_returned" : [Thing_class["required_damages_class"]],
    "是否要求承担担保责任assume_guarantee_responsibility" :[Thing_class["guarantee_liability_class"]],     # 为空则不要求，否则列表形式
    "需返回债权实现费用（起诉前）debt_realization_costs_before_filing_suit" : Thing_class["debt_realization_costs_class"],
    "需返回债权实现费用（起诉后）debt_realization_costs_after_filing_suit" : Thing_class["debt_realization_costs_class"]
}

# 借款事件类
borrow_class = {
    # 借款事实
    "借款目的与用途loan_purposes" : value_range["借款用途loan_purposes_type"],
    "借款人与出借人关系类型borrower_and_lender_relationship_type" : value_range["借款人与出借人关系类型borrower_and_lender_relationship_type"],
    "担保人的姓名或单位名称assuming_guarantee_responsibility_name" : value_range["字符串string_format"],
    "借款人与担保人关系类型borrower_and_guarantor_relationship_type" : value_range["借款人与出借人关系类型borrower_and_lender_relationship_type"],
    "意思表示日will_declaration_date" : value_range["日期值date_format"],
    "借款次数lending_frequency_number" : value_range["数值numerical_format"],
    "借款次数情况lending_frequency_type" : value_range["借款次数情况lending_frequency_type"],
    "是否有借款凭证loan_voucher" : [Thing_class["voucher_class"]],
    # 约定事实
    "约定的借款金额agreed_lend_money" : [Thing_class["agreed_lend_money_class"]],
    "约定的还款日期或借款期限agreed_return_data_or_term" : [Thing_class["agreed_return_data_class"]],
    "约定的利息agreed_interest" : [Thing_class["agreed_interest_class"]],
    "约定的逾期利息agreed_overdue_interest" : [Thing_class["agreed_interest_class"]],
    "约定的违约金agreed_liquidated_damages" : [Thing_class["agreed_damages_class"]],
    "管辖约定情况agreed_jurisdiction" : value_range["约定情况agreed_form"],
    "仲裁约定情况agreed_arbitration" : value_range["约定情况agreed_form"],
    "程序性费用的承担（律师费、诉讼费等）约定agreed_procedure_cost" : Thing_class["agreed_procedure_cost_class"],
    "约定的还款方式agreed_repayment" : [Thing_class["agreed_return_methods_class"]],
    "约定的担保agreed_guarantee" : [Thing_class["agreed_guarantee_class"]],
    # 交付与还款事实
    "借款实际交付loan_actual_delivery" : [Thing_class["agreed_guarantee_class"]],  ##lxb##应该是"loan_actual_delivery_class"
    "已还款总体情况类型repayment_type" : value_range["已还款总体情况类型repayment_type"],
    "已还款repaid" : [Thing_class["repaid_class"]],
}