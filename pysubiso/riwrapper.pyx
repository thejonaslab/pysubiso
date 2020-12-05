# cython: language_level=3, boundscheck=True
# distutils: language = c++
import numpy as np
import time

from libcpp.string cimport string
cdef extern from "rimatch.h":
   int is_indsubiso(int query_N, int * query_adj, int * query_vertlabel,               
                 int ref_N, int * ref_adj, int * ref_vertlabel, float maxtime) except +

   # int old_match(string referencefile,
   #               string queryfile);

# def old_match_call(reference_filename,
#                    query_filename):
#     return old_match(reference_filename, query_filename)


cpdef c_is_indsubiso(
    int[:, :] g_sub_adj,
    int[:] g_sub_colors,
    int[:, :] g_main_adj,
    int[:] g_main_colors,
    float maxtime,
):
    """
    Check if graph g (with provided node colors) is induced 
    subisomorphic to graph G.

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

    return is_indsubiso( g_sub_adj.shape[0],
                      &g_sub_adj[0, 0],
                      &g_sub_colors[0],
                      g_main_adj.shape[0],
                      &g_main_adj[0,0],
                      &g_main_colors[0], maxtime)

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

        res = is_indsubiso(
            g_sub_adj.shape[0],
            &sub_adj[0, 0],
            &g_sub_colors[0],
            g_main_adj.shape[0],
            &g_main_adj[0, 0],
            &g_main_colors[0],
            max(maxtime - elapsed_time, 1e-3) # fixme should be remaining time
        )
        results[pos] = res
        
        sub_adj[i, j] = orig_edge
        sub_adj[j, i] = orig_edge
        elapsed_time = time.time() - start_time
        if elapsed_time  > maxtime:
            raise Exception("timeout")

