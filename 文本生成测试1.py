# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:44:09 2019

@author: weiqing.xwq
"""

import codecs,re
from textrank4zh import TextRank4Keyword, TextRank4Sentence

#text = codecs.open('C:/Users/weiqing.xwq/Desktop/xhb.txt', 'r', 'gbk').read()
text ='\n'.join(re.split('[。！；→？]',codecs.open('C:/Users/weiqing.xwq/Desktop/zw.txt', 'r', 'gbk').read()))
tr4w=TextRank4Keyword(stop_words_file='C:/Users/weiqing.xwq/Desktop/TextRank4ZH-master/textrank4zh/stopwords.txt')
tr4w.analyze(text=text, lower=True, window=3,vertex_source='words_no_stop_words')  # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象

print( '关键词：' )
for item in tr4w.get_keywords(15, word_min_len=2):
    print(item.word, item.weight)

print()
print( '关键短语：' )
for phrase in tr4w.get_keyphrases(keywords_num=100,min_occur_num= 2):
    print(phrase)

tr4s = TextRank4Sentence()
tr4s.analyze(text=text, lower=True, source = 'words_no_stop_words')

print()
print( '摘要：' )
for item in tr4s.get_key_sentences(num=8):
    print(item.index, item.weight, item.sentence)