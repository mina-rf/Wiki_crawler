# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WikiItem(scrapy.Item):
    title = scrapy.Field()
    preface = scrapy.Field()
    body = scrapy.Field()
    page = scrapy.Field()
    links = scrapy.Field()
    page_rank = scrapy.Field()
    cluster_id = scrapy.Field()

    def __str__(self):
        return ''
