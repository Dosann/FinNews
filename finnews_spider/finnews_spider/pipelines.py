# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
import pymysql
from twisted.enterprise import adbapi


class FinnewsSpiderPipeline(object):

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            port=settings['MYSQL_PORT'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)


    def __init__(self,dbpool):
        self.dbpool=dbpool

    #pipeline默认调用
    def process_item(self, item, spider):
        d=self.dbpool.runInteraction(self._conditional_insert, item, spider)#调用插入的方法
        log.msg("-------------------连接好了-------------------")
        d.addErrback(self._handle_error,item,spider)#调用异常处理方法
        d.addBoth(lambda _: item)
        return d

    def _conditional_insert(self, conn, item, spider):
        if item['article'] != '':
            log.msg("-------------------打印-------------------")


            conn.execute("insert into articles(id, article) values(%s, %s)",
                        (item['ID'], item['article']))
            log.msg("-------------------一轮循环完毕-------------------")
    def _handle_error(self, failue, item, spider):
        print(failue)