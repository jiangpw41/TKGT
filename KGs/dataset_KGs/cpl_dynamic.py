from cpl_value_range import value_range, Thing_class


__all__=["cpl_kg_schema"]


# Row_Name角色类型：-1为任意（可以0和多个），0表示至少一个，>0为准确数
Court_determination_attributes = {
    "姓名名称" : value_range["字符串"],
    # 诉讼请求：围绕原告诉讼请求，被告可能辩称，法院则可能驳回、支持等
    "诉讼请求":{
        "是否变更诉讼请求" : value_range["是否"],
        "需返回本金总额" : value_range["金额"],
        "需返回利息" : [Thing_class["required_interest_class"]],
        "需返回逾期利息" : [Thing_class["required_interest_class"]],
        "需返回违约金" : [Thing_class["required_damages_class"]],
        "是否要求承担担保责任" :[Thing_class["guarantee_liability_class"]],     # 为空则不要求，否则列表形式
        "需返回债权实现费用（起诉前）" : Thing_class["debt_realization_costs_class"],
        "需返回债权实现费用（起诉后）" : Thing_class["debt_realization_costs_class"],
    },
    # 借款事件：含各方对借款事实信息、约定事实信息、交付与还款事实信息的陈述
    "借贷事件":{
            # 借款事实信息
        "借贷信息":{
            "借款目的与用途" : value_range["借款用途"],
            "借款人与出借人关系类型" : value_range["借款人与出借人关系类型"],
            "担保人的姓名或单位名称" : value_range["字符串"],
            "借款人与担保人关系类型" : value_range["借款人与出借人关系类型"],
            "意思表示日" : value_range["日期值"],
            "借款次数" : value_range["数值"],
            "借款次数情况" : value_range["借款次数情况"],
            "是否有借款凭证" : [Thing_class["voucher_class"]],
        },
            # 约定事实信息
        "约定信息":{
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
        },
            # 交付与还款事实信息
        "还款信息":{
            "借款实际交付" : [Thing_class["actual_delivery_class"]],
            "已还款总体情况类型" : value_range["已还款总体情况类型"],
            "已还款" : [Thing_class["repaid_class"]],
        }
    },
    # 专题问题：案件文本中关于特殊问题的部分
    "专题问题":{
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

Plaintiff_claim_attributes = {
    "姓名名称" : value_range["字符串"],
    # 诉讼请求：围绕原告诉讼请求，被告可能辩称，法院则可能驳回、支持等
    "诉讼请求":{
        "是否变更诉讼请求" : value_range["是否"],
        "需返回本金总额" : value_range["金额"],
        "需返回利息" : [Thing_class["required_interest_class"]],
        "需返回逾期利息" : [Thing_class["required_interest_class"]],
        "需返回违约金" : [Thing_class["required_damages_class"]],
        "是否要求承担担保责任" :[Thing_class["guarantee_liability_class"]],     # 为空则不要求，否则列表形式
        "需返回债权实现费用（起诉前）" : Thing_class["debt_realization_costs_class"],
        "需返回债权实现费用（起诉后）" : Thing_class["debt_realization_costs_class"],
    },
    # 借款事件：含各方对借款事实信息、约定事实信息、交付与还款事实信息的陈述
    "借贷事件":{
            # 借款事实信息
        "借贷信息":{
            "借款目的与用途" : value_range["借款用途"],
            "借款人与出借人关系类型" : value_range["借款人与出借人关系类型"],
            "担保人的姓名或单位名称" : value_range["字符串"],
            "借款人与担保人关系类型" : value_range["借款人与出借人关系类型"],
            "意思表示日" : value_range["日期值"],
            "借款次数" : value_range["数值"],
            "借款次数情况" : value_range["借款次数情况"],
            "是否有借款凭证" : [Thing_class["voucher_class"]],
        },
            # 约定事实信息
        "约定信息":{
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
        },
            # 交付与还款事实信息
        "还款信息":{
            "借款实际交付" : [Thing_class["actual_delivery_class"]],
            "已还款总体情况类型" : value_range["已还款总体情况类型"],
            "已还款" : [Thing_class["repaid_class"]],
        }
    }
}

Defendant_argue_attributes = {
    "姓名名称" : value_range["字符串"],
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
    "借款实际交付" : [Thing_class["actual_delivery_class"]],
    "已还款总体情况类型" : value_range["已还款总体情况类型"],
    "已还款" : [Thing_class["repaid_class"]],
}


kg_schema = {
    "intro" : "这是一个关于民间借贷案件裁判文书的知识图谱，图中有法院、原告（出借人）、被告（借款人或担保人）三类实体，实体的属性包括各方的基本信息和对案件事实的不同视角的称述。其中由原告提起诉讼并陈述，被告可以对任何一点进行抗辩，法庭则需要查明事实并最终裁决。",
    "entity_type" : "multi_entity",        # "single_entity", or "multi_entity"
    "event_type" : "dynamic",        # 完全静态如E2E和Rotowire的属性"static", 属性类化可多次可迭代成整体的"dynamic"
    "entity":{
        "法院":{
            "number": (1,1),
            "intro" : "法院",
            "predicate" : "判定",
            "attributes" : Court_determination_attributes
        },
        "出借人（原告）":{
            "number": (1,5),
            "intro" : "Plaintiff",
            "predicate" : "诉称",
            "attributes": Plaintiff_claim_attributes
        },
        "借款人（被告）":{
            "number": (1,8),
            "intro" : "Defendant被告（借款人、担保人）",
            "predicate" : "辩称",
            "attributes" : Defendant_argue_attributes
        },
    },
    "relation":{                    # 仅仅记录需要被采集的关系
        "Plaintiff_and_Defendant":{
            "BorrowingAndOwing":{
                "number": (1,1),        # 单次单笔借款
                "intro" : "原告是出借人，被告是借款人、担保人以及其他相关人员"      # 有向
            },
        }
    }
}


