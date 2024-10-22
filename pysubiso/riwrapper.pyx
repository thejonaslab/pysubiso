# cython: language_level=3, boundscheck=True
# distutils: language = c++
import numpy as np
import time
cimport numpy as cnp

from libcpp.string cimport string
cdef extern from "rimatch.h":
   int is_match(int query_N, int * query_adj, int * query_vertlabel,               
                int ref_N, int * ref_adj, int * ref_vertlabel, float maxtime,
                int match_type) nogil except +

   int which_edges_indsubiso_incremental(int query_N, int * query_adj, int * query_vertlabel,               
                                         int ref_N, int * ref_adj, int * ref_vertlabel,
                                         int possible_edges_N, int * possible_edges,
                                         int * possible_edges_out, 
                                         float max_time) nogil except +
   


cpdef c_is_match(
    int[:, :] g_sub_adj,
    int[:] g_sub_colors,
    int[:, :] g_main_adj,
    int[:] g_main_colors,
    float maxtime,
    int match_type
):
    """
    Check if graph g_sub (with provided node colors) is either:
    - isomorphic (match_type = 0 )
    - induced subisomorphic (match_type = 1) 
    to a (potentially larger) graph g_main. 

    Note that non-zero values in the adjacency matrices 
    are treated as labeled edges and the adj matrix 
    is assumed to be symmetric (A.T = A)

    g_sub_adj: adjacency matrix for subgraph to check
    g_sub_colors: integer labels for each node of subgraph
    g_main_adj: adjacency matrix for full graph
    g_main_colors: integer labels for each node of subgraph
    maxtime: maximum runtime for a single call to is_subiso
    """
    assert g_sub_adj.shape[0] == g_sub_adj.shape[1]
    assert len(g_sub_colors) == g_sub_adj.shape[0]
    
    assert g_main_adj.shape[0] == g_main_adj.shape[1]
    assert len(g_main_colors) == g_main_adj.shape[0]

    return is_match( g_sub_adj.shape[0],
                     &g_sub_adj[0, 0],
                     &g_sub_colors[0],
                     g_main_adj.shape[0],
                     &g_main_adj[0,0],
                     &g_main_colors[0], maxtime, match_type)

cpdef c_which_edges_indsubiso(
    int[:, :] g_sub_adj,
    int[:] g_sub_colors,
    int[:, :] g_main_adj,
    int[:] g_main_colors,
    int[:, :] possible_edges,
    int[:] results,
    float maxtime,
):
    """
    Get which edges that when added to g, preserve induced subisomorphism to G.

    g_sub_adj: adjacency matrix for subgraph to check
    g_sub_colors: integer labels for each node of subgraph
    g_main_adj: adjacency matrix for full graph
    g_main_colors: integer labels for each node of subgraph
    poss_edges_add : N x 3 list of [i, j, color] of possible next edges
    maxtime: maximum runtime for a single call to is_subiso
    """
    assert g_sub_adj.shape[0] == g_sub_adj.shape[1]
    assert len(g_sub_colors) == g_sub_adj.shape[0]
    
    assert g_main_adj.shape[0] == g_main_adj.shape[1]
    assert len(g_main_colors) == g_main_adj.shape[0]


    assert possible_edges.shape[1] == 3
    
    cdef int n_sub_nodes = g_sub_adj.shape[0]
    cdef int res
    cdef int[:, :] sub_adj = np.copy(g_sub_adj)
    cdef double start_time = time.time()
    cdef double elapsed_time = 0.0
    cdef int i, j, c, pos
    for pos, (i, j, c) in enumerate(possible_edges):
        orig_edge = sub_adj[i, j]
        sub_adj[i, j] = c
        sub_adj[j, i] = c # FIXME do we need to do this

        elapsed_time = time.time() - start_time

        res = is_match(
            g_sub_adj.shape[0],
            &sub_adj[0, 0],
            &g_sub_colors[0],
            g_main_adj.shape[0],
            &g_main_adj[0, 0],
            &g_main_colors[0],
            max(maxtime - elapsed_time, 1e-3), 1
        )
        results[pos] = res
        
        sub_adj[i, j] = orig_edge
        sub_adj[j, i] = orig_edge
        elapsed_time = time.time() - start_time
        if elapsed_time  > maxtime:
            raise Exception("timeout")

cpdef c_which_edges_indsubiso_incremental(
    int[:, :] g_sub_adj,
    int[:] g_sub_colors,
    int[:, :] g_main_adj,
    int[:] g_main_colors,
    int[:, :] possible_edges,
    float maxtime,
):
    """
    Get which edges that when added to g, preserve induced subisomorphism to G.

    g_sub_adj: adjacency matrix for subgraph to check
    g_sub_colors: integer labels for each node of subgraph
    g_main_adj: adjacency matrix for full graph
    g_main_colors: integer labels for each node of subgraph
    poss_edges_add : N x 3 list of [i, j, color] of possible next edges
    maxtime: maximum runtime for a single call to is_subiso
    """
    assert g_sub_adj.shape[0] == g_sub_adj.shape[1]
    assert len(g_sub_colors) == g_sub_adj.shape[0]
    
    assert g_main_adj.shape[0] == g_main_adj.shape[1]
    assert len(g_main_colors) == g_main_adj.shape[0]


    cdef int OUT_N = possible_edges.shape[0]
    assert possible_edges.shape[1] == 3
    
    cdef int n_sub_nodes = g_sub_adj.shape[0]
    # cdef int[:, :] sub_adj = np.copy(g_sub_adj)
    cdef double start_time = time.time()
    cdef double elapsed_time = 0.0

    possible_out = np.zeros((OUT_N,), dtype=np.int32)
    
    cdef int[:,] po = possible_out


    r = which_edges_indsubiso_incremental(g_sub_adj.shape[0],
                                       &g_sub_adj[0, 0], 
                                       &g_sub_colors[0],
                                       g_main_adj.shape[0],                                        
                                       &g_main_adj[0, 0],
                                       &g_main_colors[0], 
                                       OUT_N,                                        
                                       &possible_edges[0,0],
                                       &po[0],
                                       maxtime)

    if r == -1:
        raise RuntimeError("timeout")
    return possible_out > 0

    # cdef int i, j, c, pos
    # for pos, (i, j, c) in enumerate(possible_edges):
    #     orig_edge = sub_adj[i, j]
    #     sub_adj[i, j] = c
    #     sub_adj[j, i] = c # FIXME do we need to do this

    #     elapsed_time = time.time() - start_time

    #     res = is_indsubiso(
    #         g_sub_adj.shape[0],
    #         &sub_adj[0, 0],
    #         &g_sub_colors[0],
    #         g_main_adj.shape[0],
    #         &g_main_adj[0, 0],
    #         &g_main_colors[0],
    #         max(maxtime - elapsed_time, 1e-3) # fixme should be remaining time
    #     )
    #     results[pos] = res
        
    #     sub_adj[i, j] = orig_edge
    #     sub_adj[j, i] = orig_edge
    #     elapsed_time = time.time() - start_time
    #     if elapsed_time  > maxtime:
    #         raise Exception("timeout")

