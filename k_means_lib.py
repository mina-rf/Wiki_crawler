import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from sklearn.cluster import KMeans


def init():
    es = Elasticsearch()

    s = Search(using=es, index='wiki-index', doc_type='doc')
    response = s.scan()
    doc_ids = [hit.meta.id for hit in response]
    docs = {doc_id: get_term_vector(es, doc_id) for doc_id in doc_ids}

    dictionary = {}
    cnt = 0
    c = 0
    d_map = {}
    for doc_id in doc_ids:
        d_map[doc_id] = c
        c += 1
        term_vector = docs[doc_id]
        for term in term_vector:
            if term not in dictionary:
                dictionary[term] = cnt
                cnt += 1

    term_doc_matrix = [[0 for j in range(len(dictionary))] for i in range(len(doc_ids))]
    for doc_id, tv in docs.items():
        for t, f in tv.items():
            ind = dictionary[t]
            term_doc_matrix[d_map[doc_id]][ind] = f

    return dictionary, term_doc_matrix


def find_best_cluster(term_doc_matrix):
    prev_cost = np.math.inf
    prev_best_cluster = None
    for k in range(1, 20):  # TODO: input the limit
        best_cluster = KMeans(n_clusters=k, random_state=0).fit(X=term_doc_matrix)
        for i in range(2):
            kmeans = KMeans(n_clusters=k, random_state=0).fit(X=term_doc_matrix)
            if best_cluster.inertia_ > kmeans.inertia_:
                best_cluster = kmeans
        cost = best_cluster.inertia_ + 500000 * k
        if cost > prev_cost:
            print('k', k - 1)
            return prev_best_cluster
        # print('k', k, 'cost', cost + 500000 * k, 'delta', prev_cost - cost)
        prev_cost = cost
        prev_best_cluster = best_cluster


def get_term_vector(es, doc_id):
    tv_json = es.termvectors(index='wiki-index', doc_type='doc', id=doc_id, fields=['body'], term_statistics=True,
                             field_statistics=True, )
    term_vector = {}
    for term, info in tv_json['term_vectors']['body']['terms'].items():
        term_freq = info['term_freq']
        term_vector[term] = term_freq
        # doc_len += term_freq * term_freq
    # term_vector_normalized = {term: freq / math.sqrt(doc_len) for term, freq in term_vector.items()}
    return term_vector


if __name__ == '__main__':
    dic, term_doc_matrix = init()
    find_best_cluster(term_doc_matrix)
