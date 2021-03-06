"""
Extended math utilities.
"""
# Authors: G. Varoquaux, A. Gramfort, A. Passos
# License: BSD

import sys
import math

import numpy as np
from scipy import linalg

#XXX: We should have a function with numpy's slogdet API
def _fast_logdet(A):
    """
    Compute log(det(A)) for A symmetric
    Equivalent to : np.log(np.linalg.det(A))
    but more robust
    It returns -Inf if det(A) is non positive or is not defined.
    """
    # XXX: Should be implemented as in numpy, using ATLAS
    # http://projects.scipy.org/numpy/browser/trunk/numpy/linalg/linalg.py#L1559
    ld = np.sum(np.log(np.diag(A)))
    a = np.exp(ld/A.shape[0])
    d = np.linalg.det(A/a)
    ld += np.log(d)
    if not np.isfinite(ld):
        return -np.inf
    return ld

def _fast_logdet_numpy(A):
    """
    Compute log(det(A)) for A symmetric
    Equivalent to : np.log(nl.det(A))
    but more robust
    It returns -Inf if det(A) is non positive or is not defined.
    """
    sign, ld = np.linalg.slogdet(A)
    if not sign > 0:
        return -np.inf
    return ld


# Numpy >= 1.5 provides a fast logdet
if hasattr(np.linalg, 'slogdet'):
    fast_logdet = _fast_logdet_numpy
else:
    fast_logdet = _fast_logdet

if sys.version_info[1] < 6:
    # math.factorial is only available in 2.6
    def factorial(x) :
        # simple recursive implementation
        if x == 0: return 1
        return x * factorial(x-1)
else:
    factorial = math.factorial


if sys.version_info[1] < 6:
    def combinations(seq, r=None):
        """Generator returning combinations of items from sequence <seq>
        taken <r> at a time. Order is not significant. If <r> is not given,
        the entire sequence is returned.
        """
        if r == None:
            r = len(seq)
        if r <= 0:
            yield []
        else:
            for i in xrange(len(seq)):
                for cc in combinations(seq[i+1:], r-1):
                    yield [seq[i]]+cc

else:
    import itertools
    combinations = itertools.combinations



def density(w, **kwargs):
    """Compute density of a sparse vector
        Return a value between 0 and 1
    """
    d = 0 if w is None else float((w != 0).sum()) / w.size
    return d


def fast_svd(M, k):
    """Computes the k-truncated SVD using random projections

    Parameters
    ===========
    M: ndarray or sparse matrix
        Matrix to decompose

    k: int
        Number of singular values and vectors to extract.

    Notes
    =====

    This algorithm finds the exact truncated eigenvalue decomposition
    using randomization to speed up the computations. I is particularly
    fast on large matrices on which you whish to extract only a small
    number of components.

    References: Finding structure with randomness: Stochastic
    algorithms for constructing approximate matrix decompositions,
    Halko, et al., 2009 (arXiv:909)

    """
    # Lazy import of scipy sparse, because it is very slow.
    from scipy import sparse
    p = k + 5
    r = np.random.normal(size=(M.shape[1], p))
    if sparse.issparse(M):
        Y = M * r
    else:
        Y = np.dot(M, r)
    del r
    Q, r = linalg.qr(Y)
    if sparse.issparse(M):
        B = Q.T * M
    else:
        B = np.dot(Q.T, M)
    a = linalg.svd(B, full_matrices=False)
    Uhat = a[0]
    del B
    s = a[1]
    v = a[2]
    U = np.dot(Q, Uhat)
    return U.T[:k].T, s[:k], v[:k]

