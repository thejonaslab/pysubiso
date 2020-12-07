import gzip
import time
import pickle

import numpy as np
import networkx as nx
import pytest

import pysubiso
from pysubiso.util import * 


MATCHERS = ['ri', 'NX']


@pytest.mark.parametrize('matcher', MATCHERS)
def test_iso_same(matcher):
    # X is to itself
    x = np.zeros((3, 3), np.int32)
    c = np.zeros(3, np.int32)

    x[0, 1] = 1
    x[1, 2] = 1
    x = x + x.T

    m = pysubiso.create_match(matcher)
    assert m.is_iso(x, c, x, c)

def random_graph_small(graph_size=20, node_colors = [1, 2, 5],
                       edge_colors = [1, 2, 4]):

    graph_size = np.random.randint(1, graph_size)
    node_color_n = np.random.choice(node_colors + [graph_size])
    edge_color_n = np.random.choice(edge_colors)
                
    g = nx_random_graph(graph_size, node_color_n, edge_color_n)
    return g

def permute_graph(adj, c):
    idx =np.random.permutation(adj.shape[0])    

    adj_perm = adj[idx]
    adj_perm = adj_perm[:, idx]
    c_perm = c[idx]
    return adj_perm, c_perm

@pytest.mark.parametrize('matcher', MATCHERS)
def test_iso_simple(matcher):
    """
    Create a graph and permute its nodes and edges
    """
    np.random.seed(0)
    g = random_graph_small()
    g_adj, g_color = nx_to_adj(g)


    g_perm_adj, g_perm_color = permute_graph(g_adj, g_color)

    m = pysubiso.create_match(matcher)
    assert m.is_iso(g_adj, g_color, g_perm_adj, g_perm_color)

@pytest.mark.parametrize('matcher', MATCHERS)
def test_iso_removed(matcher):
    """
    Create a graph and remove (nodes, edges)
    """

    m = pysubiso.create_match(matcher)
    
    np.random.seed(0)
    g = random_graph_small()
    for e in g.edges(data=True):
        print(e)
    g_adj, g_color = nx_to_adj(g)

    g_perm = nx_permute(g)
    g_perm.remove_node(np.random.choice(g_perm.nodes))
    g_perm = nx_canonicalize_nodes(g_perm)
    
    g_new_adj, g_new_color = nx_to_adj(g_perm)
    assert not m.is_iso(g_adj, g_color, g_new_adj, g_new_color)

    g_perm = g.copy() #nx_permute(g)
    e = list(g_perm.edges)[0] # np.random.permutation(g_perm.edges)[0]
    print(g_perm.edges[e[0], e[1]])
    e1 = list(g_perm.edges)[1] # np.random.permutation(g_perm.edges)[0]
    print("removing", e)
    print(len(g_perm.edges))
    g_perm.remove_edge(e[0], e[1])
    g_perm.remove_edge(e1[0], e1[1])
    print(len(g_perm.edges))
    
    g_new_adj, g_new_color = nx_to_adj(g_perm)
    print(g_new_adj)
    print(nx_to_adj(g)[0] - nx_to_adj(g_perm)[0])
    
    assert not m.is_iso(g_adj, g_color, g_new_adj, g_new_color)

