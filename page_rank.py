import numpy as np
from elasticsearch import Elasticsearch
from scipy import sparse
from sklearn.preprocessing import normalize
from elasticsearch_dsl import Search


def make_adjacency_matrix(index):
    es = Elasticsearch()
    # all_docs = es.search(index=index, body={"query": {"match_all": {}}})
    s = Search(using=es, index='wiki-index', doc_type='doc')
    all_docs = s.scan()
    url_id = {}
    matrix = sparse.csr_matrix(np.zeros((0, 0)))
    for hit in all_docs:

        page = hit['page']
        # print(page)
        if page not in url_id:
            url_id[page] = {'id' : len(url_id) , 'doc_id' : hit.meta.id}
            matrix = sparse.csr_matrix((matrix.data, matrix.indices, matrix.indptr),
                                       shape=(len(url_id) - 1, len(url_id)))
            matrix = sparse.vstack([matrix, sparse.csr_matrix((1, len(url_id)))])
        else:
            url_id[page]['doc_id'] = hit.meta.id
        for link in hit['links']:
            if link not in url_id:
                url_id[link] = {'id' : len(url_id) , 'doc_id' : 0}
                matrix = sparse.csr_matrix((matrix.data, matrix.indices, matrix.indptr),
                                           shape=(len(url_id) - 1, len(url_id)))
                matrix = sparse.vstack([matrix, sparse.csr_matrix((1, len(url_id)))])
            matrix[url_id[page]['id'], url_id[link]['id']] = 1

    normalize(matrix, norm='l1', axis=1, copy=False)
    return {'matrix': matrix, 'url_id': url_id}


def add_teleporting(p, alpha):
    n = p.shape[0]
    v = np.full((n, n,), 1 / n)
    ans = (1 - alpha) * p + alpha * v
    # print(ans)
    return ans.transpose()


def eigen_vector_power_method(sa, n, eigen_vector):
    for i in range(n):
        eigen_vector = sa.dot(eigen_vector)
        eigen_vector /= max(eigen_vector)
    return eigen_vector


def page_rank(eigen_vector):
    return eigen_vector / sum(eigen_vector)


def add_page_rank_to_index(pr_matrix, url_id, index):
    es = Elasticsearch()
    count = 0
    for url, id in url_id.items():
        if id['doc_id']!=0 :
            print(url, pr_matrix[id['id'], 0])
            es.update(index=index, doc_type='doc', id=id['doc_id'], body={'doc': {'page_rank': pr_matrix[id['id'], 0]}})





# res = make_adjacency_matrix('wiki-index')
# url_id = res['url_id']
#
# adj = res['matrix']
# m = add_teleporting(adj, 0.3)
# m = eigen_vector_power_method(m, 3, np.ones((m.shape[0], 1)))
# m = page_rank(m)
#
# add_page_rank_to_index(m, res['url_id'], 'wiki-index')

