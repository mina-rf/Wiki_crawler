# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os

from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from tqdm import tqdm


class ItemCounter(object):
    count = 0
    titles = set()

    def __init__(self):
        self.bar = tqdm(total=get_project_settings().get('CLOSESPIDER_PAGECOUNT'))

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.bar.close()

    def process_item(self, item, spider):
        if item['title'] not in self.titles:
            self.bar.update(1)
            self.count += 1
        return item


class DupContentPipeline(object):
    titles = set()

    def process_item(self, item, spider):
        if item['title'] in self.titles:
            raise DropItem('Duplicated Content for %s' % item['page'])
        else:
            self.titles.add(item['title'])
            return item


class JsonWriterPipeline(object):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(BASE_DIR, 'files')

    def open_spider(self, spider):
        for f in os.listdir(self.p):
            os.remove(os.path.join(self.p, f))

    def process_item(self, item, spider):
        file_name = item.get('title') + '.json'
        a = os.path.join(self.p, file_name)
        self.file = open(a, 'w')
        json.dump(dict(item), self.file)
        self.file.close()

        return item
