import gzip
import time
import pickle

import numpy as np
import networkx as nx
from tqdm import tqdm

import pysubiso

def test_c_is_subiso_1():
    # X is subiso to itself
    x = np.zeros((3, 3), np.int32)
    c = np.zeros(3, np.int32)

    x[0, 1] = 1
    x[1, 2] = 1
    x = x + x.T

    assert pysubiso.c_is_subiso(x, c, x, c, 1.0)

# def test_c_is_subiso_2():
#     # subgraph is subiso, but not the other way
#     x = np.zeros((3, 3), np.int32)
#     c = np.zeros(3, np.int32)
#     x[0, 1] = 1
#     x[1, 2] = 1
#     x = x + x.T

#     y = np.zeros((3, 3), np.int32)
#     c = np.zeros(3, np.int32)
#     y[0, 1] = 1
#     y = y + y.T

#     assert riwrapper.c_is_subiso(y, c, x, c, 1.0)
#     assert not riwrapper.c_is_subiso(x, c, y, c, 1.0)

# def test_c_is_subiso_3():
#     # randomly generated subgraph w/ unique node labels
#     n_sub_nodes = 20
#     n_main_nodes = 40
#     np.random.seed(0)
#     g = nx.generators.random_graphs.fast_gnp_random_graph(n_main_nodes, 0.3, seed=0, directed=False)
#     sub_adj = np.zeros((n_sub_nodes, n_sub_nodes), np.int32)
#     main_adj = np.zeros((n_main_nodes, n_main_nodes), np.int32)

#     for i in range(n_main_nodes):
#         for j in range(i + 1, n_main_nodes):
#             if (i, j) in g.edges:
#                 if i < n_sub_nodes and j < n_sub_nodes:
#                     sub_adj[i, j] = 1
#                 main_adj[i, j] = 1
#     sub_adj += sub_adj.T
#     main_adj += main_adj.T
#     c_sub = np.zeros(n_sub_nodes, np.int32)
#     c_main = np.zeros(n_main_nodes, np.int32)

#     assert np.allclose(sub_adj, main_adj[:n_sub_nodes, :n_sub_nodes])
#     assert riwrapper.c_is_subiso(sub_adj, c_sub, main_adj, c_main, 1.0)
#     assert not riwrapper.c_is_subiso(main_adj, c_main, sub_adj, c_sub, 1.0)

# def test_c_which_edges_subiso_labeled_1():
#     x = np.zeros((3, 3), np.int32)
#     c = np.zeros(3, np.int32)
#     x[0, 1] = 1
#     x[1, 2] = 1
#     x = x + x.T

#     y = np.zeros((3, 3), np.int32)
#     c = np.zeros(3, np.int32)
#     y[0, 1] = 1
#     y = y + y.T

#     poss_edges = np.zeros_like(x)
#     riwrapper.c_which_edges_subiso_labeled(y, c, x, c, poss_edges, 1.0)
#     assert int(np.sum(poss_edges) / 2) == 2
#     assert poss_edges[0, 2] == 1
#     assert poss_edges[1, 2] == 1

# def test_c_is_subiso_fullsuite():
#     with gzip.open('test.output.pickle.gz', 'rb') as fp:
#         test_cases = pickle.load(fp)
#     for test_ix, test_case in tqdm(enumerate(test_cases)):
#         main_adj = test_case['main_adj'].astype(np.int32)
#         sub_adj = test_case['sub_adj'].astype(np.int32)
#         main_c = test_case['main_c']
#         sub_c = test_case['sub_c']
#         res = test_case['is_subiso']
#         assert res == riwrapper.c_is_subiso(sub_adj, sub_c, main_adj, main_c, 10.0), test_ix

# def test_c_which_edges_subiso_labeled_2():
#     x = np.zeros((3, 3), np.int32)
#     c = np.zeros(3, np.int32)
#     x[0, 1] = 1
#     x[1, 2] = 1
#     x[0, 2] = 1
#     x = x + x.T

#     poss_edges = np.zeros_like(x)
#     riwrapper.c_which_edges_subiso_labeled(x, c, x, c, poss_edges, 1.0)
#     assert np.sum(poss_edges) == 0

# def test_c_which_edges_subiso_labeled_3():
#     x = np.zeros((3, 3), np.int32)
#     c = np.zeros(3, np.int32)
#     x[0, 1] = 1
#     x[1, 2] = 1
#     x = x + x.T

#     poss_edges = np.zeros_like(x)
#     riwrapper.c_which_edges_subiso_labeled(x, c, x, c, poss_edges, 1.0)
#     assert np.sum(poss_edges) == 0

# def test_c_which_edges_subiso_labeled_4():
#     # randomly generated graph w/ unique node labels
#     n_main_nodes = 40
#     np.random.seed(0)
#     g = nx.generators.random_graphs.fast_gnp_random_graph(n_main_nodes, 0.3, seed=0, directed=False)
#     main_adj = np.zeros((n_main_nodes, n_main_nodes), np.int32)
#     for i in range(n_main_nodes):
#         for j in range(i + 1, n_main_nodes):
#             if (i, j) in g.edges:
#                 main_adj[i, j] = 1
#     main_adj += main_adj.T
#     c_main = np.random.choice(range(3), size=n_main_nodes, replace=True).astype(np.int32)
#     assert riwrapper.c_is_subiso(main_adj, c_main, main_adj, c_main, 1.0)

#     n_edges_del = int(0.10 * len(g.edges))
#     sub_adj = np.copy(main_adj)
#     edges_to_del = [
#         list(g.edges)[i] for i in
#         np.random.choice(range(len(g.edges)), size=n_edges_del, replace=False)
#     ]
#     for edge in edges_to_del:
#         i, j = edge
#         sub_adj[i, j] = 0
#         sub_adj[j, i] = 0

#     assert riwrapper.c_is_subiso(sub_adj, c_main, main_adj, c_main, 1.0)
#     assert not riwrapper.c_is_subiso(main_adj, c_main, sub_adj, c_main, 1.0)

#     poss_edges = np.zeros_like(sub_adj).astype(np.int32)
#     riwrapper.c_which_edges_subiso_labeled(sub_adj, c_main, main_adj, c_main, poss_edges, 1.0)
#     edges_to_add = []
#     for i in range(len(poss_edges)):
#         for j in range(i + 1, len(poss_edges)):
#             if poss_edges[i, j]:
#                 edges_to_add.append((i, j))
#     assert set(edges_to_del) == set(edges_to_add)

