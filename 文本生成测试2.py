# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 11:13:43 2019

@author: weiqing.xwq
"""
import jieba,copy,re,codecs
from collections import Counter

stopwords = 'C:/Users/weiqing.xwq/Desktop/TextRank4ZH-master/textrank4zh/stopwords.txt'
title = ''
# coding = gbk
#text = '''推进技术从精美的手表到书架式扬声器，快速发展的技术不断推出新的用途和先进的小工具，并不断推向市场。这就是我们今天世界的现实，你可以花一整天的时间通过销售科技产品的商店，这可以把你的家变成一个智能的房子。以下是最新的小工具，它们将让您走在科技前沿，让您的生活更美好：FITBIT ALTA HR Fitbit Alta HR是一款可靠的健身追踪器，配有足够的电池汁，可让您长达一周。它监控您的步数，睡眠时间，燃烧的卡路里数和心率。腕带采用OLED显示屏，可与计算机无线同步。 NINTENDO NES CLASSIC EDITION这款Nintendo迷你游戏机通过为现代科技增添经典品味，带您回到过去。它包含30个经典的8位游戏，支持双人游戏，并允许怀旧游戏玩家通过HDMI连接到任何电视。 SHINOLA书架音箱新Shinola书架音箱是Shinola与工作室监听专家Barefoot Sound合作的成果。自供电双向扬声器不仅可以带来声音，还可以为客厅增添色彩，这要归功于它们整洁的手工橡木橱柜。它们配备了蓝牙，AUX和USB输入，为您提供一系列选项。 DELL XPS 13（2018）时尚。令人印象深刻。强大。持久。这款13英寸笔记本电脑具有足够的冲击力，可以方便地处理任何您扔的东西。 XPS 13的机身比几乎所有类型的笔记本电脑都小，几乎没有边框屏幕。 SAMSUNG GALAXY S9 +如果你需要的设备提供超出现有标准的东西并定义了高质量，那么你不应该看过三星Galaxy S9 +。它可能与S8 +有所不同，但这款智能手机本身就是一流的领导者。作为三星最新推出的产品，S9 +配备6.22英寸无限显示屏，配备革命性的2倍变焦背式摄像头，可捕捉逼真的图像。其3500mAh电池可在Wi-Fi和4G连接上为您提供长达15小时的互联网使用时间。 APPLE TV 4K苹果电视4K可以说是目前市场上最好的流媒体。该小工具可让您以4K HDR方式观看喜爱的节目，并提供远程和Siri语音选项，以获得优质体验。 SONOS PLAY：5无线多房间扬声器不会比Play：5更大。 Sonos的新产品不仅可以为您的房间充满丰富的声音，还可以为您提供全球80多种流媒体服务。您可以将小工具连接到Amazon Echo或Dot。有一个3.5毫米音频插座，旨在让您连接非流音频设备。'''
text= codecs.open('C:/Users/weiqing.xwq/Desktop/xhb.txt', 'r', 'gbk').read()
# summary = pyhanlp.HanLP.extractSummary(text, 3)
# print(summary)


class Summary():
    #**** 切分句子 ************
    def cutSentence(self,text):
        sents = []
        text = re.sub(r'\n+','。',text)  # 换行改成句号（标题段无句号的情况）
        text = text.replace('。。','。')  # 删除多余的句号
        text = text.replace('？。','。')  #
        text = text.replace('！。','。')  # 删除多余的句号
        sentences = re.split(r'。|！|？|】|；',text) # 分句
        #print(sentences)
        sentences = sentences[:-1] # 删除最后一个句号后面的空句
        for sent in sentences:
            len_sent = len(sent)
            if len_sent < 4:  # 删除换行符、一个字符等
                continue
            # sent = sent.decode('utf8')
            sent = sent.strip('　 ')
            sent = sent.lstrip('【')
            sents.append(sent)
        return sents

    #**** 提取特征词 **********************
    def getKeywords(self,title,sentences,n=10):
        words = []
        #**** 分词，获取词汇列表 *****
        # split_result = pseg.cut(text)
        for sentence in sentences:
            split_result = jieba.cut(sentence)
            for i in split_result:
                words.append(i)
        #**** 统计词频TF *****
        c = Counter(words) # 词典
        #**** 去除停用词(为了提高效率，该步骤放到统计词频之后)
        self.delStopwords(c)
        #**** 标题中提取特征 *********
        words_title = [word for word in jieba.cut(title,cut_all=True)]
        self.delStopwords(words_title)
        #**** 获取topN ************
        topN = c.most_common(n)
        # for i in topN:
        #     print(i[0],i[1])
        words_topN = [i[0] for i in topN if i[1]>1] #在topN中排除出现次数少于2次的词

        words_topN = list(set(words_topN)|set(words_title)) # 正文关键词与标题关键词取并集

        print (' '.join(words_topN))
        return words_topN

    #**** 去除停用词 *******************************
    def delStopwords(self,dict):
        sw_file = codecs.open(stopwords,encoding='utf8')
        stop_words = []
        for line in sw_file.readlines():
            stop_words.append(line.strip())
        #***** 输入参数为list *************
        # if type(dict) is types.ListType:
        if type(dict) is list:
            words = dict
            for word in words:
                if word in stop_words:
                    words.remove(word)
        #***** 输入参数type为 <class 'collections.Counter'>  *****
        else:
            words = copy.deepcopy(list(dict.keys()))
            for word in words:
                if word in stop_words:
                    del dict[word]
        return words

    #**** 提取topN句子 **********************
    def getTopNSentences(self,sentences,keywords,n=3):
        sents_score = {}
        len_sentences = len(sentences)
        #**** 初始化句子重要性得分，并计算句子平均长度
        len_avg = 0
        len_min = len(sentences[0])
        len_max = len(sentences[0])
        for sent in sentences:
            sents_score[sent] = 0
            l = len(sent)
            len_avg += l
            if len_min > l:
                len_min = l
            if len_max < l:
                len_max = l
        len_avg = len_avg / len_sentences
        # print(len_min,len_avg,len_max)
        #**** 计算句子权重得分 **********
        for sent in sentences:
            #**** 不考虑句长在指定范围外的句子 ******
            l = len(sent)
            if l < (len_min + len_avg) / 2 or l > (3 * len_max - 2 * len_avg) / 4:
                continue
            words = []
            sent_words = jieba.cut(sent) # <generator object cut at 0x11B38120>
            for i in sent_words:
                words.append(i)
            keywords_cnt = 0
            len_sent = len(words)
            if len_sent == 0:
                continue

            for word in words:
                if word in keywords:
                    keywords_cnt += 1
            score = keywords_cnt * keywords_cnt * 1.0 / len_sent
            sents_score[sent] = score
            if sentences.index(sent) == 0:# 提高首句权重
                sents_score[sent] = 2 * score
        #**** 排序 **********************
        dict_list = sorted(sents_score.items(),key=lambda x:x[1],reverse=True)
        # print(dict_list)
        #**** 返回topN ******************
        sents_topN = []
        for i in dict_list[:n]:
            sents_topN.append(i[0])
            # print i[0],i[1]
        sents_topN = list(set(sents_topN))
        #**** 按比例提取 **************************
        if len_sentences <= 5:
            sents_topN = sents_topN[:1]
        elif len_sentences < 9:
            sents_topN = sents_topN[:2]

        return sents_topN

    #**** 恢复topN句子在文中的相对顺序 *********
    def sents_sort(self,sents_topN,sentences):
        keysents = []
        for sent in sentences:
            if sent in sents_topN and sent not in keysents:
                keysents.append(sent)
        keysents = self.post_processing(keysents)

        return keysents

    def post_processing(self,keysents):
        #**** 删除不完整句子中的详细部分 ********************
        detail_tags = ['，一是','：一是','，第一，','：第一，','，首先，','；首先，']
        for i in keysents:
            for tag in detail_tags:
                index = i.find(tag)
                if index != -1:
                    keysents[keysents.index(i)] = i[:index]
        #**** 删除编号 ****************************
        for i in keysents:
            # print(i)
            regex = re.compile(r'^一、|^二、|^三、|^三、|^四、|^五、|^六、|^七、|^八、|^九、|^十、|^\d{1,2}、|^\d{1,2} ')
            result = re.findall(regex,i)
            if result:
                keysents[keysents.index(i)] = re.sub(regex,'',i)
        #**** 删除备注性质的句子 ********************
        for i in keysents:
            regex = re.compile(r'^注\d*：')
            result = re.findall(regex,i)
            if result:
                keysents.remove(i)
        #**** 删除句首括号中的内容 ********************
        for i in keysents:
            regex = re.compile(r'^.∗.∗')
            result = re.findall(regex,i)
            if result:
                keysents[keysents.index(i)] = re.sub(regex,'',i)
        #**** 删除来源(空格前的部分) ********************
        for i in keysents:
            regex = re.compile(r'^.{1,20} ')
            result = re.findall(regex,i)
            if result:
                keysents[keysents.index(i)] = re.sub(regex,'',i)
        #**** 删除引号部分（如：银行间债市小幅下跌，见下图：） ********************
        for i in keysents:
            regex = re.compile(r'，[^，]+：$')
            result = re.findall(regex,i)
            if result:
                keysents[keysents.index(i)] = re.sub(regex,'',i)

        return keysents

    def main(self,title,text):
        sentences = self.cutSentence(text)
        keywords = self.getKeywords(title, sentences, n=8)
        sents_topN = self.getTopNSentences(sentences, keywords, n=3)
        keysents = self.sents_sort(sents_topN, sentences)
        print(keysents)
        return keysents


#if __name__=='__main__':
summary=Summary()
summary.main(title,text)