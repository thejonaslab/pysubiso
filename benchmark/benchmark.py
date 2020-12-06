"""
Ruffus pipeline to benchmark varying different datasets

"""

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
from ruffus import *



EXPERIMENTS = {'debug_100' : {'files' : ['/tmp/slow_graphs.00000000.tar.gz'],
                              'matchers' : ['ri', 'lemon'],
                              'timeout' : 10.0,
                              'num' : 100},
               
               'allgraphs_4000' : {'files' : ['all_graphs.00000000.tar.gz',
                                              'all_graphs.00000001.tar.gz',
                                              'all_graphs.00000002.tar.gz',
                                              'all_graphs.00000003.tar.gz', ],
                                  'matchers' : ['ri', 'lemon'],
                                  'timeout' : 1.0, 
                                   'num' : 1000},               
               'riperf5' : {'files' : ['all_graphs.00000000.tar.gz',
                                              'all_graphs.00000001.tar.gz',
                                              'all_graphs.00000002.tar.gz',
                                              'all_graphs.00000003.tar.gz', ],
                                  'matchers' : ['ri'],
                                  'timeout' : 1.0, 
                                   'num' : 100},               
               # 'debug_400' : {'files' : ['/tmp/slow_graphs.00000000.tar.gz'],
               #            'matchers' : ['ri', 'lemon'],
               #            'num' : 400}

               'benchmark_newnew_100' : {'files' : ['all_graphs.00000000.tar.gz',
                                             
               ],
                                  'matchers' : ['ri', 'lemon'],
                                  'timeout' : 1.0, 
                                   'num' : 100},               

               'allgraphs_4000_faster' : {'files' : ['all_graphs.00000000.tar.gz',
                                              'all_graphs.00000001.tar.gz',
                                              'all_graphs.00000002.tar.gz',
                                              'all_graphs.00000003.tar.gz', ],
                                  'matchers' : ['ri', 'lemon'],
                                  'timeout' : 1.0, 
                                   'num' : 1000},

               'allgraphs_4000_with_next_edges' : {'files' : ['all_graphs.00000000.tar.gz',
                                              'all_graphs.00000001.tar.gz',
                                              'all_graphs.00000002.tar.gz',
                                              'all_graphs.00000003.tar.gz', ],
                                  'matchers' : ['ri', 'lemon'],
                                  'timeout' : 1.0, 
                                   'num' : 1000},
               'slow_200' : {'files' : ['/tmp/slow_graphs.00000000.tar.gz'],
                              'matchers' : ['ri', 'lemon'],
                              'timeout' : 10.0,
                              'num' : 200},               
}

def params():
    for exp_name, ec in EXPERIMENTS.items():
        infiles = ec['files']
        for matcher in ec['matchers']:
            
            outfiles = f"results.{exp_name}.{matcher}.pickle"
            yield infiles, outfiles, exp_name, ec, matcher, ec['num'], ec['timeout']

@files(params)
def run_exp(infiles, outfile, exp_name, ec, matcher, num, TIMEOUT):

    m = pysubiso.create_match(matcher)

    log = []

    possible_edges = np.array([1, 2, 3, 4], dtype=np.int32)
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


            t1 = time.time()
            timeout = False
            try:
                candidate_edges = pysubiso.gen_possible_next_edges(g_sub_adj, possible_edges)

                valid_indsubiso = m.edge_add_indsubiso(g_sub_adj, g_sub_color,
                                                       g_adj, g_color,
                                                       candidate_edges, TIMEOUT)
            except pysubiso.TimeoutError as e:
                timeout = True

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
    pipeline_run([run_exp])
