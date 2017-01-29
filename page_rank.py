import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from scipy import sparse
from sklearn.preprocessing import normalize
from tqdm import trange, tqdm


def make_adjacency_matrix(index):
    es = Elasticsearch()
    s = Search(using=es, index=index, doc_type='doc')
    all_docs = s.scan()
    all_docs = [hit for hit in all_docs]
    print('making adjacency matrix:')
    url_id, matrix = build_matrix(all_docs)

    normalize(matrix, norm='l1', axis=1, copy=False)
    return matrix, url_id


def build_matrix(all_docs, meta=True):
    url_id = {}
    matrix = sparse.csr_matrix(np.zeros((0, 0)))
    for i in trange(len(all_docs)):
        hit = all_docs[i]
        page = hit['page']
        if page not in url_id:
            d = 0
            if meta:
                d = hit.meta.id
            url_id[page] = {'id': len(url_id), 'doc_id': d}
            matrix = sparse.csr_matrix((matrix.data, matrix.indices, matrix.indptr),
                                       shape=(len(url_id) - 1, len(url_id)))
            matrix = sparse.vstack([matrix, sparse.csr_matrix((1, len(url_id)))])
        else:
            if meta:
                url_id[page]['doc_id'] = hit.meta.id
        for link in hit['links']:
            if link not in url_id:
                url_id[link] = {'id': len(url_id), 'doc_id': 0}
                matrix = sparse.csr_matrix((matrix.data, matrix.indices, matrix.indptr),
                                           shape=(len(url_id) - 1, len(url_id)))
                matrix = sparse.vstack([matrix, sparse.csr_matrix((1, len(url_id)))])
            matrix[url_id[page]['id'], url_id[link]['id']] = 1
    return url_id, matrix


def add_teleporting(p, alpha):
    n = p.shape[0]
    v = np.full((n, n,), 1 / n)
    ans = (1 - alpha) * p + alpha * v
    return ans.transpose()


def eigen_vector_power_method(sa, n, eigen_vector):
    print('computing eigen vector:')
    for i in trange(n):
        eigen_vector = sa.dot(eigen_vector)
        eigen_vector /= max(eigen_vector)
    return eigen_vector


def page_rank(eigen_vector):
    return eigen_vector / sum(eigen_vector)


def add_page_rank_to_index(pr_matrix, url_id, index):
    print('updating index:')
    es = Elasticsearch()
    pbar = tqdm(total=len(url_id))
    for url, id in url_id.items():
        pbar.update(1)
        if id['doc_id'] != 0:
            es.update(index=index, doc_type='doc', id=id['doc_id'], body={'doc': {'page_rank': pr_matrix[id['id'], 0]}})
    pbar.close()


def compute_and_update_pr(alpha, index, itr):
    matrix, url_id = make_adjacency_matrix(index)
    matrix = add_teleporting(matrix, alpha)
    pr = eigen_vector_power_method(matrix, itr, np.ones((matrix.shape[0], 1)))
    pr = page_rank(pr)
    add_page_rank_to_index(pr, url_id, index)

# res = make_adjacency_matrix('wiki-index')
# url_id = res['url_id']
#
# adj = res['matrix']
# m = add_teleporting(adj, 0.3)
# m = eigen_vector_power_method(m, 3, np.ones((m.shape[0], 1)))
# m = page_rank(m)
#
# add_page_rank_to_index(m, res['url_id'], 'wiki-index')
