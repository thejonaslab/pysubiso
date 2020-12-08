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
    possible_edge_colors = np.array([1, 2, 3])
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
    possible_edge_colors = np.array([1, 2, 3])
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

@pytest.mark.parametrize('node_color_n', [1, 2, 3, 5, 8])
@pytest.mark.parametrize('edge_color_n', [1, 2, 4, 8])
@pytest.mark.parametrize('copies', [1, 2, 3, 4])
def test_get_color_edge_possible_graph_gen(node_color_n, edge_color_n, copies):
    """
    Create graphs that will have a specific nodetype-edgetype stats by 
    construction. 

    """
    np.random.seed(0)
    for iters in range(10):
        node_color_n = 4
        edge_color_n = 6

        possible_edge_colors = np.arange(edge_color_n) + 1
        possible_node_colors = np.arange(node_color_n)

        G = nx.Graph()
        npos = 0
        copies = 8
        for i in range(copies):
            for nc in possible_node_colors:
                G.add_node(npos, color=nc)
                npos += 1

        nc_ec_stats = np.zeros((node_color_n, node_color_n, edge_color_n+1), dtype=np.int32)
        for i in range(node_color_n):
            for j in range(i+1, node_color_n):
                for ec in range(1, edge_color_n + 1):
                    nc_ec_stats[i, j, ec] = np.random.poisson(0.5)

                    nc_ec_stats[j, i, ec] = nc_ec_stats[i, j, ec]
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

                            unconnected = set([(n, new_node_id) for p in nc_i_nodes])


                        j= np.random.randint(0, len(unconnected))
                        tgt_pair = list(unconnected)[j]
                        print('adding edge between node colors', nc_i, nc_j, "with color=", ec) 
                        G.add_edge(tgt_pair[0], tgt_pair[1], color=ec)




        g_adj, g_color = pysubiso.util.nx_to_adj(G)
        possible_table = pysubiso.get_color_edge_possible_table(g_adj, g_color, possible_edge_colors)
        compare_node_edge_tables(possible_table, nc_ec_stats)


