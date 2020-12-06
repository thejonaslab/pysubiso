import gzip
import time
import pickle

import numpy as np
import networkx as nx
import pytest

import pysubiso
from pysubiso.util import * 


MATCHERS = ['RI', 'lemon']


def random_graph_small(graph_size=20, node_colors = [1, 2, 5],
                       edge_colors = [1, 2, 4]):

    graph_size = np.random.randint(1, graph_size)
    node_color_n = np.random.choice(node_colors + [graph_size])
    edge_color_n = np.random.choice(edge_colors)
                
    g = nx_random_graph(graph_size, node_color_n, edge_color_n)
    return g

        

def test_edge_add_indsubiso_random_suite():
    """
    Generate random graphs, remove random subsets of edges, 
    check if results subiso. Compares against manual 
    invocation of matcher. 
    
    """


    matchers = {m : pysubiso.create_match(m) for m in MATCHERS}
    
    np.random.seed(0)
    
    for _ in range(1000):
                
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

        results = []
        for m_name, m in matchers.items():
            
            valid_indsubiso = m.edge_add_indsubiso(g_sub_adj, g_sub_color,
                                                   g_adj, g_color,
                                                   candidate_edges, 10.0)
            assert valid_indsubiso.shape[0] == candidate_edges.shape[0]
            for res, (i, j, c) in zip(valid_indsubiso, candidate_edges):
                a = g_sub_adj.copy()
                a[i, j] = c
                assert res == m.is_indsubiso(a, g_sub_color, g_adj, g_color)
            
            results.append(valid_indsubiso)

        results = np.vstack(results).T

        was_correct = results[:, 0][:, np.newaxis] == results
        
        assert was_correct.all(), str(results)
        
        
