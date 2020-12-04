import gzip
import time
import pickle

import numpy as np
import networkx as nx
import pytest

import pysubiso

MATCHERS = ['RI']


def nx_random_graph(N, node_color_n, edge_color_n):
    """
    Generate a random graph of N nodes with the indicated edge colors
    and node colors

    """

    g = nx.generators.random_graphs.fast_gnp_random_graph(N, 0.3, seed=0, directed=False)
    v_colors = np.random.randint(node_color_n, size=N)
    e_colors = np.random.randint(edge_color_n, size=len(g.edges))

    for n in g.nodes:
        g.nodes[n]['color'] = v_colors[n]
    for i, (n1, n2) in enumerate(g.edges):
        g.edges[n1, n2]['color'] = e_colors[i]
        
    return g

def nx_to_adj(g):
    node_order = np.arange(len(g.nodes))
    adj = nx.to_numpy_array(g, dtype=np.int32,
                            weight='color', nodelist = node_order)
    color = np.array([g.nodes[n]['color'] for n in node_order], dtype=np.int32)
    return adj, color

def nx_permute(g):
    mapping = {i: v for i, v in enumerate(np.random.permutation(len(g.nodes)))}
    g2 = nx.relabel_nodes(g, mapping)
    return g2

def nx_random_subgraph(g, n):
    
    tgt_nodes = np.random.permutation(len(g.nodes))[:n]
    gs = nx.subgraph(g, tgt_nodes)
    for n in gs.nodes:
         gs.nodes[n]['old_id'] = n
    mapping = {k: i for i,k in enumerate(tgt_nodes)}
    return nx.relabel_nodes(gs, mapping)


@pytest.mark.parametrize('matcher', MATCHERS)
def test_indsubiso_simple(matcher):
    # X is subiso to itself
    x = np.zeros((3, 3), np.int32)
    c = np.zeros(3, np.int32)

    x[0, 1] = 1
    x[1, 2] = 1
    x = x + x.T

    m = pysubiso.create_match(matcher)
    assert m.is_indsubiso(x, c, x, c)

@pytest.mark.parametrize('matcher', MATCHERS)
def test_indsubiso_simple_edgedel(matcher):
    # subgraph is subiso, but not the other way
    x = np.zeros((3, 3), np.int32)
    c = np.zeros(3, np.int32)
    x[0, 1] = 1
    x[1, 2] = 1
    x = x + x.T

    y = np.zeros((3, 3), np.int32)
    c = np.zeros(3, np.int32)
    y[0, 1] = 1
    y = y + y.T
    m = pysubiso.create_match(matcher)

    assert m.is_indsubiso(y, c, x, c)
    assert not m.is_indsubiso(x, c, y, c)
    
@pytest.mark.parametrize('matcher', MATCHERS)
def test_indsubiso_del_edges(matcher):

    m = pysubiso.create_match(matcher)
    np.random.seed(0)
    
    for _ in range(1000):
        graph_size = np.random.randint(1, 20)
        node_color_n = np.random.choice([1, 2, 5, graph_size])
        edge_color_n = np.random.choice([1, 2, 4])
                
        g = nx_random_graph(graph_size, node_color_n, edge_color_n)    
        g_adj, g_color = nx_to_adj(g)

        g_perm = nx_permute(g)
        for n in range(1, len(g_perm.nodes)):

            g_sub = nx_random_subgraph(g_perm, n)

            g_sub_adj, g_sub_color = nx_to_adj(g)
            assert m.is_indsubiso(g_sub_adj, g_sub_color,
                                  g_adj, g_color)

@pytest.mark.xfail
@pytest.mark.parametrize('matcher', MATCHERS)
def test_timeout(matcher):
    m = pysubiso.create_match(matcher)
    np.random.seed(0)

    graph_size = 1000
    node_color_n = 3
    edge_color_n = 4
    
    g = nx_random_graph(graph_size, node_color_n, edge_color_n)    
    g_adj, g_color = nx_to_adj(g)

    g_perm = nx_permute(g)
    g_sub = nx_random_subgraph(g_perm, 980)
    g_sub_adj, g_sub_color = nx_to_adj(g)

    with pytest.raises(pysubiso.TimeoutError):
        m.is_indsubiso(g_sub_adj, g_sub_color,
                       g_adj, g_color, 0.001)    
    

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
#     pysubiso.c_which_edges_subiso_labeled(y, c, x, c, poss_edges, 1.0)
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
#         assert res == pysubiso.c_is_subiso(sub_adj, sub_c, main_adj, main_c, 10.0), test_ix

# def test_c_which_edges_subiso_labeled_2():
#     x = np.zeros((3, 3), np.int32)
#     c = np.zeros(3, np.int32)
#     x[0, 1] = 1
#     x[1, 2] = 1
#     x[0, 2] = 1
#     x = x + x.T

#     poss_edges = np.zeros_like(x)
#     pysubiso.c_which_edges_subiso_labeled(x, c, x, c, poss_edges, 1.0)
#     assert np.sum(poss_edges) == 0

# def test_c_which_edges_subiso_labeled_3():
#     x = np.zeros((3, 3), np.int32)
#     c = np.zeros(3, np.int32)
#     x[0, 1] = 1
#     x[1, 2] = 1
#     x = x + x.T

#     poss_edges = np.zeros_like(x)
#     pysubiso.c_which_edges_subiso_labeled(x, c, x, c, poss_edges, 1.0)
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
#     assert pysubiso.c_is_subiso(main_adj, c_main, main_adj, c_main, 1.0)

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

#     assert pysubiso.c_is_subiso(sub_adj, c_main, main_adj, c_main, 1.0)
#     assert not pysubiso.c_is_subiso(main_adj, c_main, sub_adj, c_main, 1.0)

#     poss_edges = np.zeros_like(sub_adj).astype(np.int32)
#     pysubiso.c_which_edges_subiso_labeled(sub_adj, c_main, main_adj, c_main, poss_edges, 1.0)
#     edges_to_add = []
#     for i in range(len(poss_edges)):
#         for j in range(i + 1, len(poss_edges)):
#             if poss_edges[i, j]:
#                 edges_to_add.append((i, j))
#     assert set(edges_to_del) == set(edges_to_add)


