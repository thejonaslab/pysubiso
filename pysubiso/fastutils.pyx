import numpy as np
cimport numpy as np

cimport cython

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef _gen_possible_next_edges(np.int32_t[:,:] adj,
                              np.int32_t[:] colors,
                              np.int32_t[:, :] out):
    cdef Py_ssize_t i, j
    cdef np.int32_t c = 0 
    cdef Py_ssize_t pos = 0
    cdef Py_ssize_t color_n = colors.shape[0]

    
    for i in range(adj.shape[0]):
        for j in range(i +1, adj.shape[1]):
            if adj[i, j] == 0:
                for c in range(color_n):
                    out[pos, 0] = i
                    out[pos, 1] = j
                    out[pos, 2] = colors[c]
                    pos += 1
    return pos


cpdef gen_possible_next_edges(np.int32_t[:,:] adj, np.int32_t[:] colors):
    """
    Given a (symmetric) input adjacency matrix adj and an
    array of possible colors, compute all possible edges that could be added
    to the matrix and return. 


    Input: adj: N x N _symmetric_ adjacency matrix (np.int32)
           colors: array of possible edge colors (> 0, np.int32)
    Returns:
           M x 3 np.int32 np.array of [(i, j, c)] 

    Note : We don't consider self-loops and only loop at the 
    upper-triangular part of the matrix. 
    """

    cpdef max_N = (adj.shape[0] * adj.shape[1] //2 * len(colors))
    

    cpdef out = np.empty((max_N, 3), dtype=np.int32)

    num_out = _gen_possible_next_edges(adj, colors, out)
    out.resize((num_out, 3))

    return out
