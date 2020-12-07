import numpy as np
import networkx as nx
import tarfile
import os

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
    """
    Convert a networkx graph to adj matrix and node colors
    """
    node_order = np.arange(len(g.nodes))
    adj = nx.to_numpy_array(g, dtype=np.int32,
                            weight='color', nodelist = node_order)
    color = np.array([g.nodes[n]['color'] for n in node_order], dtype=np.int32)
    return adj, color

def nx_permute(g):
    """
    Permute the ordering and labeling of nodes in a networkx graph g
    """
    mapping = {i: v for i, v in enumerate(np.random.permutation(len(g.nodes)))}
    g2 = nx.relabel_nodes(g, mapping)
    return g2

def nx_canonicalize_nodes(g):
    """
    returns the nodes with labels 0... N-1

    """
    mapping = {v: i for i,v  in enumerate(g.nodes)}
    g_clean = nx.relabel_nodes(g, mapping)
    return g_clean

def nx_random_subgraph(g, n):
    """
    Randomly delete all but n nodes from g. Returns new relabeled graph
    Note that original node id is stored in attribute old_id
    """
    tgt_nodes = np.random.permutation(len(g.nodes))[:n]
    gs = nx.subgraph(g, tgt_nodes)
    for n in gs.nodes:
         gs.nodes[n]['old_id'] = n
    mapping = {k: i for i,k in enumerate(tgt_nodes)}
    return nx.relabel_nodes(gs, mapping)

def nx_random_edge_del(g, n):
    """
    Randomly delete N - n nodes from g. Returns new graph
    Note that original node id is stored in attribute old_id
    """

    g = g.copy()
    N = len(g.edges)
    assert n <= N
    tgt_edges = np.random.permutation(g.edges)[:N - n]
    g.remove_edges_from(tgt_edges)
    return g

def adj_colors_to_nx_graph(adj, colors):
    
    G = nx.convert_matrix.from_numpy_matrix(adj)
    for c, n in zip(colors, G.nodes):
        G.nodes[n]['color'] = c
    for e in G.edges:
        G.edges[e[0], e[1]]['color'] = G.edges[e[0], e[1]]['weight']
        del G.edges[e[0], e[1]]['weight']
    return G


def read_graphml_tgz_data(filename, max_num = -1):
    """
    Helper function to read our data files, which are gzipped
    with a graph, subgraph pair in each directory, as
    graphml files. 

    returns g_adj, g_color, g_sub_adj, g_sub_color

    Note we don't keep the number/type of possible next 
    edges anywhere, and it is dataset-dependent
    """

    tf_load = tarfile.open(filename, mode='r:gz') 
    n = tf_load.getnames()
    if max_num > 0:
        n = n[:max_num]

    pairs = [os.path.dirname(s) for s in n]
    for p in pairs:
        main = tf_load.extractfile(p + "/main.graphml").read()
        sub = tf_load.extractfile(p + "/sub.graphml").read()
        g_main = nx.parse_graphml(main, node_type=int)
        g_sub = nx.parse_graphml(sub, node_type=int)

        g_adj, g_color = nx_to_adj(g_main)

        g_sub_adj, g_sub_color = nx_to_adj(g_sub)

        yield g_adj, g_color, g_sub_adj, g_sub_color
