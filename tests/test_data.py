"""
Test functions with real data. 


"""

import gzip
import time
import pickle
import os
import numpy as np
import networkx as nx
import pytest
import tarfile

import pysubiso

from glob import glob

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(TEST_DIR, "../data")

MOL_DATA_NORMAL = [os.path.basename(f) for f in glob(DATA_DIR + "/molecules.normal.*.tar.gz")]


MATCHERS = ['RI', 'lemon']


@pytest.mark.parametrize('matcher', MATCHERS)
@pytest.mark.parametrize('filename', MOL_DATA_NORMAL)
def test_moldata_normal_next_indsubsio(matcher, filename):
    """
    For the mol dataset, make sure our edge_add_indsubiso code
    matches what we'd actually see if we added the edge. 
    
    """

    TIMEOUT = 1.0
    CANDIDATE_EDGE_COLORS = np.array([1, 2, 3, 4], dtype=np.int32)
    m = pysubiso.create_match(matcher)

    #for filename in MOL_DATA_NORMAL:
    full_filename = os.path.join(DATA_DIR, filename)
    for g_adj, g_color, g_sub_adj, g_sub_color \
        in pysubiso.util.read_graphml_tgz_data(full_filename):

        try:
            candidate_edges = pysubiso.gen_possible_next_edges(g_sub_adj,
                                                               CANDIDATE_EDGE_COLORS)

            valid_indsubiso = m.edge_add_indsubiso(g_sub_adj, g_sub_color,
                                                   g_adj, g_color,
                                                   candidate_edges, TIMEOUT)

            for res, (i, j, c) in zip(valid_indsubiso, candidate_edges):
                a = g_sub_adj.copy()
                a[i, j] = c
                a[j, i] = c
                manual_res =  m.is_indsubiso(a, g_sub_color, g_adj, g_color)
                assert res == manual_res, f"edge {i},{j}, color={c} did not match"
            
        except pysubiso.TimeoutError as e:
            timeout = True
            continue
    
