import numpy as np
import networkx as nx


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

