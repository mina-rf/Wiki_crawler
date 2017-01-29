import numpy as np
import math
import operator


def mutual_info(term, docs, cluster):
    n = np.zeros((2, 2))
    for doc in docs:
        if doc['cluster'] == cluster:
            if doc['term_vector'][term] != 0:
                n[1, 1] += 1
            else:
                n[0, 1] += 1
        elif doc['term_vector'][term]:
            n[1, 0] += 1
        else:
            n[0, 0] += 1
    n = np.array(n)+1
    ans = 0
    for i in range(2):
        for j in range(2):
            # print((n[i, j] / ((n[i, 0] + n[i, 1]) * (n[0, j] + n[1, j]))))
            ans += (n[i, j] * math.log(n[i, j] / ((n[i, 0] + n[i, 1]) * (n[0, j] + n[1, j]))))
    return ans

def make_docs_clusters(term_vectors , clusters):
    ans = []
    for tv in term_vectors:
        ans.append({'cluster' : clusters[term_vectors.index(tv)] , 'term_vector' : tv})
    return ans


def choose_label(cluster_id , term_id , docs ):
    mu_infos = {term : mutual_info(id ,docs,cluster_id) for term , id in term_id.items()}
    mu_infos_sorted = sorted(mu_infos.items(), key=operator.itemgetter(1), reverse=True)
    return [item[0] for item in mu_infos_sorted[:5]]


def label_all(cluster_num , term_id , docs):
    return {i : choose_label(i , term_id , docs) for i in range(cluster_num)}








