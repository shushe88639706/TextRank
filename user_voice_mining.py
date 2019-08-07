# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 16:52:28 2019

@author: weiqing.xwq
"""
import datetime
import wordfind_func as func

print('********开始********')
starttime = datetime.datetime.now()
print(starttime)
cut_all = True #切词方式
file_current = u'kk.txt'   #测试文本
file_base = u'gs.txt'   #测试文本
stopwords_file=u'stopwords.txt'
#stopwords_file='C:/Users/weiqing.xwq/Desktop/stop.txt'
pre_word_embeddings_vec=u'D:/sgns.weibo.char'

#文本分词处理
corpus_current=func.corpus_file(file_current,stopwords_file,cut_all)
corpus_base=func.corpus_file(file_base,stopwords_file,cut_all)

#模型训练
vec_num=300  #向量空间维度
min_count=2 #最短词频
model_current,model_txt_current,vocab_txt_current=func.model(vec_num,corpus_current,min_count)
model_base,model_txt_base,vocab_txt_base=func.model(vec_num,corpus_base,min_count)

#句子处理
newsplit_current = func.newsplit_func(file_current)
newsplit_base = func.newsplit_func(file_base)
stop_words = func.stopwordslist(stopwords_file)  # 这里加载停用词的路径
words_list=func.word_cutstopwords_list(newsplit_current,stop_words,cut_all) 
print(words_list[:5])

#词特征向量
word_vec_path=pre_word_embeddings_vec #预训练词向量
print('预训练词向量结果')
#word_vec_path=model_txt_current #模型现训练词向量
#print('模型现训练词向量结果')
word_embeddings=func.word_embeddings_fun(word_vec_path)
print("词表特征词一共有"+str(len(word_embeddings))+"个词语/字。") 

#词相似度计算
#role1 = ['相互']
word_cnt_list_path=model_txt_current
word_cnt_list=func.word_embeddings_fun(word_cnt_list_path)
print("特征词一共有"+str(len(word_cnt_list))+"个词语/字。") 
role1 = list(word_cnt_list.keys())[:2]  #前50词相关性     
print("源词为："+str(role1))
role2 = list(word_cnt_list.keys())[:2]  #前50词相关性 
#生成词相似度矩阵文本      
func.similarity_word(role1,role2,model_current)
  
#句子向量
sentence_vectors=func.sentence_vec(words_list,word_embeddings,vec_num)
#句子相似度特征处理
sim_mat=func.similarity_sentence(newsplit_current,sentence_vectors,vec_num)
#句子相似度计算
ranked_sentences=func.ranked_sentences_func(sim_mat,newsplit_current)
#sim_mat.shape

#关键词
keywords_num=40
print("取出词频最高的前"+str(keywords_num)+"个词：")
print_words = open(vocab_txt_current, encoding='utf-8').read().split('\n')
print("关键词：\n"+str(print_words[:keywords_num]))

#热词词云
wordcloud_file=corpus_current
#func.print_wordcloud(wordcloud_file)

# 取出得分最高的前10个句子作为摘要
num = 15
print("取出得分最高的前"+str(num)+"个句子作为摘要：")
for i in range(num):
    print("第"+str(i+1)+"条摘要：",ranked_sentences[i][1])
    #ranked_sentences[1][1]

#新增消失等热词监控
cnt_carrent_sum=len(newsplit_current)
cnt_base_sum=len(newsplit_base)
d_new_cnt=30  #新增词排行
d_lost_cnt=30 #消失词排行
new_word_cnt_min=5 #新增词限定最小词频
lost_word_cnt_min=10 #消失词限定最小词频
base_word_cnt=3 #基准词频量
d_new,d_lost,d_add,d_se=func.wordfind(vocab_txt_current,vocab_txt_base,cnt_carrent_sum,cnt_base_sum,new_word_cnt_min,lost_word_cnt_min,d_new_cnt,d_lost_cnt,base_word_cnt)
#生成新增词-消失词文本摘要，发现新问题
print('\n新问题：')
word_list_new=d_new.word.values
new_word_tosentence_new=func.new_word_tosentence(word_list_new,ranked_sentences,stop_words,cut_all)
print('\n消失的问题：')
word_list_lost=d_lost.word.values
new_word_tosentence_new=func.new_word_tosentence(word_list_lost,ranked_sentences,stop_words,cut_all)
print('\n权重增加的问题：')
word_list_add=d_add.word.values
new_word_tosentence_new=func.new_word_tosentence(word_list_add,ranked_sentences,stop_words,cut_all)
print('\n权重降低的问题：')
word_list_se=d_se.word.values
new_word_tosentence_new=func.new_word_tosentence(word_list_se,ranked_sentences,stop_words,cut_all)

#句子聚类，与知识点比较，发现新知识
#用肘部法则(轮廓系数)来确定最佳的K值
k_min=5
k_max=30
func.kmeans_to_find_k(sim_mat,k_min,k_max)
n_clusters=14
#结合平均畸变程度(与轮廓系数)使用类别数量4较合适
import pandas as pd
from sklearn.cluster import KMeans
clf=KMeans(n_clusters)
clf.fit(sim_mat)
y_pred = clf.fit_predict(sim_mat)
data = {u'句子': newsplit_current,u'分类':y_pred}
newsplit_current_style = pd.DataFrame(data)
print(newsplit_current_style[:300].sort_values(by=[u'分类']))
            
print('********结束********')    
endtime = datetime.datetime.now()
print('使用时间：')
print (endtime - starttime)
