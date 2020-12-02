# cython: language_level=3, boundscheck=True
# distutils: language = c++
import numpy as np

from libcpp.string cimport string
cdef extern from "ritest.h":
   int is_subiso(int query_N, int * query_adj, int * query_vertlabel,               
                 int ref_N, int * ref_adj, int * ref_vertlabel, float maxtime) except +

   # int old_match(string referencefile,
   #               string queryfile);

def test():
    print("hello world")
    return 12345



        # wasiso, mapping = cythontest.lemon_subiso_vf2(
        #     gsub_adj, gmain_colors, 
        #     gmain_adj, gmain_colors, 
        #     weighted_edges=True, max_run_sec=max_run_sec)

# def old_match_call(reference_filename,
#                    query_filename):
#     return old_match(reference_filename, query_filename)

cpdef c_is_subiso(
    int[:, :] g_sub_adj,
    int[:] g_sub_colors,
    int[:, :] g_main_adj,
    int[:] g_main_colors,
    float maxtime,
):
    """
    Check if graph g (with provided node colors) is subisomorphic to graph G.

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

    return is_subiso( g_sub_adj.shape[0],
                      &g_sub_adj[0, 0],
                      &g_sub_colors[0],
                      g_main_adj.shape[0],
                      &g_main_adj[0,0],
                      &g_main_colors[0], maxtime)

cpdef c_which_edges_subiso_labeled(
    int[:, :] g_sub_adj,
    int[:] g_sub_colors,
    int[:, :] g_main_adj,
    int[:] g_main_colors,
    int[:, :] poss_edges_adj,
    float maxtime,
):
    """
    Get which edges that when added to g, preserve subisomorphism to G.

    g_sub_adj: adjacency matrix for subgraph to check
    g_sub_colors: integer labels for each node of subgraph
    g_main_adj: adjacency matrix for full graph
    g_main_colors: integer labels for each node of subgraph
    poss_edges_adj: adjacency matrix to return results in
    maxtime: maximum runtime for a single call to is_subiso
    """
    assert g_sub_adj.shape[0] == g_sub_adj.shape[1]
    assert len(g_sub_colors) == g_sub_adj.shape[0]
    
    assert g_main_adj.shape[0] == g_main_adj.shape[1]
    assert len(g_main_colors) == g_main_adj.shape[0]

    assert poss_edges_adj.shape[0] == poss_edges_adj.shape[1]
    assert g_sub_adj.shape[0] == poss_edges_adj.shape[0]

    cdef int n_sub_nodes = g_sub_adj.shape[0]
    cdef int res
    cdef int[:, :] sub_adj = np.copy(g_sub_adj)
    for i in range(n_sub_nodes):
        for j in range(i + 1, n_sub_nodes):
            if sub_adj[i, j] == 0:  # try adding edge
                sub_adj[i, j] = 1
                sub_adj[j, i] = 1
                res = is_subiso(
                    g_sub_adj.shape[0],
                    &sub_adj[0, 0],
                    &g_sub_colors[0],
                    g_main_adj.shape[0],
                    &g_main_adj[0, 0],
                    &g_main_colors[0],
                    maxtime
                )
                sub_adj[i, j] = 0
                sub_adj[j, i] = 0

                poss_edges_adj[i, j] = res
                poss_edges_adj[j, i] = res

# def lemon_subiso_vf2(int[:, :] gsub_adj, int[:] gsub_label, 
#                      int[:, :] gmain_adj, int[:] gmain_label, 
#                      multiple_edges=False, weighted_edges=False, 
#                      max_run_sec=10.0):
# 
#     
#     cdef int d = gmain_adj.shape[0] 
#     cdef int[:] out = np.zeros(d, dtype=np.int32)
# 
#     cdef int out_size = 0; 
# 
#     
#     wasiso=  subiso_vf2_weighted(&gsub_adj[0, 0], 
#                                  &gsub_label[0], len(gsub_adj), 
#                                  &gmain_adj[0, 0], &gmain_label[0], 
#                                  len(gmain_adj), 
#                                  &out[0], &out_size, max_run_sec)
#     return wasiso, np.array(out[:out_size])
# 
# def py_which_edges_subiso_labeled(int[:, :] g_full_in, int[:, :] g_sub_in, 
#                                   int[:] g_label_in, 
#                                   int[:,:, :] g_skip, 
#                                   int[:] g_possible_weights,
#                                   float max_run_sec=0.0):
# 
#     N = g_full_in.shape[0]
#     PW = len(g_possible_weights)
#     possible_out = np.zeros((N, N, PW), dtype=np.int32)
#     
#     cdef int[:, :, :] po = possible_out
#     with nogil:
#         r = which_edges_subiso_labeled(&g_full_in[0, 0], 
#                                        &g_sub_in[0, 0], 
#                                        &g_label_in[0], 
#                                        &g_skip[0,0, 0], 
#                                        N, 
#                                        &g_possible_weights[0], 
#                                        PW,
#                                        &po[0,0, 0], max_run_sec)
#     if r == -1:
#         raise RuntimeError("Ran over time")
#     return possible_out
