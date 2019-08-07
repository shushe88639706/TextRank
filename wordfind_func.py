# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 16:42:32 2019

@author: weiqing.xwq
"""
newdict=u'newdict.txt' #自定义词典  
import re    
import jieba,os
jieba.load_userdict(newdict) #加载自定义词典  
import pandas as pd
import numpy as np
import datetime

def wordfind(current_file,base_file,cnt_carrent_sum,cnt_base_sum,new_word_cnt_min=5,lost_word_cnt_min=5,d_new_cnt=30,d_lost_cnt=30,base_word_cnt=2):
    #数据表
    base= base_file
    current= current_file
    #读入
    d_base=pd.read_csv(base,sep=' ',names=['word','cnt'],nrows = 300) #取前300个词
    d_current=pd.read_csv(current,sep=' ',names=['word','cnt'],nrows = 300) #取前300个词
    #增加词频排名列
    d_base['rank']=d_base['cnt'].rank(ascending=False)
    d_current['rank']=d_current['cnt'].rank(ascending=False)
    #单词权重
    d_current['weight']=d_current['cnt']/cnt_carrent_sum
    d_base['weight']=d_base['cnt']/cnt_base_sum
    #合并数据
    a_d=pd.merge(d_current,d_base,how='outer',on='word')
    #重命名
    a_d.rename(index=str, columns={"cnt_x": "cnt_current", "rank_x": "rank_current",'weight_x':'weight_current',"cnt_y": "cnt_base", "rank_y": "rank_base",'weight_y':'weight_base'},inplace=True)
    #排行值na补充为最后一位，如d_qt有100行，补充数为101
    a_d.rank_current=a_d.rank_current.where(a_d.rank_current.notnull(), d_current.shape[0])
    a_d.rank_base=a_d.rank_base.where(a_d.rank_base.notnull(), d_base.shape[0])
    a_d.weight_current=a_d.weight_current.where(a_d.weight_current.notnull(), d_current.shape[0])
    a_d.weight_base=a_d.weight_base.where(a_d.weight_base.notnull(), d_base.shape[0])
    #词频数na补充为0
    a_d=a_d.where(a_d.notnull(), 0)
    #增加排名变化列
    a_d['rc-rb']=a_d.rank_current-a_d.rank_base
    #增加权重变化列
    a_d['wc-wb']=a_d.weight_current-a_d.weight_base
    #取排名变化前50的词（新增词30，消失词20）
    #新增的词
    d_new=a_d[(a_d.cnt_current>new_word_cnt_min)&(a_d.cnt_base<base_word_cnt)].sort_values(by='rc-rb',ascending=True)[:d_new_cnt] 
    #消失的词
    d_lost=a_d[(a_d.cnt_base>lost_word_cnt_min)&(a_d.cnt_current<base_word_cnt)].sort_values(by='rc-rb',ascending=False)[:d_lost_cnt] 
    #权重增加的词
    d_add=a_d[(a_d.rank_current<a_d.rank_base)&(a_d.weight_current>a_d.weight_base)].sort_values(by='wc-wb',ascending=True)[:d_new_cnt] 
    #权重减弱的词
    d_se=a_d[(a_d.rank_current>a_d.rank_base)&(a_d.weight_current<a_d.weight_base)].sort_values(by='wc-wb',ascending=False)[:d_lost_cnt] 
    #data=d_top.append(d_new)
    return d_new,d_lost,d_add,d_se

#词云
def print_wordcloud(wordcloud_file):
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    var = open(wordcloud_file, encoding='utf-8').read().split('\n')
    #print(var)
    wl_space_split = '.'.join(var)
    my_wordcloud = WordCloud(font_path='C:/Windows/Fonts/simsun.ttc',width=12,height=12).generate(wl_space_split)
    plt.figure(figsize=(12,12))
    plt.imshow(my_wordcloud)
    plt.axis("off")
    plt.savefig('词云')
    #plt.show()

# 计算两个词的相似度/相关程度
def similarity_word(word_first,word_last,model):
    pair_dict={}
    pairs = [(x,y) for x in word_first for y in word_last]
    #print(pairs)  #[('相互宝', '分摊'), ('相互宝', '红包')] 
    output = open('pairs.txt','w')
    for pair in pairs:
        pair_dict[(pair[0], pair[1])]=model.similarity(pair[0], pair[1])
        print("> [%s]和[%s]的相似度为：" % (pair[0],pair[1]), model.similarity(pair[0], pair[1]))   # 预测相似性
    for i in pair_dict:
        write_str = str(i) + ' ' + str(pair_dict[i]) + '\n'
        output.write(write_str) 
        #print (i,pair_dict[i])
    output.close() 
 
#停用词表
def stopwordslist(filename):  
    stopwords_list = [line.strip() for line in open(filename, 'r', encoding='utf-8').readlines()]  
    return stopwords_list    

#
def word_cutstopwords_list(line_split,stop_words,cut_all):
    words=[]
    for l in line_split:
        word=jieba.lcut(l,cut_all = cut_all,HMM=True)          
        outstr = []
        for w in word:  
            if w not in stop_words:  
                if w != '\t':  
                    outstr.append( w ) 
        words.append(outstr)
    return words    

#新文本名生成
def corpus_file(filename,stopwords_file,cut_all):
    pre,ext = os.path.splitext(filename)   #输入文件分开前缀，后缀   pre=test_01   ext=.txt
    corpus = pre + '_seg' + ext    #训练语料为按行分词后的文本文件    corpus=test_01_seg.txt
    #fin = open(filename,encoding='gbk').read().strip(' ').strip('\n').replace('\n\n','\n')   #strip()取出首位空格，和换行符，用\n替换\n\n
    stopwords = set(open(stopwords_file,encoding='utf8').read().strip('\n').split('\n'))   #读入停用词
    with open(filename,encoding='gbk') as f:
        with open(corpus, 'w+',encoding="utf-8") as f2:
            for document in f.readlines():
                result = ' '.join([x for x in jieba.lcut(document,cut_all = cut_all,HMM=True) if x not in stopwords and len(x)>1 and len(x)<4 ]) #特征词长度
                f2.write(result)
                f2.write("\n")
    f.close()
    f2.close()
    return corpus

#句子分拆
def newsplit_func(filename):
    #文件比较小，文件行数
    count = len(open(filename,'r').readlines())
    print("文件行数："+str(count))    
    Contents=[]
    file_object=open (filename,'r',encoding='gbk')
    try:
        file_content=file_object.read()
    finally:
        file_object.close()
    Contents.append(file_content)
    #txt=Contents.split()
    
    for i in Contents:
        #line_split = re.split(r'[。！；？《》、“”，：→\n]',i)
        line_split = re.split(r'[。！:：；→？\n]',i)
    line_split = [myL.replace(u'\u3000',u'') for myL in line_split if len(myL)>2]
    newsplit = [myL.strip() for myL in line_split]
    newsplit = list(filter(None, newsplit))   
    print(newsplit[:5])
    return newsplit
 
#词向量
def word_embeddings_fun(word_vec_path):
    import numpy as np
    word_embeddings = {}
    f = open(word_vec_path, encoding='utf-8').readlines()
    print(f[:1]) #输出特征词数量与维度
    for line in f:
        # 把第一行的内容去掉
        if len(line)>12:
            values = line.split()
            # 第一个元素是词语
            word = values[0]
            embedding = np.asarray(values[1:], dtype='float32')
            word_embeddings[word] = embedding
    return word_embeddings    

#词向量模型
def model(vec_num,corpus,min_count):
    pre,ext = os.path.splitext(corpus)   #输入文件分开前缀，后缀   pre=test_01   ext=.txt
    model_txt = pre + '_model' + ext    #训练语料为按行分词后的文本文件    corpus=test_01_seg.txt
    vocab_txt = pre + '_vocab' + ext    #训练语料为按行分词后的文本文件    corpus=test_01_seg.txt
    from gensim.models import word2vec
    print(pre.split('_')[0]+"特征向量为："+str(vec_num)+"维。") 
    #训练模型
    sentences = word2vec.LineSentence(corpus)  # 加载语料,LineSentence用于处理分行分词语料
    #sentences1 = word2vec.Text8Corpus(corpus)  #用来处理按文本分词语料
    #print('=--=-=-=-=-=',sentences)
    model = word2vec.Word2Vec(sentences, size=vec_num,window=25,min_count=min_count,workers=5,sg=1,hs=1)  #训练模型就这一句话  去掉出现频率小于2的词,100维，
    # http://blog.csdn.net/szlcw1/article/details/52751314 训练skip-gram模型; 第一个参数是训练预料，min_count是小于该数的单词会被踢出，默认值为5，size是神经网络的隐藏层单元数，在保存的model.txt中会显示size维的向量值。默认是100。默认window=5
    model.wv.save_word2vec_format(model_txt,vocab_txt,binary=False) # 将模型保存成文本，model.wv.save_word2vec_format()来进行模型的保存的话，会生成一个模型文件。里边存放着模型中所有词的词向量。这个文件中有多少行模型中就有多少个词向量。
    return model,model_txt,vocab_txt

#句向量
def sentence_vec(words_list,word_embeddings,vec_num=100):                  
    sentence_vectors = []
    for i in words_list:
        if len(i)!=0:
        	#.get 是通过字典索引得到对应键值
            v = sum([word_embeddings.get(w, np.zeros((vec_num,))) for w in i])/(len(i))
        else:
            v = np.zeros((vec_num,))
        sentence_vectors.append(v)
    #print(sentence_vectors[:1])    
    return sentence_vectors

#句子相似度特征处理
def similarity_sentence(newsplit,sentence_vectors,vec_num):
    start = datetime.datetime.now()
    from sklearn.metrics.pairwise import cosine_similarity
    sim_mat = np.zeros([len(newsplit), len(newsplit)])    
    print("一共循环"+str(len(newsplit))+"次。")
    for i in range(len(newsplit)):
        print('\r当前进度：{1:<4.2f}%{0}'.format('▉'*int(10*i/len(newsplit)),(round(100*i/len(newsplit),2))), end='')
        for j in range(len(newsplit)):
            if i != j:
                sim_mat[i][j] = cosine_similarity(sentence_vectors[i].reshape(1,vec_num), sentence_vectors[j].reshape(1,vec_num))[0,0]
    print('\n特征处理完成！')
    print('\n特征处理时间：')
    end = datetime.datetime.now()
    print(end - start)    
    print("句子相似度矩阵的形状为：",sim_mat.shape)
    return sim_mat

#句子相似度计算
def ranked_sentences_func(sim_mat,newsplit):
    import networkx as nx    
    start_model = datetime.datetime.now()
    # 利用句子相似度矩阵构建图结构，句子为节点，句子相似度为转移概率
    nx_graph = nx.from_numpy_array(sim_mat)
    # 得到所有句子的textrank值
    scores = nx.pagerank(nx_graph)
    end_model = datetime.datetime.now()
    print('建模时间：')
    print(end_model - start_model)    
    # 根据textrank值对未处理的句子进行排序
    ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(newsplit)), reverse=True)
    return ranked_sentences

#新词发现匹配句子
def new_word_tosentence(word_list,ranked_sentences,stop_words,cut_all):    
    import numpy as np
    new_word_tosentence={}
    r=np.array(ranked_sentences).reshape(len(ranked_sentences),2)
    #词与句子相似度矩阵文本 
    ranked_sentences_split_word=word_cutstopwords_list(r[:,1],stop_words,cut_all) 
    for i in word_list:
        for j in range(len(r[:,1])):
            if i in ranked_sentences_split_word[j]:
                print(i+":"+ranked_sentences[j][1])
                new_word_tosentence[i]=ranked_sentences[j][1]
                break
    return new_word_tosentence

#确定k值
def kmeans_to_find_k(sim_mat,k_min=5,k_max=30):
    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt
    from scipy.spatial.distance import cdist
    from sklearn import metrics
    import numpy as np
    
    K = range(k_min, k_max)
    meandistortions = []
    silhouette_score_list=[]
    for k in K:
      kmeans = KMeans(n_clusters=k)
      kmeans.fit(sim_mat)
      meandistortions.append(sum(np.min(cdist(sim_mat, kmeans.cluster_centers_, 'euclidean'), axis=1)) / sim_mat.shape[0])
      #print('K = %s, 轮廓系数 = %.03f' % (k, metrics.silhouette_score(dt[:,2:], kmeans.labels_,metric='euclidean')))
      silhouette_score_list.append(metrics.silhouette_score(sim_mat, kmeans.labels_,metric='euclidean'))
    plt.plot(K, meandistortions, 'bx-',label=u'zhoubu')
    plt.plot(K,silhouette_score_list,'ro-',label=u'lunkuo')
    plt.xlabel('k')
    plt.ylabel('avg change')
    plt.title('K cnt_s to choose')
    plt.grid(True)
    plt.legend(loc='upper right')