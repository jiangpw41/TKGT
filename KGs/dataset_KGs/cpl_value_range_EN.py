# kgs：序号从零开始

value_range = {
    "yes_or_no":["yes", "no"],
    "source_text" : str,
    "lending_relationship_role" : ["lender", "borrower", "guarantor", "others"],
    "lending_frequency_type" : ["single_loan", "undistinguished_multiple_loans", "distinguished_multiple_loans", "partially_distinguished_multiple_loans", "rollover_of_loan_with_interest_capitalized"],  ##lxb##和第122行重复了
    "case_complexity" : ["ordinary", "complex"],   ##lxb##删除此行，保留第134行
    "agent_role" : ["authorized_agent", "legal_representative"],
    "string_list_format" : [str],
    "numerical_format" : int,       # 从0开始
    "string_format" : str,
    "date_format" : str,       # 待定义
    "amounts_type": [
        "principal;",
        "interest;",
        "overdue_interest;",
        "liquidated_damages"
    ],
    "start_date_type": [
        "loan_agreement_establishment_date",
        "loan_actual_delivery_date",
        "interest_offset_date",
        "filing_suit_date",
        "loan_agreement_establishment_date_and_loan_actual_delivery_date",
        "interest_free_loan_maturity_date",
        "court_determined_payment_date",
        "case_filing_date",
        "installment_payments_date",
        "reconfirm_creditor_debtor_relationship_date"
    ],
    "end_date_type": [
        "stipulated_date_for_the_payment_of_principal_and_interest",
        "filing_suit_date",
        "actual_date_of_full_performance",
        "temporarily_calculated_date",
        "complaint_served_date",
        "court_determined_payment_date"
    ],
    "amounts" : int,       #（元）
    "interest_type": [
        "annual_interest_rate",
        "annual_interest_amount",
        "monthly_interest_rate",
        "monthly_interest_amount",
        "daily_interest_rate",
        "daily_interest_amount",
        "pbc_lpr",
        "lpr",
        "pbc_lpr_4x",
        "lpr_4x",
        "limits_of_national_regulations_or_judicial_protection",
        "proportion_of_loan_amount",
        "agreed_or_fixed_amount",
        "annual_fixed_dividend",
        "monthly_fixed_dividend",
        "daily_fixed_dividend"
    ],
    "rate_numerical_format": str,          #"率类型": "1=年利率，是指借贷双方直接约定每年需支付的利息率，如“每年按照借款的24%支付利率”、“每年按照借款的0.24支付利率”，输入“24%”;\n2=年利息，是指借贷双方直接约定每年需支付的利息总额，如“每年支付利息2000元”、“每年支付利息2千元”，输入“2000”;\n3=月利率，是指借贷双方直接约定每月需支付的利息率，如“每月按照借款的2%支付利率”、“每月按照借款的0.02支付利率”、“两分利”，输入“2%”;\n4=月利息，是指借贷双方直接约定每年需支付的利息总额，如“每月支付利息200元”、“每月支付利息两百元”，输入“200”;\n5=日利率，是指借贷双方直接约定每月需支付的利息率，如“每日按照借款的0.2%支付利率”、“每日按照借款的千分之二支付利率”，输入“0.2%”;\n6=日利息，是指借贷双方直接约定每日需支付的利息总额，如“每日支付利息1000元”、“每日支付利息一千元”，输入“1000”;"
    "guarantee_responsibility_type": [
        "joint_liability",
        "general_liability",
        "secured_auction_collateral"
    ],
    "fee_type": [
        "collection_fee",
        "travel_fee",
        "attorney_fee",
        "preservation_fee"
    ],
    "loan_purposes_type": [
        "business",
        "consumer",
        "right_assignment",
        "debt_assignment",
        "capital_turnover",
        "purchase_house_car_renovation",
        "loan_for_others",
        "investment",
        "others"
    ],
    "borrower_and_lender_relationship_type": [
        "relatives",
        "friends",
        "colleagues",
        "introduced_by_relatives",
        "introduced_by_friends",
        "introduced_by_colleagues",
        "matched_by_third_party_platform",
        "house_rental_relationship",
        "fellow_villagers",
        "neighbors"
    ],
    "loan_voucher_type": [
        "iou_jietiao",
        "debt_acknowledgement_qiantiao",
        "loan_contract",
        "oral",
        "receipt_shoutiao",
        "consulting_service_agreement",
        "debt_confirmation_memorandum",
        "partnership_agreement"
    ],
    "delivery_type": [
        "bank_transfer",
        "cash_payment",
        "wechat_alipay_electronic_transfer",
        "credit_card_payment_on_behalf",
        "transfer_zhuanzhang",
        "remittance_dakuan",
        "direct_delivery_to_third_party",
        "delivery_through_third_party",
        "delivery_from_third_party_to_fourth_party",
        "delivery_with_interest_included_in_principal"
    ],
    "agreement_on_procedural_fee_burden_type": [
        "lender_bear",
        "borrower_bear",
        "jointly_bear",
        "defaulting_party_bear"
    ],
    "lending_frequency_type": [ ##lxb##和第8行重复了
        "single_loan",
        "undistinguished_multiple_loans",
        "distinguished_multiple_loans",
        "partially_distinguished_multiple_loans",
        "rollover_of_loan_with_interest_capitalized"
    ],
    "agreed_form": [
        "oral_agreement",
        "written_agreement",
        "unspecified_agreement"
    ],
    "case_complexity": [  ##lxb##和第7行重复了
        "ordinary",
        "complex",
        "p2p",
        "nominal_shares_with_actual_debt"  ##lxb##中文是"名股实债"
    ],
    "before_or_after_filing": [
        "before_filing_suit",
        "after_filing_suit"
    ],
    "agreed_repayment_type": [
        "equal_monthly_repayment",
        "equal_annual_repayment",
        "equal_semi_annual_repayment",
        "equal_quarterly_repayment",
        "lump_sum_repayment_at_maturity",
        "initial_onetime_deduction_kantouxi",
        "monthly_repayment",
        "annual_repayment",
        "semi_annual_repayment",
        "quarterly_repayment"
    ],
    "repayment_type": [
        "principal_fully_unreturned_of_interest_free_loan",
        "principal_partially_unreturned_of_interest_free_loan",
        "principal_fully_returned_and_interest_fully_returned",
        "principal_fully_returned_and_interest_partially_returned",
        "principal_fully_returned_and_interest_fully_unreturned",
        "principal_partially_returned_and_interest_fully_returned",
        "principal_partially_returned_and_interest_partially_returned",
        "principal_partially_returned_and_interest_fully_unreturned",
        "principal_fully_unreturned_and_interest_fully_returned",
        "principal_fully_unreturned_and_interest_partially_returned",
        "principal_fully_unreturned_and_interest_fully_unreturned"
    ],
    "已还款金额性质amounts_type": [  ##lxb##"已还款金额性质"和"金额性质"一致，是否删去"已还款金额性质"?后续也没有用到"已还款金额性质"
        "principal;",
        "interest;",
        "overdue_interest;",
        "liquidated_damages"
    ],
    "guarantee_method_type": [
        "mortgage",
        "pledge",
        "suretyship"
    ],
    "suretyship_type": [
        "personal",
        "general_corporate",
        "guarantee_company"
    ],
    "court_recognition_of_marital_debt": [
        "yes",
        "no"
    ],
    "court_recognition_of_clipping_interest": [
        "yes",
        "no"
    ],
    "court_recognition_of_guarantee_effectiveness_for_shareholders_by_company": [
        "yes",
        "no"
    ],
    "creditor_right_acquisition_type": [
        "right_assignment",
        "debt_assignment"
    ],
    "court_recognition_of_subject_qualification_and_contract_validity": [
        "subject_qualification_renders_contract_invalid",
        "subject_qualification_defective_but_contract_valid",
        "subject_qualification_without_defect"
    ],
    "court_recognition_of_professional_lender": [
        "yes",
        "no"
    ],
    "party_bearing_burden_of_proof": [
        "borrower",
        "lender",
        "guarantor",
        "court"
    ],
    "court_handle_procedure": [
        "continue_hearing",
        "suspend_litigation",
        "reject_lawsuit"
    ],
} 


special_issue = {
    "marital_debt" : {
        "court_hold" : value_range["court_recognition_of_marital_debt"],
        "court_hold_text":  value_range["string_format"],
    },
    "clipping_interest" : {
        "court_hold" : value_range["court_recognition_of_clipping_interest"],
        "court_hold_text":  value_range["string_format"],
    },
    "company_guarantee_for_shareholder" : {
        "court_hold" : value_range["court_recognition_of_guarantee_effectiveness_for_shareholders_by_company"],
        "court_hold_text":  value_range["string_format"],
    },
    "creditor_debtor_rights_acquisition" : {
        "creditor_right_acquisition_type" : value_range["creditor_right_acquisition_type"],  ##lxb##此处应该是"债权取得类型",原来是"券""法院对夫妻债务的认定"
        "transferor_name" : value_range["string_format"],
        "transferee_name" : value_range["string_format"],
    },
   "lender_subject_qualification":{
        "court_hold" : value_range["court_recognition_of_subject_qualification_and_contract_validity"],
        "court_hold_text" : value_range["string_format"],
    },
    "professional_lender":{
        "court_hold" : value_range["court_recognition_of_professional_lender"],
        "party_bearing_burden_of_proof" : value_range["party_bearing_burden_of_proof"],
        "court_hold_text" : value_range["string_format"],
    },
    "internet_platform_responsibility":{
        "court_hold" : value_range["yes_or_no"],
        "court_hold_text" : value_range["string_format"],
    },
    "civil_and_criminal_intersection":{
        "court_handle_procedure" : value_range["court_handle_procedure"],
        "court_hold_text" : value_range["string_format"],
    },
    "interest_rate_adjust_and_determine":{
        "court_hold_text" : value_range["string_format"],
    }
}

# 知识图谱架构与取值表
## 案件总体类属性
case_class = {
    "case_id" : value_range["string_format"],
    "case_name" : value_range["string_format"],
    "lending_frequency_type" : value_range["lending_frequency_type"],
    "case_complexity" : value_range["case_complexity"],
    "wrong_judgment" : value_range["yes_or_no"],
    "clerical_error" : value_range["yes_or_no"],
    "brief_case_review" : value_range["string_format"],
    "case_closure_date" : value_range["date_format"],                      # 非表必需
    "special_issue" : special_issue
}

#####################################################（Role）####################################################
court_class = {
    "name" : value_range["string_format"],                  # 非表必需
    "location" : value_range["string_format"],                      # 非表必需
    "presiding_judge" : value_range["string_format"],                    # 非表必需
    "clerk" : value_range["string_format"],                    # 非表必需
    "people_assessor" : value_range["string_list_format"]              # 非表必需
}

agent_role_class = {
    "name" : value_range["string_format"],
    "attendance_at_court_hearing" : value_range["yes_or_no"],
    "agent_role" : value_range["agent_role"],
    "work_unit" : value_range["string_format"],                     # 非表必需
}

case_role_class = {
    "name": value_range["string_format"],
    "lending_relationship_role" : value_range["lending_relationship_role"],
    "same_case_role_id" : value_range["numerical_format"],
    "agent" : [agent_role_class]
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
    "date":value_range["date_format"],
    "start_or_end_date" : ["start_date", "end_date"],    ##lxb##是不是少了value_range[]?
    "date_type" : [ value_range["start_date_type"], value_range["end_date_type"]],
}

# 利息率类
interest_rate_class = {
    "rate_numerical" : value_range["rate_numerical_format"],
    "interest_type" : value_range["interest_type"]
}

# 需返回利息
required_interest_class = {
    "overdue_interest" : value_range["yes_or_no"],
    "total_amounts" : value_range["amounts"],
    "start_date_of_calculation" : [date_class],
    "end_date_of_calculation" : [date_class],
    "interest_rate" : interest_rate_class
}

# 需返回违约金
required_damages_class = {
    "total_amounts" : value_range["amounts"],
    "start_date_of_calculation" : [date_class],
    "end_date_of_calculation" : [date_class],
    "types_and_amounts_of_liquidated_damages" : interest_rate_class
}

# 担保责任情况类
guarantee_liability_class = {
    "assuming_guarantee_responsibility_name" : value_range["string_format"],
    "guarantee_responsibility_type" : value_range["guarantee_responsibility_type"]
}

# 债权实现费用类
debt_realization_costs_class = {
    "total_amounts": value_range["amounts"],
    "fee_type": value_range["fee_type"]
}

# 借款凭证类
voucher_class = {
    "name" : value_range["string_format"],
    "loan_voucher_type" : value_range["loan_voucher_type"],
    "issuance_date" : value_range["date_format"],
    "voucher_content_text" : value_range["string_format"],         # 只有原文，没有值
}

# 约定的借款金额类
agreed_lend_money_class = {
    "agreed_form" : value_range["agreed_form"],
    "occurrence_date" : value_range["date_format"],
    "amounts" : value_range["amounts"]
}
# 约定的还款日期或借款期限
agreed_return_data_class = {     ##lxb## "date"?
    "agreed_form" : value_range["agreed_form"],
    "occurrence_date" : value_range["date_format"],
    "loan_start_date" : value_range["date_format"],
    "repayment_date" : value_range["date_format"],
    "loan_term_month": value_range["numerical_format"],      # 以月为计数单位
}

# 约定的利息
agreed_interest_class = {
    "overdue_interest" : value_range["yes_or_no"],
    "agreed_form" : value_range["agreed_form"],
    "occurrence_date" : value_range["date_format"],
    "agreed_interest" : interest_rate_class
}

# 约定的违约金
agreed_damages_class = {
    "agreed_form" : value_range["agreed_form"],
    "occurrence_date" : value_range["date_format"],
    "agreed_types_and_amounts_of_liquidated_damages" : interest_rate_class
}

# 程序性费用的承担（律师费、诉讼费等）约定
agreed_procedure_cost_class = {
    "agreed_form" : value_range["agreed_form"],
    "agreement_on_procedural_fee_burden_type" : value_range["agreement_on_procedural_fee_burden_type"],
}

# 约定的还款方式
agreed_return_methods_class = {
    "agreed_form" : value_range["agreed_form"],
    "occurrence_date" : value_range["date_format"],
    "principal_repayment_type" : value_range["agreed_repayment_type"],
    "interest_repayment_type" : value_range["agreed_repayment_type"],
    "amount_per_repayment": value_range["amounts"],      # 以月为计数单位   ##lxb##为什么是"以月为计数单位"?
    "repayment_date_each_time": value_range["date_format"],      # 以月为计数单位   ##lxb##为什么是"以月为计数单位"?
}

# 约定的担保
agreed_guarantee_class = {
    "agreed_form" : value_range["agreed_form"],
    "occurrence_date" : value_range["date_format"],
    "guarantee_method_type" : value_range["guarantee_method_type"],
    "guarantee_scope" : value_range["string_format"],                 # 原文
    "guarantee_term_month": value_range["amounts"],              # 以月为计数单位   ##lxb##value_range["金额amounts"]会不会有歧义，尽管取值都是int
    "collateral_current_condition": value_range["string_format"],                 # 原文
    "suretyship_type": value_range["suretyship_type"],
    "guarantee_responsibility_type": value_range["guarantee_responsibility_type"],
}

# 借款实际交付类
agreed_guarantee_class = {   ##lxb##这个应该是loan_actual_delivery_class?
    "amounts" : value_range["amounts"],
    "occurrence_date" : value_range["date_format"],
    "delivery_type" : value_range["delivery_type"],
    "corresponding_loan_sequence_number" : value_range["numerical_format"],
}

# 已还款类
repaid_class = {
    "occurrence_date" : value_range["date_format"],
    "amounts" : value_range["amounts"],
    "delivery_typ" : value_range["delivery_type"],
    "amounts_type" : value_range["amounts_type"],
    "corresponding_loan_sequence_number" : value_range["numerical_format"],
    "interest_offset_by_repaid_amount_up_to_which_day" : value_range["date_format"],
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
    "amend_litigation_request" : value_range["yes_or_no"],
    "total_principal_to_be_returned" : value_range["amounts"],
    "total_interest_to_be_returned" : [Thing_class["required_interest_class"]],
    "total_overdue_interest_to_be_returned" : [Thing_class["required_interest_class"]],
    "total_liquidated_damages_to_be_returned" : [Thing_class["required_damages_class"]],
    "assume_guarantee_responsibility" :[Thing_class["guarantee_liability_class"]],
    "debt_realization_costs_before_filing_suit" : Thing_class["debt_realization_costs_class"],
    "debt_realization_costs_after_filing_suit" : Thing_class["debt_realization_costs_class"]
}

# 借款事件类
borrow_class = {
    # 借款事实
    "loan_purposes" : value_range["loan_purposes_type"],
    "borrower_and_lender_relationship_type" : value_range["borrower_and_lender_relationship_type"],
    "assuming_guarantee_responsibility_name" : value_range["string_format"],
    "borrower_and_guarantor_relationship_type" : value_range["borrower_and_lender_relationship_type"],
    "will_declaration_date" : value_range["date_format"],
    "lending_frequency_number" : value_range["numerical_format"],
    "lending_frequency_type" : value_range["lending_frequency_type"],
    "loan_voucher" : [Thing_class["voucher_class"]],
    # 约定事实
    "agreed_lend_money" : [Thing_class["agreed_lend_money_class"]],
    "agreed_return_date_or_term" : [Thing_class["agreed_return_data_class"]],
    "agreed_interest" : [Thing_class["agreed_interest_class"]],
    "agreed_overdue_interest" : [Thing_class["agreed_interest_class"]],
    "agreed_liquidated_damages" : [Thing_class["agreed_damages_class"]],
    "agreed_jurisdiction" : value_range["agreed_form"],
    "agreed_arbitration" : value_range["agreed_form"],
    "agreed_procedure_cost" : Thing_class["agreed_procedure_cost_class"],
    "agreed_repayment" : [Thing_class["agreed_return_methods_class"]],
    "agreed_guarantee" : [Thing_class["agreed_guarantee_class"]],
    # 交付与还款事实
    "loan_actual_delivery" : [Thing_class["agreed_guarantee_class"]],
    "repayment_type" : value_range["repayment_type"],
    "repaid" : [Thing_class["repaid_class"]],
}