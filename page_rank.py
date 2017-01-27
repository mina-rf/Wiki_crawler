import numpy as np
from scipy import sparse
from elasticsearch import Elasticsearch
from sklearn.preprocessing import normalize


def make_adjacency_matrix(index):
    es = Elasticsearch()
    all_docs = es.search(index=index, body={"query": {"match_all": {}}})
    url_id = {}
    matrix = sparse.csr_matrix(np.zeros((0,0)))
    for hit in all_docs['hits']['hits']:
        print('hit')

        page = hit['_source']['page']

        if page not in url_id:
            url_id[page] = len(url_id)
            # matrix = np.append(matrix, np.zeros((1, len(url_id)-1)), axis=0)
            matrix = sparse.csr_matrix((matrix.data, matrix.indices, matrix.indptr),shape = (len(url_id)-1, len(url_id)))
            matrix = sparse.vstack([matrix, sparse.csr_matrix((1, len(url_id)))])
            # matrix = np.append(matrix, np.zeros((len(url_id), 1)), axis=1)
        for link in hit['_source']['links']:
            if link not in url_id :
                url_id[link] = len(url_id)
                # matrix = np.append(matrix, np.zeros((1,len(url_id)-1)) , axis=0)
                # matrix = np.append(matrix, np.zeros((len(url_id) , 1)) , axis=1)
                matrix = sparse.csr_matrix((matrix.data, matrix.indices, matrix.indptr),
                                           shape=(len(url_id) - 1, len(url_id)))
                matrix = sparse.vstack([matrix, sparse.csr_matrix((1, len(url_id)))])
            matrix[url_id[page],url_id[link]]=1


    normalize(matrix, norm='l1', axis=1 , copy=False)
    return {'matrix' :matrix , 'url_id' : url_id}


def add_teleporting(p , alpha):
    n = p.shape[0]
    v = np.full((n,n,),1/n)
    ans = (1-alpha)*p + alpha*v
    # print(ans)
    return ans.transpose()


def eigen_vector_power_method(sa , n , eigen_vector):
    for i in range(n):
        eigen_vector = sa.dot(eigen_vector)
        eigen_vector /= max(eigen_vector)
    return eigen_vector


def page_rank(eigen_vector):
    return eigen_vector/sum(eigen_vector)

# a = [[15 , 4 , 0] , [10 , 12 , 6] , [20 , 4 , 2]]
# sa = sparse.csr_matrix(a)
# ans = eigen_vector_power_method(sa,1 , eigen_vector_power_method(sa,1,np.ones(3)))

# print(add_teleporting(sa , 0.5))
# print(ans)
# print(page_rank(ans))
adj = make_adjacency_matrix('wiki-index')['matrix']
m = add_teleporting(adj,0.3)
m = eigen_vector_power_method(m , 3 , np.ones((m.shape[0],1)))
m= page_rank(m)
print(m)