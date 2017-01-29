# -*- coding: utf-8 -*-
import json
import os
from os import listdir
from os.path import isfile, join

import elasticsearch
from elasticsearch import Elasticsearch
from tqdm import tqdm

INDEX_NAME = 'wiki-index'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def make_index(index_dir):
    es = Elasticsearch()
    try:
        es.indices.delete(index=INDEX_NAME, ignore=[400, 404])
    except elasticsearch.NotFoundError:
        pass
    es.indices.create(index=INDEX_NAME, ignore=400)
    index_dir = os.path.join(BASE_DIR, index_dir)
    all_files = [join(index_dir, f) for f in listdir(index_dir) if isfile(join(index_dir, f)) and not f.startswith('.')]
    bar = tqdm(total=len(all_files))
    for file in all_files:
        bar.update(1)
        with open(file) as data_file:
            body = json.load(data_file)
            es.index(index=INDEX_NAME, doc_type='doc', body=body)
    print('http://localhost:9200/' + INDEX_NAME + '/_search?pretty=true&size=100')
    es.index(index=INDEX_NAME, doc_type='cluster', body={'cluster_id': 0, 'label': 'همه'})


def get_docs_list(index_dir):
    out = []
    index_dir = os.path.join(BASE_DIR, index_dir)
    all_files = [join(index_dir, f) for f in listdir(index_dir) if isfile(join(index_dir, f)) and not f.startswith('.')]
    bar = tqdm(total=len(all_files))
    for file in all_files:
        bar.update(1)
        with open(file) as data_file:
            body = json.load(data_file)
            out.append(body)
    return out


def delete_index(index):
    es = Elasticsearch()
    es.indices.delete(index=index, ignore=[400, 404])
    print('نمایه ' + index + 'با موفقیت پاک شد.')
