"""
This is a Spyder project to grab historic news from serveral sources.
writtenby : duxin
email     : duxn_be@outlook.com
2018 All rights reserved.
"""

import scrapy
from scrapy import log
from finnews_spider.items import ArticleItem
import pymysql
#import queue
import time

class MySpider(scrapy.Spider):
    name='get_articles'

    def GetConnection():
        conn = pymysql.connect(host = 'localhost',
                       db = 'finnews',
                       port = 3306,
                       user = 'root',
                       password = '123456',
                       use_unicode = True,
                       charset = 'utf8')
        return conn

    conn = GetConnection()
    cur = pymysql.cursors.Cursor(connection = conn)
    cur.execute('select id,title,url from headers where article_downloaded is NULL')
    data = cur.fetchall()
    num_original_tasks = len(data)
    num_tasks = len(data)
    #self.que = ConstructQueue(data)
    start_urls = [task[2]+'?duxin_task_id=%d'%task[0] for task in data]
    del data
    
    def __init__(self, *a, **kw):
        super(MySpider, self).__init__(*a, **kw)
 

    def parse(self, response):
        spliter = '?duxin_task_id='
        url = response.url
        if spliter not in url:
            url = response.request.meta['redirect_urls'][0]
            taskid = int(url.split(spliter)[-1])
            print('Error: Visit blocked by server! Task id: %d'%taskid)
            #num_tasks += 1
            yield scrapy.Request(url)
        else:
            taskid = int(url.split(spliter)[-1])
            selector = response.selector.xpath('//article').xpath('//p/text()')
            doc = ''.join(selector.extract())
            doc = doc[:65000]

            item = ArticleItem()
            item['ID'] = taskid
            item['article'] = doc
            log.msg('Successfully inserted article NO. %d into database. %s'%(taskid, str(time.ctime())))
            yield item

