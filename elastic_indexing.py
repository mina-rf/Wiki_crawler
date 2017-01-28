import json
import os
from os import listdir
from os.path import isfile, join

import elasticsearch
from elasticsearch import Elasticsearch


def make_index(dir):
    es = Elasticsearch()
    try:
        es.indices.delete(index='wiki-index', ignore=[400, 404])
    except elasticsearch.NotFoundError:
        pass
    es.indices.create(index='wiki-index', ignore=400)
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    dir = os.path.join(BASE_DIR, dir)
    all_files = [join(dir, f) for f in listdir(dir) if isfile(join(dir, f)) and not f.startswith('.')]
    for file in all_files:
        with open(file) as data_file:
            body = json.load(data_file)
            es.index(index="wiki-index", doc_type='doc', body=body)
    print('done')


make_index('files')
