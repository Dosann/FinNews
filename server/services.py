# -*- coding:utf-8 -*-

import os
import json
import pymysql
import gensim
from math import ceil
from mysqlconnection import MysqlConnection

class service():

    def __init__(self):
        # paths
        self.path_dct   = 'models/dict01.dat'
        self.path_tfidf = 'models/tfidf01.dat'

        self.conn = MysqlConnection()
        self.InitTfidf(force = False)

    def get_newest_article(self):
        return service.handleArticleBloomberg(self.conn.Query("""select article from articles order by ID desc limit 1""")[0][0])
    
    @staticmethod
    def handleArticleBloomberg(text):
        return text[476:]

    def get_all_article(self):
        articles = self.conn.Query("""select article from articles""")
        articles = list(map(lambda x:x[0], articles))
        return articles

    def InitTfidf(self, force = False):
        if force == True:
            articles = self.ArticlePreprocess(self.get_all_article())
            self.dct = self.DictionaryGenerateModel(articles)
            self.tfidf = self.TfidfGenerateModel(articles, self.dct)
        else:
            self.dct = None
            if not (os.path.exists(self.path_dct) and os.path.exists(self.path_tfidf)):
                articles = self.ArticlePreprocess(self.get_all_article())
            if os.path.exists(self.path_dct):
                self.dct = gensim.corpora.Dictionary.load(self.path_dct)
            else:
                self.dct = self.DictionaryGenerateModel(articles)
            if os.path.exists(self.path_tfidf):
                self.tfidf = gensim.models.TfidfModel.load(self.path_tfidf)
            else:
                self.tfidf = self.TfidfGenerateModel(articles, self.dct)
        print('Dictionary and Tfidf model initialized.')

    def ArticlePreprocess(self, articles):
        articles = list(map(service.handleArticleBloomberg, articles))
        articles = list(map(lambda x:list(gensim.utils.tokenize(x)), articles))
        return articles
    
    def DictionaryGenerateModel(self, articles):
        # Train dictionary
        dct = gensim.corpora.Dictionary(articles)
        dct.save(self.path_dct)
        print("Generated gensim.corpora.Dictionary from articles, and saved it to '%s'."%self.path_dct)
        return dct

    def TfidfGenerateModel(self, articles, dct):
        # Train tfidf model
        corpus = [dct.doc2bow(article) for article in articles]
        model = gensim.models.TfidfModel(corpus)
        model.save(self.path_tfidf)
        print("Generated gensim.models.TfidfModel from articles, and saved it to '%s'."%self.path_tfidf)
        return model
    
    def get_keywords(self, article, num_keywords = 20):
        article = self.ArticlePreprocess([article])
        #print(article)
        vector = self.dct.doc2bow(article[0])
        rank = sorted(self.tfidf[vector], key = lambda x:x[1], reverse = True)
        num_keywords = min(len(rank), num_keywords)
        top_pairs = rank[:num_keywords]
        #print(top_rank)
        top_words  = list(map(lambda x:self.dct[x[0]], top_pairs))
        top_scores = list(map(lambda x:ceil(x[1] * 300), top_pairs))
        return list(zip(top_words, top_scores))
    
    def get_recent_articles(self, time_period = 30, num_limit = 100):
        self.conn.Update("set @dt = (select date_add(now(), interval -%d day))"%time_period)
        num_articles = self.conn.Query("select count(*) from headers where published_at > @dt")[0][0]
        num_articles_select = min(num_articles, num_limit)
        articles = self.conn.Query("select tbla.ID, tbla.published_at, tblb.article from articles tblb left join headers tbla " + \
        "on (tbla.ID = tblb.ID) where tbla.ID in " + \
        "(select * from (select ID from headers where published_at > @dt order by rand() limit %d) as tbl02);"%num_articles_select)
        num_articles_selected = len(articles)
        print("Loaded %d articles from db."%num_articles_selected)
        # for article in articles:
        #     print(article[0], article[1])
        #print(sql)
        if num_articles_selected == 0:
            articles = None
        else:
            articles = list(map(lambda x:list(x[:2])+[service.handleArticleBloomberg(x[2])], articles))
        return articles
        
    def get_wordfreq(self, period = 'monthly', word = None):
        tablemap = dict{
            'monthly' : 'wordcount_monthly',
            'weekly'  : 'wordcount_weekly',
            'daily'   : 'wordcount_daily'
        }
        wordfreq = self.conn.Query("""select day,counts from %s"""%tablemap[period])
        date = list(map(lambda x:pd.Timestamp.strftime('%Y-%m-%d', x[0]), wordfreq))

