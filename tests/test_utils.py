import numpy as np

import pysubiso
import time
import itertools
import networkx as nx
import pytest

def reference_gen_possible_next_edges(adj, colors):
    """

    """
    out = []
    for i in range(adj.shape[0]):
        for j in range(i +1, adj.shape[1]):
            if adj[i, j] == 0:
                for c in colors:
                    out.append([i, j, c])
    return np.array(out, dtype=np.int32).reshape((len(out), 3))
    

def test_possible_next_edges():
    np.random.seed(10)

    # empty
    adj = np.zeros((31, 31), dtype=np.int32)
    possible_colors = np.array([1, 2, 3,4], dtype=np.int32)
    
    possible_edges = pysubiso.gen_possible_next_edges(adj, possible_colors)

    for N in [1, 5, 10, 20, 32, 64, 100]:
        for color_n in [1, 4, 10]:

            # color_n * 3 to generate sparsity
            adj = np.random.randint(color_n*3, size=(N,N)).astype(np.int32)
            adj[adj > color_n] = 0 

            adj = np.triu(adj, k=1)
            possible_colors =np.arange(color_n, dtype=np.int32) + 1

            t1 = time.time()
            possible_edges = pysubiso.gen_possible_next_edges(adj, possible_colors)
            t2 = time.time()
            correct =reference_gen_possible_next_edges(adj, possible_colors)
            t3 = time.time()

            old_time = t3-t2
            new_time = t2-t1
            print(f"{old_time/new_time:3.1f} times faster ({old_time*1e6:3.1f} us vs {new_time*1e6:3.1f} us)")

            np.testing.assert_array_equal(possible_edges, correct)


def test_get_color_edge_possible_table():
    """
    Simple manual sanity-preserving examples
    """

    # (node colors) -edge colors-
    
    # (0) -1- (1) -2- (2) -3- (3)
    
    adj = np.array([[0, 1, 0, 0],
                    [1, 0, 2, 0],
                    [0, 2, 0, 3],
                    [0, 0, 3, 0]], dtype=np.int32)
    node_colors = np.array([0, 1, 2, 3], dtype=np.int32)
    possible_edge_colors = np.array([1, 2, 3], dtype=np.int32)
    possible_node_colors = np.unique(node_colors)
    
    possible_table = pysubiso.get_color_edge_possible_table(adj, node_colors, possible_edge_colors)

    ans = np.zeros((np.max(node_colors) + 1, np.max(node_colors)+1, np.max(possible_edge_colors)+1), dtype=np.int32)
    ans[0, 1, 1] = 1
    ans[1, 0, 1] = 1
    ans[1, 2, 2] = 1
    ans[2, 1, 2] = 1
    ans[2, 3, 3] = 1
    ans[3, 2, 3] = 1

        
    compare_node_edge_tables(possible_table, ans)

    
    # (0) -1- (1) -2- (1) -3- (0)
    
    adj = np.array([[0, 1, 0, 0],
                    [1, 0, 2, 0],
                    [0, 2, 0, 3],
                    [0, 0, 3, 0]], dtype=np.int32)
    node_colors = np.array([0, 1, 1, 0], dtype=np.int32)
    possible_edge_colors = np.array([1, 2, 3], dtype=np.int32)
    possible_node_colors = np.unique(node_colors)
    
    possible_table = pysubiso.get_color_edge_possible_table(adj, node_colors, possible_edge_colors)

    ans = np.zeros((np.max(node_colors) + 1, np.max(node_colors)+1, np.max(possible_edge_colors)+1), dtype=np.int32)
    ans[0, 1, 1] = 1
    ans[1, 0, 1] = 1
    ans[1, 1, 2] = 1
    ans[0, 1, 3] = 1
    ans[1, 0, 3] = 1

    
    compare_node_edge_tables(possible_table, ans)
    

def sort_tuple(a):
    return tuple(sorted(a))

def compare_node_edge_tables(a, b):
    assert a.shape == b.shape
    for ec in range(a.shape[2]):
        np.testing.assert_array_equal(a[:, :, ec], b[:, :, ec], err_msg=f"error, ec={ec}")



def create_graph_specific_nodetype_edgetype_counts(node_color_n, edge_color_n, copies, nc_ec_stats):
    possible_edge_colors = np.arange(edge_color_n) + 1
    possible_node_colors = np.arange(node_color_n)

    G = nx.Graph()
    npos = 0
    for i in range(copies):
        for nc in possible_node_colors:
            G.add_node(npos, color=nc)
            npos += 1

    # random matrix

    for i in range(node_color_n):
        nc_i = possible_node_colors[i]
        for j in range(i, node_color_n):
            nc_j = possible_node_colors[j]
            for ec in possible_edge_colors:
                ##
                tgt_number = nc_ec_stats[nc_i, nc_j, ec] # there should be this many edges between nodes of this color and nodes of that color
                for _ in range(tgt_number):
                    nc_i_nodes = np.random.permutation([n for (n, d) in G.nodes(data=True) if d['color'] == nc_i])
                    nc_j_nodes = np.random.permutation([n for (n, d) in G.nodes(data=True) if d['color'] == nc_j])
                    unconnected = set([sort_tuple(p) for p in itertools.product(nc_i_nodes, nc_j_nodes)\
                                   if p not in G.edges])
                    if len(unconnected)  == 0:
                        ## if there are no disconnected nodes of this color, add a new one

                        new_node_id = len(G.nodes)
                        G.add_node(new_node_id, color=nc_j)

                        unconnected = set([(n, new_node_id) for n in nc_i_nodes])


                    j= np.random.randint(0, len(unconnected))
                    tgt_pair = list(unconnected)[j]

                    G.add_edge(tgt_pair[0], tgt_pair[1], color=ec)
    return G

def create_nc_ec_table(node_color_n, edge_color_n, lamb=0.5):
    nc_ec_stats = np.zeros((node_color_n, node_color_n, edge_color_n+1), dtype=np.int32)
    for i in range(node_color_n):
        for j in range(i+1, node_color_n):
            for ec in range(1, edge_color_n + 1):
                nc_ec_stats[i, j, ec] = np.random.poisson(lamb)

                nc_ec_stats[j, i, ec] = nc_ec_stats[i, j, ec]
    return nc_ec_stats
                                                   
@pytest.mark.parametrize('node_color_n', [1, 2, 3, 5, 8])
@pytest.mark.parametrize('edge_color_n', [1, 2, 4, 8])
@pytest.mark.parametrize('copies', [1, 2, 3, 4])
def test_get_color_edge_possible_graph_gen(node_color_n, edge_color_n, copies):
    """
    Create graphs that will have a specific nodetype-edgetype stats by 
    construction and then checks that we can recover those stats properly

    """
    np.random.seed(0)
    for iters in range(10):

        possible_edge_colors = np.arange(edge_color_n, dtype=np.int32) + 1
        possible_node_colors = np.arange(node_color_n, dtype=np.int32)

        
        nc_ec_stats = create_nc_ec_table(node_color_n, edge_color_n, 0.5)

        G = create_graph_specific_nodetype_edgetype_counts(node_color_n, edge_color_n,
                                                           copies, nc_ec_stats)

        g_adj, g_color = pysubiso.util.nx_to_adj(G)
        possible_table = pysubiso.get_color_edge_possible_table(g_adj, g_color, possible_edge_colors)
        compare_node_edge_tables(possible_table, nc_ec_stats)


@pytest.mark.parametrize('node_color_n', [1, 2, 3, 5, 8])
@pytest.mark.parametrize('edge_color_n', [1, 2, 4, 8])
@pytest.mark.parametrize('copies', [1, 2, 3, 4])
def test_candidate_edge_filtering(node_color_n, edge_color_n, copies):
    #################################################
    ## create random edge stats table
    #################################################
    np.random.seed(0)

    for _ in range(1):


        nc_ec_stats = create_nc_ec_table(node_color_n, edge_color_n, 0.5)

        #################################################
        ## create graph with associated nodecolor-edgecolor stats
        #################################################    
        G = create_graph_specific_nodetype_edgetype_counts(node_color_n, edge_color_n,
                                                           copies, nc_ec_stats)

        #################################################
        ## create a list of all possible candidate edges
        #################################################
        g_adj, g_colors = pysubiso.util.nx_to_adj(G)
        possible_edge_colors = np.arange(edge_color_n, dtype=np.int32) + 1

        candidate_edges = pysubiso.gen_possible_next_edges(g_adj, possible_edge_colors)
        for i, j, c in candidate_edges:
            assert j > i
            assert c> 0

        print(set((np.arange(edge_color_n)+1).tolist()))
        assert set(np.unique(candidate_edges[:, 2]) ).issubset(set(possible_edge_colors))

        #################################################
        ## filter the edges
        #################################################
        filtered_candidate_edges = pysubiso.filter_candidate_edges(np.zeros_like(g_adj), g_colors,
                                                                   g_adj, g_colors,
                                                                   possible_edge_colors , 
                                                                   candidate_edges)
        print(len(candidate_edges), "-->", len(filtered_candidate_edges))

        fce_set = set([tuple(c) for c in filtered_candidate_edges])
        for i, j, c in filtered_candidate_edges:
            assert j > i
            ec = g_adj[i,j]
            if ec ==  0:
                continue
            nc_0 = g_colors[i]
            nc_1 = g_colors[j]
            print(f"candidate from ({i}, color {nc_0})--{ec}--({j}, color {nc_1})")

            #################################################
            # check if this exists in G by brute force
            #################################################
            match = False
            for e0, e1, d in G.edges(data=True):
                tgt_nc_0 = g_colors[e0]
                tgt_nc_1 = g_colors[e1]
                tgt_ec = d['color']
                assert tgt_ec > 0
                if (tgt_nc_0, tgt_nc_1, tgt_ec) == (nc_0, nc_1, ec):
                    match=True

            if match:
                assert (i, j, c) in fce_set
            else:
                assert (i, j, c) not in fce_set


