# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 19:22:51 2019

@author: weiqing.xwq
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 16:52:28 2019

@author: weiqing.xwq
"""
import codecs

text = codecs.open('C:/Users/weiqing.xwq/Desktop/xhb.txt', 'r', 'gbk').read()

from textrank4zh import TextRank4Keyword, TextRank4Sentence
import jieba
import logging

# 取消jieba 的日志输出
jieba.setLogLevel(logging.INFO)


def get_key_words(text, num=2):
    """提取关键词"""
    tr4w = TextRank4Keyword(stop_words_file='C:/Users/weiqing.xwq/Desktop/TextRank4ZH-master/textrank4zh/stopwords.txt')
    tr4w.analyze(text, lower=2)
    key_words = tr4w.get_keywords(num)
    return [item.word for item in key_words]

def get_summary(text, num=2):
    """提取摘要"""
    tr4s = TextRank4Sentence(stop_words_file='C:/Users/weiqing.xwq/Desktop/TextRank4ZH-master/textrank4zh/stopwords.txt')
    tr4s.analyze(text=text, lower=2, source='no_stop_words')
    return [item.sentence for item in tr4s.get_key_sentences(num)]

import jieba.analyse

# 基于 TF-IDF 算法的关键词抽取
tags = jieba.analyse.extract_tags(text, topK=8)
print('基于TF-IDF算法的关键词抽取')
print(",".join(tags))


# 基于 TextRank 算法的关键词抽取
tags = jieba.analyse.textrank(text, topK=8)
print('基于TextRank算法的关键词抽取')
print(",".join(tags))


from snownlp import SnowNLP

s = SnowNLP(text)
print('基于SnowNLP算法的关键词抽取')
print(s.keywords(8))

# TextRank算法
print('基于TextRank算法的摘要抽取')
print(s.summary(5))
