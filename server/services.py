# -*- coding:utf-8 -*-

import os
import json
import pymysql
import gensim
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
        top_scores = list(map(lambda x:x[1], top_pairs))
        return list(zip(top_words, top_scores))
    
    def get_recent_articles(self, time_period = 300, num_limit = 10):
        #sql = """set @dt = (select date_add(now(), interval -%d day)); select a.ID, a.published_at, b.article from articles b left join headers a on a.ID = b.ID where (a.published_at > @dt) order by a.published_at desc limit %d"""%(time_period, num_limit)
        self.conn.Update("set @dt = (select date_add(now(), interval -300 day))")
        articles = self.conn.Query(" select tbla.ID, tbla.published_at, tblb.article from articles tblb left join headers tbla" + \
        " on (tbla.ID = tblb.ID) where (tbla.published_at > @dt) order by tbla.published_at desc limit 10;")
        #print(sql)
        articles = list(map(lambda x:list(x[:2])+[service.handleArticleBloomberg(x[2])], articles))
        return articles
        
