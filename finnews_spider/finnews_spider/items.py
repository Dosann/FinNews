# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleItem(scrapy.Item):

    # ID of an article, int. Consistent with the one in table "headers"
    ID = scrapy.Field()
    # article content, text.
    article = scrapy.Field()

    def __repr__(self):
        """only print out attr1 after exiting the Pipeline"""
        return repr({"ID": self['ID']})
