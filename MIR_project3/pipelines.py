# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os


class MirProject3Pipeline(object):
    def process_item(self, item, spider):
        file_name = item.get('title') + '.json'
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        p = os.path.join(BASE_DIR, 'files')
        a = os.path.join(p, file_name)
        self.file = open(a, 'w')
        json.dump(dict(item), self.file)
        self.file.close()

        return item
