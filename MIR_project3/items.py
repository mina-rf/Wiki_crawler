# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from collections import defaultdict

import scrapy


class WikiItem(scrapy.Item):
    title = scrapy.Field()
    preface = scrapy.Field()
    body = scrapy.Field()
    page = scrapy.Field()
    links = scrapy.Field()
    page_rank = scrapy.Field()
    cluster_id = scrapy.Field()
    abstract = scrapy.Field()

    def __str__(self):
        return ''


class FlexibleItem(scrapy.Item):
    fields = defaultdict(scrapy.Field)

    def __setitem__(self, key, value):
        self._values[key] = value
