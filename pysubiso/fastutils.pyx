import numpy as np
cimport numpy as np

cimport cython
import time

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef _gen_possible_next_edges(np.int32_t[:,:] adj,
                              np.int32_t[:] edge_colors,
                              np.int32_t[:, :] out):
    cdef Py_ssize_t i, j
    cdef np.int32_t c = 0 
    cdef Py_ssize_t pos = 0
    cdef Py_ssize_t color_n = edge_colors.shape[0]

    
    for i in range(adj.shape[0]):
        for j in range(i +1, adj.shape[1]):
            if adj[i, j] == 0:
                for c in range(color_n):
                    out[pos, 0] = i
                    out[pos, 1] = j
                    out[pos, 2] = edge_colors[c]
                    pos += 1
    return pos


cpdef gen_possible_next_edges(np.int32_t[:,:] adj, np.int32_t[:] edge_colors):
    """
    Given a (symmetric) input adjacency matrix adj and an
    array of possible colors, compute all possible edges that could be added
    to the matrix and return. 

    Note colors must be > 0 and we don't generate candidates for
    nodes that already have edges between them. 


    Input: adj: N x N _symmetric_ adjacency matrix (np.int32)
           colors: array of possible edge colors (> 0, np.int32)
    Returns:
           M x 3 np.int32 np.array of [(i, j, c)] where
                     c is the actual edge color value (not index)

    Note : We don't consider self-loops and only loop at the 
    upper-triangular part of the matrix. 
    """

    cpdef max_N = (adj.shape[0] * adj.shape[1] //2 * len(edge_colors))
    

    cpdef out = np.empty((max_N, 3), dtype=np.int32)

    num_out = _gen_possible_next_edges(adj, edge_colors, out)
    out.resize((num_out, 3))

    return out


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef _candidate_to_adj(np.int32_t[:, :] candidates, np.int8_t[:] success,
                       np.int32_t[:] color_idx_map,
                       int adj_N, int color_C,
                       np.int32_t[:, :, :] out_adj):

    cdef Py_ssize_t i, j, c, s, pos
    for pos in range(candidates.shape[0]):
        i = candidates[pos, 0]
        j = candidates[pos, 1]
        c = candidates[pos, 2]
        if success[pos]:
            out_adj[i, j, color_idx_map[c]] = 1
            out_adj[j, i, color_idx_map[c]] = 1



def candidate_to_adj(np.int32_t[:, :] candidates, np.int8_t[:] success,
                     np.int32_t[:] color_idx_map,
                     int adj_N, int color_C):
    """
    Convert a list of candidate edges and their successes to an adj map
    """

    out_adj = np.zeros((adj_N, adj_N, color_C), dtype=np.int32)

    _candidate_to_adj(candidates, success, color_idx_map,
                      adj_N, color_C, out_adj)
    return out_adj

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef _get_color_edge_possible_table(np.int32_t[:,:] adj,
                                   np.int32_t[:] node_colors,
                                   np.int32_t[:] possible_edge_colors,
                                   np.int32_t[:, :, :] out):

    cdef int i, j, nc_i, nc_j, ec
    cdef int possible_node_colors = np.max(node_colors)

    for i in range(adj.shape[0]):
        for j in range(i +1, adj.shape[1]):
            nc_i = node_colors[i]
            nc_j = node_colors[j]
            ec = adj[i,j]
            if ec > 0: # ec = 0 --> no edge
                out[nc_i, nc_j, ec] += 1
                if nc_i != nc_j: # don't double-count diagonal
                    out[nc_j, nc_i, ec] += 1
    return out

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cpdef get_color_edge_possible_table(np.int32_t[:,:] adj,
                                    np.int32_t[:] node_colors,
                                    np.int32_t[:] possible_edge_colors):
    """
    
    Returns NC x NC x EC matrix where 
    p[nc_i, nc_j, ec] = number of edges of color ec in adj 
    from node color i to node colorj 
    """
    cdef int possible_node_colors = np.max(node_colors)

    color_edge_possible_table = np.zeros((possible_node_colors + 1,
                                          possible_node_colors +1,
                                          np.max(possible_edge_colors) + 1),
                                         dtype=np.int32)

    _get_color_edge_possible_table(adj, node_colors,
                                  possible_edge_colors,
                                  color_edge_possible_table)
    return color_edge_possible_table

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef int _filter_edge_table(np.int32_t[:, :] candidate_edges,
                        np.int32_t[:] sub_colors,
                        np.int32_t[:, :, :] color_edge_possible_table,
                        np.int32_t[:, :] filtered_candidates_out) :
    cdef np.int32_t pos, i, j, c

    pos = 0
    cdef int N = candidate_edges.shape[0]
    cdef int ce_i
    cdef int nc_i, nc_j
    for ce_i in range(N):
        i = candidate_edges[ce_i, 0]
        j = candidate_edges[ce_i, 1]
        c = candidate_edges[ce_i, 2]

        nc_i = sub_colors[i]
        nc_j = sub_colors[j]

        if color_edge_possible_table[nc_i, nc_j, c] > 0:
            filtered_candidates_out[pos, 0] = i
            filtered_candidates_out[pos, 1] = j
            filtered_candidates_out[pos, 2] = c
            pos +=1
    return pos
            


cpdef filter_candidate_edges(sub_adj, sub_colors,
                             main_adj, main_colors,
                             possible_edge_colors, 
                             candidate_edges):
    """
    Filter candidate edges for graph sub using heuristics. 
    If we add (i, j, c) to sub is there any chance of it being subiso
    to main? 

    sub_adj, main_adj: adjacency matrix where entry is color _value_
    sub_colors, main_colors: unique colors in the graph

    heuristics used:
    1. If the main has no edges between node color i and node color j
       of edge color c then we can skip candidate 
    ## FIXME add more

    """
    assert np.min(possible_edge_colors) > 0 
    cdef int possible_node_colors = np.max(main_colors)

    color_edge_possible_table = np.zeros((possible_node_colors + 1,
                                          possible_node_colors +1,
                                          np.max(possible_edge_colors) + 1),
                                         dtype=np.int32)

    _get_color_edge_possible_table(main_adj, main_colors,
                                   possible_edge_colors,
                                   color_edge_possible_table)

    filtered_candidates_out = np.empty((len(candidate_edges),3), dtype=np.int32)
    num_out = _filter_edge_table(candidate_edges, sub_colors, color_edge_possible_table,
                                 filtered_candidates_out)
    filtered_candidates_out.resize(num_out, 3)
    return filtered_candidates_out
            
    

    
