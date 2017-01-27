import numpy as np
from scipy import sparse




def add_teleporting(p , alpha):
    n = p.shape[0]
    v = np.full((n,n,),1/n)
    ans = (1-alpha)*p + alpha*v
    print(ans)
    return ans


def eigen_vector_power_method(sa , n , eigen_vector):
    for i in range(n):
        eigen_vector = sa.dot(eigen_vector)
        eigen_vector /= max(eigen_vector)
    return eigen_vector


def page_rank(eigen_vector):
    return eigen_vector/sum(eigen_vector)

a = [[15 , 4 , 0] , [10 , 12 , 6] , [20 , 4 , 2]]
sa = sparse.csr_matrix(a)
ans = eigen_vector_power_method(sa,1 , eigen_vector_power_method(sa,1,np.ones(3)))

print(add_teleporting(sa , 0.5))
print(ans)
print(page_rank(ans))