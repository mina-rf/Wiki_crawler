import os
from os import listdir
from os.path import isfile, join

import json
from elasticsearch import Elasticsearch


def make_index(dir):
    es = Elasticsearch()
    es.indices.create(index='wiki-index', ignore=400)
    cwd = os.getcwd()
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    dir = os.path.join(BASE_DIR, dir)
    all_files = [f for f in listdir(dir) if isfile(join(dir, f))]
    for file in all_files:
        with open(str(dir)+'/'+str(file)) as data_file:
            body = json.load(data_file)
            es.index(index="wiki-index", doc_type='doc', body=body)


make_index('files')