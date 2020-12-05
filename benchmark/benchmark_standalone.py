
import networkx as nx
import pysubiso
import tarfile
from pysubiso import util
import os
import numpy as np
import time
import pickle

from tqdm import tqdm
import pandas as pd

def possible_edges(g, color_labels=[1, 2, 3, 4]):
    """


    """

    g_adj, g_color = util.nx_to_adj(g)

    out = []
    for i in range(g_adj.shape[0]):
        for j in range(i+1, g_adj.shape[1]):
            if g_adj[i, j] == 0:
                for c in color_labels:
                    out.append((i, j, c))
    return np.array(out, dtype=np.int32)


def run_exp(infiles, outfile, exp_name, ec, matcher, num, TIMEOUT):

    m = pysubiso.create_match(matcher)

    log = []
    
    for filename in infiles:
        tf_load = tarfile.open(filename, mode='r:gz') 
        n = tf_load.getnames()[:num]

        pairs = [os.path.dirname(s) for s in n]
        for p in tqdm(pairs):
            main = tf_load.extractfile(p + "/main.graphml").read()
            sub = tf_load.extractfile(p + "/sub.graphml").read()
            g_main = nx.parse_graphml(main, node_type=int)
            g_sub = nx.parse_graphml(sub, node_type=int)

            g_adj, g_color = util.nx_to_adj(g_main)

            g_sub_adj, g_sub_color = util.nx_to_adj(g_sub)
            if g_adj.shape[0] < 28:
                continue
            candidate_edges = possible_edges(g_sub)

            t1 = time.time()
            timeout = False
            try:
                valid_indsubiso = m.edge_add_indsubiso(g_sub_adj, g_sub_color,
                                                       g_adj, g_color,
                                                       candidate_edges, TIMEOUT)
            except:
                timeout = True
                pass
            t2 = time.time()

            log.append({"id" : p,
                        "runtime" : t2-t1,
                        'timed_out' : timeout,
                        'timeout' : TIMEOUT, 
                        'matcher' : matcher,
                        'filename' : filename, 
                        "g_main_nodes" : len(g_main.nodes),
                        "g_sub_nodes" : len(g_sub.nodes)})

    df = pd.DataFrame(log)
    pickle.dump(df, open(outfile, 'wb'))


if __name__ == "__main__":

    infiles = ['all_graphs.00000000.tar.gz',
               #'all_graphs.00000001.tar.gz',
               #'all_graphs.00000002.tar.gz',
               #'all_graphs.00000003.tar.gz',
    ]

    outfile = "/tmp/out.pickle"
    exp_name = "dummpy"
    ec = {}
    matcher = 'ri'
    timeout =  1.0
    num = 1
    run_exp(infiles, outfile, exp_name, ec, matcher, num, timeout)
