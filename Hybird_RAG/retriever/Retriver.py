

def HybirdRAG_for_Context( entity, attr, text, mode):
    if mode=="naive":
        return text
    elif mode=="rule_based":
        