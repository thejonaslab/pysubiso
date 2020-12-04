import numpy as np
import copy
from libcpp.utility cimport pair
from libcpp.vector cimport vector

from libc.stdint cimport uint32_t
from libcpp cimport bool


cimport numpy as np
cimport cython

from libcpp.string cimport string

ctypedef pair[uint32_t, uint32_t] edge_t
ctypedef vector[edge_t] edgelist_t



cdef extern from "lemonmatch.h":
     int numpy_test(float *, int)
     int subiso_vf2(int *, int *, int,
                    int *, int *, int, 
                    int *, int *)

     int subiso_vf2_multi(int *, int *, int,
                          int *, int *, int, 
                          int *, int *)

     int subiso_vf2_weighted(int *, int *, int,
                          int *, int *, int, 
                          int *, int *, double) except + 

     int which_edges_subiso(int * g_full_in,
                            int * g_sub_in,
                            int * g_label_in, 
                            int * g_skip, int g_n,
                            int * possible_edge_out) nogil

     int which_edges_subiso_labeled(int * g_full_in,
                                    int * g_sub_in,
                                    int * g_label_in, 
                                    int * g_skip, int g_n,
                                    int * possible_weights, 
                                    int possible_weight_n, 
                                    int * possible_edge_out, float max_time_sec) nogil

# cdef extern from "vf3lib.h" namespace "vf3":
#      int subiso_vf3_weighted(int *, int *, int,
#                           int *, int *, int, 
#                           int *, int *)

# cdef extern from "bgllib.h" namespace "bgl":
#      int subiso_weighted(int *, int *, int,
#                          int *, int *, int, 
#                          int *, int *)

#      int bgl_which_edges_subiso_labeled(int * g_full_in,
#                                     int * g_sub_in,
#                                     int * g_label_in, 
#                                     int * g_skip, int g_n,
#                                     int * possible_weights, 
#                                     int possible_weight_n, 
#                                     int * possible_edge_out, float max_time_sec) nogil



def lemonmatch_test():
    x = np.arange(16).astype(np.float32)

    cdef float[::1] arr_memview = x
    numpy_test(&arr_memview[0], 4)

def lemon_subiso_vf2(int[:, :] gsub_adj, int[:] gsub_label, 
                     int[:, :] gmain_adj, int[:] gmain_label, 
                     multiple_edges=False, weighted_edges=False, 
                     max_run_sec=10.0):

    
    cdef int d = gmain_adj.shape[0] 
    cdef int[:] out = np.zeros(d, dtype=np.int32)

    cdef int out_size = 0; 

    
    wasiso=  subiso_vf2_weighted(&gsub_adj[0, 0], 
                                 &gsub_label[0], len(gsub_adj), 
                                 &gmain_adj[0, 0], &gmain_label[0], 
                                 len(gmain_adj), 
                                 &out[0], &out_size, max_run_sec)
    return wasiso, np.array(out[:out_size])


def py_which_edges_subiso(int[:, :] g_full_in, int[:, :] g_sub_in, 
                       int[:] g_label_in, 
                       int[:,:] g_skip):

    N = g_full_in.shape[0]
    possible_out = np.zeros((N, N), dtype=np.int32)
    
    cdef int[:, :] po = possible_out
    r = which_edges_subiso(&g_full_in[0, 0], 
                           &g_sub_in[0, 0], 
                           &g_label_in[0], 
                           &g_skip[0,0], 
                           N, 
                           &po[0,0])
    return possible_out


def py_which_edges_subiso_labeled(int[:, :] g_full_in, int[:, :] g_sub_in, 
                                  int[:] g_label_in, 
                                  int[:,:, :] g_skip, 
                                  int[:] g_possible_weights,
                                  float max_run_sec=0.0):

    N = g_full_in.shape[0]
    PW = len(g_possible_weights)
    possible_out = np.zeros((N, N, PW), dtype=np.int32)
    
    cdef int[:, :, :] po = possible_out
    with nogil:
        r = which_edges_subiso_labeled(&g_full_in[0, 0], 
                                       &g_sub_in[0, 0], 
                                       &g_label_in[0], 
                                       &g_skip[0,0, 0], 
                                       N, 
                                       &g_possible_weights[0], 
                                       PW,
                                       &po[0,0, 0], max_run_sec)
    if r == -1:
        raise RuntimeError("Ran over time")
    return possible_out

# @cython.boundscheck(False)  # Deactivate bounds checking
# @cython.wraparound(False) 
# cdef _random_distinct_int(int N, int m, int small=1):
#     """
#     Return m distinct integers from the range 0 to N-1
    
#     Note if small we assume m << N
    
#     """
#     cdef int[:] out = np.empty(m, dtype=np.int32)
#     out[:] = -1
#     cdef int c
#     if small:
#         # fast path
#         for i in range(m):
#             c = np.random.randint(N)
#             if i == 0:
#                 out[i] = c
#             else:
#                 found_unique = False
#                 while not found_unique:
#                     no_match = True
#                     for j in range(i):
#                         if out[j] == c:
#                             c = np.random.randint(N)
#                             no_match = False
#                             break
#                     if no_match:
#                         found_unique=True
#                 out[i] = c
#         return out 
#     else:        
#         return np.random.permutation(N)[:m].astype(np.int32)


# @cython.boundscheck(False)  # Deactivate bounds checking
# @cython.wraparound(False) 
# cdef edge_count_list(int[:, :] input_list, 
#                      int[:, :] to_find):
#     """
#     for each edge in to_find, how many times does it occur
#     in input_list? 

#     UNDIRECTED
#     """
    
#     assert input_list.shape[1] == 2
#     assert to_find.shape[1] == 2

#     cdef int[:] counts = np.zeros(len(to_find), dtype=np.int32)
#     for e1_i in range(len(input_list)):
#         e1 = input_list[e1_i]
#         for e2_i in range(len(to_find)):
#             e2 = to_find[e2_i]
#             if e1 == e2 or ((e1[0] == e2[1] ) and (e1[1] == e2[0])):
#                 counts[e2_i] += 1
#     return counts



# @cython.boundscheck(False)  # Deactivate bounds checking
# @cython.wraparound(False) 
# cpdef _vert_labeled_mcmc_multi_edge_swap(int [:, :] edge_array, 
#                                          int max_multi, 
#                                          _debug_force_sel_edges = (-1, -1)):
#     """
#     numba-jitable version of mcmc edge swap operation
    
#     Do not swap if you would create a pair of vertices with more than
#     max_multi edges between them 

#     edge_array is a N x 2 array of integer-valued edge tuples
#     in no required order

#     e_idx_1 / e_idx_2 are for testing! 
#     """
#     EDGE_N = edge_array.shape[0]
#     #edge_out = edge_array.copy()
#     DO_NOTHING = -1, -1, (0, 0), (0, 0)

#     cdef int e_idx_1, e_idx_2

#     if _debug_force_sel_edges == (-1, -1):
#         e_idx_1, e_idx_2 = _random_distinct_int(EDGE_N, 2)
#     else:
#         e_idx_1, e_idx_2 = _debug_force_sel_edges

#     cdef int[2] e_1
#     e_1[0] =  edge_array[e_idx_1, 0]
#     e_1[1] = edge_array[e_idx_1, 1]

#     cdef int[2] e_2
#     e_2[0] = edge_array[e_idx_2, 0]
#     e_2[1] = edge_array[e_idx_2, 1]

#     if np.random.rand() < 0.5:
#         a = e_1[0]
#         e_1[0] = e_1[1]
#         e_1[1] = a

#     cdef int u, v
#     u = e_1[0]
#     v = e_1[1]

#     cdef int x, y
#     x = e_2[0]
#     y = e_2[1]

#     # check for loops, and then return
#     if (u ==x):
#         return DO_NOTHING
#     if (v == y):
#         return DO_NOTHING
#     if ((u==v) and (x==y)) or ((u == y) and (x==v)):# (u, x), (v, y)):
#         return DO_NOTHING

#     # compute counts
#     # w_uv = graphutil.count_same_edges(new_edge_k, (u, v))
#     # w_xy = graphutil.count_same_edges(new_edge_k, (x, y))
#     # w_ux = graphutil.count_same_edges(new_edge_k, (u, x))
#     # w_vy = graphutil.count_same_edges(new_edge_k, (v, y))
#     cdef int[:, :] testarray = np.array([(u, v), 
#                                          (x, y), 
#                                          (u, x), 
#                                          (v, y)], dtype=np.int32)

#     cdef int w_uv, w_xy, w_ux, w_vy
#     cdef int[:] result =  edge_count_list(edge_array, testarray)

#     w_uv = result[0]
#     w_xy = result[1]
#     w_ux = result[2]
#     w_vy = result[3]

#     # #print(u, v, x, y, type(u), type(v), type(x), type(y))
#     # check maximum number of multiedges
#     if w_ux >= max_multi or w_vy >= max_multi:
#         return DO_NOTHING

#     cdef float swaps_from, swaps_to
#     unique = np.unique(np.array([x, y, u, v]))
#     unique_n = len(unique)
#     if unique_n == 4:
#         swaps_to = w_uv * w_xy
#         swaps_from = (w_ux+1)*(w_vy+1)
#     elif unique_n == 3:
#         if u == v or x == y:
#             swaps_to = 2 * w_uv * w_xy
#             swaps_from = (w_ux + 1)*(w_vy + 1)
#         else:
#             swaps_to =  w_uv * w_xy
#             swaps_from = 2*(w_ux + 1)*(w_vy + 1)    
#     elif unique_n == 2:
#         # none are self-loops because IT IS FORBIDDEN
#         # raise Exception("how did we get here", unique, (u, v), (x, y))
        
#         # FIXME should we except here
#         pass
#     else: 
#         return DO_NOTHING

#     ## old method
#     # if do_nothing:
#     #     pass
#     # else:
#     #     P = min(1, float(swaps_from)/swaps_to)
#     #     if np.random.rand() < P:
#     #         edge_out[e_idx_1] = (u, x)
#     #         edge_out[e_idx_2] = (v, y)

#     # return edge_out
 
#     if swaps_to == 0.0:
#         swaps_to = 0.00001
#     P = min(1, float(swaps_from)/swaps_to)
#     if np.random.rand() < P:
#         return e_idx_1, e_idx_2, (u, x), (v, y)
#     return DO_NOTHING




# def subiso_vf3(int[:, :] gsub_adj, int[:] gsub_label, 
#                int[:, :] gmain_adj, int[:] gmain_label, 
#                multiple_edges=False, weighted_edges=False):

    
#     cdef int d = gmain_adj.shape[0] 
#     cdef int[:] out = np.zeros(d, dtype=np.int32)

#     cdef int out_size = 0; 

#     assert multiple_edges == False
#     assert weighted_edges == True
    
#     print("calling subiso_vf3_weighted")
#     wasiso=  subiso_vf3_weighted(&gsub_adj[0, 0], 
#                                  &gsub_label[0], len(gsub_adj), 
#                                  &gmain_adj[0, 0], &gmain_label[0], 
#                                  len(gmain_adj), 
#                                  &out[0], &out_size)
#     return wasiso, np.array([]) # np.array(out[:out_size])


# def subiso_bgl(int[:, :] gsub_adj, int[:] gsub_label, 
#                int[:, :] gmain_adj, int[:] gmain_label, 
#                multiple_edges=False, weighted_edges=False):

    
#     cdef int d = gmain_adj.shape[0] 
#     cdef int[:] out = np.zeros(d, dtype=np.int32)

#     cdef int out_size = 0; 

#     assert multiple_edges == False
#     assert weighted_edges == True
    
#     wasiso=  subiso_weighted(&gsub_adj[0, 0], 
#                              &gsub_label[0], len(gsub_adj), 
#                              &gmain_adj[0, 0], &gmain_label[0], 
#                              len(gmain_adj), 
#                              &out[0], &out_size)
#     return wasiso, np.array([]) # np.array(out[:out_size])

# def py_bgl_which_edges_subiso_labeled(int[:, :] g_full_in, int[:, :] g_sub_in, 
#                                   int[:] g_label_in, 
#                                   int[:,:] g_skip, 
#                                   int[:] g_possible_weights,
#                                   float max_run_sec=0.0):

#     N = g_full_in.shape[0]
#     PW = len(g_possible_weights)
#     possible_out = np.zeros((N, N, PW), dtype=np.int32)
    
#     cdef int[:, :, :] po = possible_out
#     r = bgl_which_edges_subiso_labeled(&g_full_in[0, 0], 
#                                    &g_sub_in[0, 0], 
#                                    &g_label_in[0], 
#                                    &g_skip[0,0], 
#                                    N, 
#                                    &g_possible_weights[0], 
#                                    PW,
#                                    &po[0,0, 0], max_run_sec)
#     if r == -1:
#         raise RuntimeError("Ran over time")
#     return possible_out
