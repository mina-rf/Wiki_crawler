import math

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from scipy import sparse
from sklearn.cluster import KMeans
from tqdm import tqdm

from cluster_labeling import make_docs_clusters, label_all
from elastic_indexing import INDEX_NAME


def cluster(L):
    dic, term_doc_matrix, doc_id = init()
    k, best_cluster = find_best_cluster(term_doc_matrix, L)
    docs = make_docs_clusters(term_doc_matrix, best_cluster.labels_)
    update_index_clusters(doc_id, best_cluster.labels_)
    label_all(k, dic, docs)
    print('http://localhost:9200/' + INDEX_NAME + '/_search?pretty=true&size=100')


def init():
    es = Elasticsearch()

    s = Search(using=es, index=INDEX_NAME, doc_type='doc')
    response = s.scan()
    doc_ids = [hit.meta.id for hit in response]
    docs = {doc_id: get_term_vector(es, doc_id) for doc_id in doc_ids}

    dictionary = {}
    cnt = 0
    d_map = {}
    for i, doc_id in enumerate(doc_ids):
        d_map[doc_id] = i
        term_vector = docs[doc_id]
        for term in term_vector:
            if term not in dictionary:
                dictionary[term] = cnt
                cnt += 1

    # TODO: Use sparce matrix
    # term_doc_matrix = [[0 for _ in range(len(dictionary))] for _ in range(len(doc_ids))]
    pbar = tqdm(total=len(docs))
    term_doc_matrix = sparse.lil_matrix((len(doc_ids), len(dictionary)))
    for doc_id, tv in docs.items():
        pbar.update(1)
        for term, freq in tv.items():
            term_idx = dictionary[term]
            doc_idx = d_map[doc_id]
            term_doc_matrix[doc_idx, term_idx] = freq

    return dictionary, term_doc_matrix, doc_ids


def find_best_cluster(term_doc_matrix, L):
    prev_cost = math.inf
    prev_best_cluster = None
    if L == -1:
        L = math.inf
    for k in range(1, L + 1):  # TODO: input the limit
        best_cluster = KMeans(n_clusters=k, random_state=0).fit(X=term_doc_matrix)
        for i in range(2):
            kmeans = KMeans(n_clusters=k, random_state=0).fit(X=term_doc_matrix)
            if best_cluster.inertia_ > kmeans.inertia_:
                best_cluster = kmeans
        cost = best_cluster.inertia_ + 500000 * k
        print('هزینه', k, 'خوشه:', cost)
        if cost > prev_cost:
            print('k بهینه', k - 1)
            return k - 1, prev_best_cluster
        # print('k', k, 'cost', cost + 500000 * k, 'delta', prev_cost - cost)
        prev_cost = cost
        prev_best_cluster = best_cluster
    print('k بهینه', L)
    return L, best_cluster


def get_term_vector(es, doc_id):
    tv_json = es.termvectors(index=INDEX_NAME, doc_type='doc', id=doc_id, fields=['body'], term_statistics=True,
                             field_statistics=True, )
    term_vector = {term: info['term_freq']
                   for term, info in tv_json['term_vectors']['body']['terms'].items()}

    return term_vector


def update_index_clusters(doc_id, clusters):
    es = Elasticsearch()
    for _id in doc_id:
        es.update(index='wiki-index', doc_type='doc', id=_id,
                  body={'doc': {'cluster_id': int(clusters[doc_id.index(_id)])}})


if __name__ == '__main__':
    dic, term_doc_matrix = init()
    find_best_cluster(term_doc_matrix)
# dic, term_doc_matrix  , doc_id = init()
# cluster = find_best_cluster(term_doc_matrix)
# docs = make_docs_clusters(term_doc_matrix , cluster.labels_)
# update_index_clusters(doc_id , cluster.labels_)
# ans = label_all(3 , dic,docs)
# update_label_index(ans)

# labels = choose_label(1,dic,docs)
# print(choose_label(1,dic,docs))
# print(choose_label(2,dic,docs))
# print(choose_label(3,dic,docs))
