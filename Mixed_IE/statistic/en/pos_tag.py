'''
https://blog.csdn.net/u010626937/article/details/95596478
'''

Universal_POS_tags = {
    "ADJ" : "adjective形容词",
    "ADP" : "adposition介词",
    "ADV" : "adverb副词",
    "AUX" : "auxiliary verb助动词",
    "CONJ" : "coordinating conjunction连词",
    "DET" : "determiner限定词如the, some, my",
    "INTJ" : "interjection感叹词",
    "NOUN" : "noun名词",
    "NUM" : "numeral数字",
    "PART" : "particle小品词，与动词构成短语动词的副词或介词",
    "PRON" : "pronoun代词",
    "PROPN" : "proper noun专有名词",
    "PUNCT" : "punctuation标点",
    "SCONJ" : "subordinating conjunction从属连词",
    "SYM" : "symbol符号",
    "VERB" : "verb动词",
    "X" : "other其他",
}

NLTK_POS_tags = {
    "CC" : "Coordinating conjunction 连接词", 
    "CD" : "Cardinal number 基数词", 
    "DT" : "Determiner 限定词（如this,that,these,those,such)不定限定词：(no,some,any,each,every,enough,either,neither,all,both,half,several,many,much,(a) few,(a) little,other,another.)", 
    "EX" : "Existential there 存在句", 
    "FW" : "Foreign word 外来词", 
    "IN" : "Preposition or subordinating conjunction 介词或从属连词", 
    "JJ" : "Adjective 形容词或序数词", 
    "JJR" : "Adjective, comparative 形容词比较级", 
    "JJS" : "Adjective, superlative 形容词最高级", 
    "LS" : "List item marker 列表标示", 
    "MD" : "Modal 情态助动词", 
    "NN" : "Noun, singular or mass 常用名词 单数形式", 
    "NNS" : "Noun, plural 常用名词 复数形式", 
    "NNP" : "Proper noun, singular 专有名词，单数形式", 
    "NNPS" : "Proper noun, plural 专有名词，复数形式", 
    "PDT" : "Predeterminer 前位限定词", 
    "POS" : "Possessive ending 所有格结束词", 
    "PRP" : "Personal pronoun 人称代词", 
    "PRP$" : "Possessive pronoun 所有格代名词", 
    "RB" : "Adverb 副词", 
    "RBR" : "Adverb, comparative 副词比较级", 
    "RBS" : "Adverb, superlative 副词最高级", 
    "RP" : "Particle 小品词", 
    "SYM" : "Symbol 符号", 
    "TO" : "to 作为介词或不定式格式", 
    "UH" : "Interjection 感叹词", 
    "VB" : "Verb, base form 动词基本形式", 
    "VBD" : "Verb, past tense 动词过去式", 
    "VBG" : "Verb, gerund or present participle 动名词和现在分词", 
    "VBN" : "Verb, past participle 过去分词", 
    "VBP" : "Verb, non-3rd person singular present 动词非第三人称单数", 
    "VBZ" : "Verb, 3rd person singular present 动词第三人称单数", 
    "WDT" : "Wh-determiner 限定词（如关系限定词：whose,which.疑问限定词：what,which,whose.）", 
    "WP" : "Wh-pronoun 代词（who whose which）", 
    "WP$" : "Possessive wh-pronoun 所有格代词", 
    "WRB" : "Wh-adverb 疑问代词（how where when）",
}