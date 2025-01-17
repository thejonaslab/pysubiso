import gzip
import time
import pickle

import numpy as np
import networkx as nx
import pytest

import pysubiso
from pysubiso.util import * 


MATCHERS = ['RI', 'lemon']


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
def test_indsubiso_simple_colors(matcher):
    """
    does A-A match B-B

    """
    x = np.zeros((3, 3), np.int32)
    c1 = np.zeros(3, np.int32)
    c2 = np.ones(3, np.int32)
    x[0, 1] = 1
    x[1, 2] = 1
    x = x + x.T

    m = pysubiso.create_match(matcher)

    assert m.is_indsubiso(x, c1, x, c1)
    assert not m.is_indsubiso(x, c1, x, c2)

    x2 = np.zeros((3, 3), np.int32)
    x2[0, 1] = 2
    x2[1, 2] = 2
    x2 = x2 + x2.T


    assert not m.is_indsubiso(x, c1, x2, c1)

def random_graph_small(graph_size=20, node_colors = [1, 2, 5],
                       edge_colors = [1, 2, 4]):

    graph_size = np.random.randint(1, graph_size)
    node_color_n = np.random.choice(node_colors + [graph_size])
    edge_color_n = np.random.choice(edge_colors)
                
    g = nx_random_graph(graph_size, node_color_n, edge_color_n)
    return g

        
@pytest.mark.parametrize('matcher', MATCHERS)
def test_indsubiso_random_del(matcher):
    """
    Generate random graphs that should be indsubiso
    by deleting subsets of nodes, edges
    
    """
    m = pysubiso.create_match(matcher)
    np.random.seed(0)
    
    for _ in range(1000):
                
        g = random_graph_small()
        g_adj, g_color = nx_to_adj(g)

        g_perm = nx_permute(g)

        ## randomly delete nodes
        for n in range(1, len(g_perm.nodes)):

            g_sub = nx_random_subgraph(g_perm, n)

            g_sub_adj, g_sub_color = nx_to_adj(g_sub)
            assert m.is_indsubiso(g_sub_adj, g_sub_color,
                                  g_adj, g_color)
        ## randomly delete edges
        for n in range(1, len(g_perm.edges)):

            g_sub = nx_random_edge_del(g_perm, n)

            g_sub_adj, g_sub_color = nx_to_adj(g_sub)
            try:
                assert m.is_indsubiso(g_sub_adj, g_sub_color,
                                      g_adj, g_color)
            except pysubiso.TimeoutError as e:
                pass
            

# def test_indsubiso_data_suite(matcher='RI'):

#     m = pysubiso.create_match(matcher)

#     with gzip.open('data/hardgraphs.pickle.gz', 'rb') as fp:
#         test_cases = pickle.load(fp)
#     for test_ix, test_case in enumerate(test_cases):
#         main_adj = test_case['main_adj'].astype(np.int32)
#         sub_adj = test_case['sub_adj'].astype(np.int32)
#         main_c = test_case['main_c']
#         sub_c = test_case['sub_c']
#         res = test_case['is_subiso']
#         t1 = time.time()
#         assert res == m.is_indsubiso(sub_adj, sub_c, main_adj, main_c, 0.1), test_ix
#         # t2 = time.time()
#         # runtime = t2-t1
#         # if runtime > 0.001:
#         #     print(test_ix, runtime)            
#         #     res == m.is_indsubiso(sub_adj, sub_c, main_adj, main_c, 0.001)


            

## Timeout is incredibly hard to check because the
## pathological cases are so different between algorithms
# @pytest.mark.xfail
# @pytest.mark.parametrize('matcher', MATCHERS)
# def test_timeout(matcher):
#     m = pysubiso.create_match(matcher)
#     np.random.seed(0)

#     graph_size = 1000
#     node_color_n = 2
#     edge_color_n = 1
    
#     g = nx_random_graph(graph_size, node_color_n, edge_color_n)    
#     g_adj, g_color = nx_to_adj(g)

#     g_perm = nx_permute(g)
#     g_sub = nx_random_subgraph(g_perm, graph_size - 10)
#     g_sub = nx_random_edge_del(g_sub, 50)
#     g_sub_adj, g_sub_color = nx_to_adj(g)

#     with pytest.raises(pysubiso.TimeoutError):
#         m.is_indsubiso(g_sub_adj, g_sub_color,
#                        g_adj, g_color, 0.001)    


@pytest.mark.parametrize('matcher', MATCHERS)
def test_simple_edge_add_indsubiso(matcher):
    x = np.zeros((3, 3), np.int32)
    x_c = np.zeros(3, np.int32)
    x[0, 1] = 1
    x[1, 2] = 1
    x = x + x.T

    y = np.zeros((3, 3), np.int32)
    y_c = np.zeros(3, np.int32)
    y[0, 1] = 1
    y = y + y.T

        
    m = pysubiso.create_match(matcher)
    assert m.is_indsubiso(y, y_c, x, x_c)

    candidate_edges = np.array([[0, 2, 1],
                                [1, 2, 1]], dtype=np.int32)
    
    valid_indsubiso = m.edge_add_indsubiso(y, y_c, x, x_c, candidate_edges, 1.0)
    assert valid_indsubiso[0]
    assert valid_indsubiso[1]


@pytest.mark.parametrize('matcher', MATCHERS)
def test_edge_add_indsubiso_random_suite(matcher):
    """
    Generate random graphs, remove random subsets of edges, 
    check if results subiso. Compares against manual 
    invocation of matcher. 
    
    """


    m = pysubiso.create_match(matcher)
    np.random.seed(0)
    
    for rand_instance_i in range(1000):
                
        g = random_graph_small()
        g_adj, g_color = nx_to_adj(g)

        g_perm = nx_permute(g)
        to_del = np.random.randint(0, len(g_perm.edges)+1)
        g_sub = nx_random_edge_del(g_perm, to_del)
        g_sub_adj, g_sub_color = nx_to_adj(g_sub)

        candidate_edges =  pysubiso.gen_possible_next_edges(g_sub_adj,
                                                   np.arange(1, np.max(g_color)+1,
                                                   dtype=np.int32))
        if len(candidate_edges) == 0:
            continue

        valid_indsubiso = m.edge_add_indsubiso(g_sub_adj, g_sub_color,
                                               g_adj, g_color,
                                               candidate_edges, 10.0)
        assert valid_indsubiso.shape[0] == candidate_edges.shape[0]
        for res, (i, j, c) in zip(valid_indsubiso, candidate_edges):
            a = g_sub_adj.copy()
            a[i, j] = c
            a[j, i] = c
            manual_res =  m.is_indsubiso(a, g_sub_color, g_adj, g_color)
            # print(rand_instance_i, ":", "edge_i=", i, "edge_j=", j, "edge_c=", c,
            #       "res=", res, "manual res=", manual_res)
            assert res == manual_res

#@pytest.mark.xfail
@pytest.mark.parametrize('matcher', MATCHERS)
def test_edge_add_indsubiso_timeout(matcher):
    """
    Generate a very large graph we know will timeout
    and check that the exception is raised
    """
    m = pysubiso.create_match(matcher)
    np.random.seed(0)

    graph_size = 80
    node_color_n = 2
    edge_color_n = 1
    
    g = nx_random_graph(graph_size, node_color_n, edge_color_n)    
    g_adj, g_color = nx_to_adj(g)

    g_perm = nx_permute(g)
    g_sub = nx_random_subgraph(g_perm, graph_size - 10)
    g_sub = nx_random_edge_del(g_sub, 5)
    g_sub_adj, g_sub_color = nx_to_adj(g_sub)

    candidate_edges = pysubiso.gen_possible_next_edges(g_sub_adj, g_sub_color)

    with pytest.raises(pysubiso.TimeoutError):
        valid_indsubiso = m.edge_add_indsubiso(g_sub_adj, g_sub_color,
                                               g_adj, g_color,
                                               candidate_edges, 0.1)



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


