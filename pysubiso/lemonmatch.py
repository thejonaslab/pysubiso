
import graphutil

import pyximport; pyximport.install()
import cythontest
import numpy as np

class TimeoutError(Exception):
    pass

def is_res_subisomorphic(gmain, gsub, 
                         check_observed=True, 
                         check_value = True, 
                         check_splitting=True, 
                         bond_weights=[1, 1.5, 2, 3], 
                         max_value_dist = {6: 1.0, 1: 0.5}, 
                         return_mapping=False):


    """
    Convenience function to check if gsub is a subgraph of molecule
    graph gmain. 

    // FIXME we assume gmain and gsub have the SAME vertices

    """
    assert len(gmain.vs) == len(gsub.vs)
    nec = graphutil.NodeEqualityCompare(check_atomicno=True, 
                                        check_observed=check_observed, 
                                        check_value = check_value, 
                                        check_splitting = check_splitting, 
                                        bond_weights=bond_weights, 
                                        max_value_dist = max_value_dist
                                        ) 
    compare_mat = nec(gmain, gsub)
    gmain_colors = graphutil.compat_mat_to_colors(compare_mat)
                                        

    full_adj = graphutil.igraph_to_adj(gmain)
    sub_adj = graphutil.igraph_to_adj(gsub)

    bond_weight_pos_mapping = {w : i+1 for i, w in enumerate(bond_weights)}
    bond_weight_pos_mapping[0] = 0

    def to_mapping(a):
        a_int = np.zeros((a.shape[0], 
                          a.shape[1]), dtype=np.int32)
        for i in range(a.shape[0]):
            for j in range(a.shape[1]):
                a_int[i, j] = a[i, j] * 2 # bond_weight_pos_mapping[a[i, j]]
        return a_int
    full_adj_int = to_mapping(full_adj)
    sub_adj_int = to_mapping(sub_adj)

    N = gmain.vcount()
    PW = len(bond_weights)


    gsub_adj = (sub_adj * 2 ).astype(np.int32) 
    gmain_adj = (full_adj * 2 ).astype(np.int32)

    wasiso, mapping = cythontest.lemon_subiso_vf2(
        gsub_adj, gmain_colors, 
        gmain_adj, gmain_colors, 
        weighted_edges=True)


    if return_mapping:
        return wasiso, mapping

    return wasiso 


def which_edges_sub_labeled_old(gmain, gsub, consider_multiple_edges=True,
                            check_observed=True, 
                            check_max_degree = False,
                            check_value = True, check_splitting=True, 
                            bond_weights=[1, 1.5, 2, 3], 
                            round_value_to = 0.1,
                            max_run_sec=0.0, use_full=False):
    """
    """


    #assert graphutil.graph_degree_check(gmain)
    #assert graphutil.graph_degree_check(gsub)
    weighted_edges=True
    check_num_H = False

    def node_color_func(v):
        node_prop = []

        node_prop.append(v['atomicno'])
        
        if check_observed:
           node_prop.append(v['observed'])
           
        def round(x):
            f = 1.0 / round_value_to 
            return np.round(x * f)/f

        if check_value:
           node_prop.append(round(v['value']))

        if check_max_degree:
           node_prop.append(v['max_degree'])

        if check_num_H and 'num_H' in v.attributes():
           node_prop.append(v['num_H'])

        if check_splitting:
            node_prop.append(v['splitting'])

        
        return tuple(node_prop)

    gmain_node_tuples = [node_color_func(v) for v in gmain.vs]
    label_tuples = set(gmain_node_tuples)
    colors = {t: i for i, t in enumerate(label_tuples)}
    gmain_colors = np.array([colors[t] for t in gmain_node_tuples]).astype(np.int32)

    full_adj = graphutil.igraph_to_adj(gmain)
    sub_adj = graphutil.igraph_to_adj(gsub)

    bond_weight_pos_mapping = {w : i+1 for i, w in enumerate(bond_weights)}
    bond_weight_pos_mapping[0] = 0

    def to_mapping(a):
        a_int = np.zeros((a.shape[0], 
                          a.shape[1]), dtype=np.int32)
        for i in range(a.shape[0]):
            for j in range(a.shape[1]):
                a_int[i, j] = a[i, j] * 2 # bond_weight_pos_mapping[a[i, j]]
        return a_int
    full_adj_int = to_mapping(full_adj)
    sub_adj_int = to_mapping(sub_adj)

    #print("full_adj_int[5, 24]=", full_adj_int[5, 24])
    #print("sub_adj_int[5, 24]=", sub_adj_int[5, 24], "sub_adj[5, 24]=", sub_adj[5, 24])
    N = gmain.vcount()
    PW = len(bond_weights)

    ### just check gsub is actually subiso to main

    is_subisomorphic = is_res_subisomorphic(gmain, gsub, 
                                            check_observed=check_observed, 
                                            check_max_degree = check_max_degree, 
                                            check_value=check_value, 
                                            check_splitting = check_splitting, 
                                            bond_weights = bond_weights, 
                                            max_value_dist = max_value_dist)

    if not is_subisomorphic:
        return np.zeros((N, N, PW), dtype=np.int32)

    
    #max_degree = np.array(gsub.vs['max_degree'])
    cur_connected = sub_adj.sum(axis=1)

    #full = (cur_connected >= max_degree)
    full = np.zeros_like(cur_connected, dtype=np.int32)
    if not use_full :
        full[:] = 0 
    else:
        print("WARNING: We should not be using max degree checking, because "\
              "our understanding of how this works was in fact quite incorrect "\
              " and we can have valid carbons with effectval val of 4.5, etc.")
    

    # not clear why we couldn't be subiso with max_degree = 1? 
    #single_degree = (max_degree == 1)

    # to_skip_2 = np.zeros(sub_adj.shape, dtype=np.int32) # 
    # to_skip_2[:] += full
    # to_skip_2.T[:] += full
    # #to_skip_2 += np.outer(single_degree, single_degree)
    # to_skip_2 = np.triu((to_skip_2 > 0).astype(np.int32), 1)
    # to_skip = to_skip_2
    to_skip = np.zeros((sub_adj.shape[0], 
                        sub_adj.shape[1], 
                        PW), dtype=np.int32)
    # skip anything with an existing bond
    for i in range(PW):
        to_skip[sub_adj > 0, i]  = 1

#    bw_lut = np.arange(len(bond_weights), dtype=np.int32) + 1
    bw_lut = np.array([2, 3, 4, 6], dtype=np.int32)

    #print("ARE WE SKIPPING (3, 4)", to_skip[3, 4])
    try:
        out= cythontest.py_which_edges_subiso_labeled(full_adj_int, sub_adj_int, 
                                                      gmain_colors, 
                                                      to_skip,
                                                      bw_lut, 
                                                      max_run_sec=max_run_sec)
    except RuntimeError:
        raise TimeoutError()
    
    #assert np.sum(np.tril(out, 0)) == 0

    out = out + out.swapaxes(1,0)

    assert out.min() >= 0
    assert out.max() <= 1
    
    return out



def which_edges_sub_labeled(gmain, gsub, 
                            check_observed=True, 
                            check_max_degree = False,
                            check_value = True, 
                            check_splitting=True, 
                            bond_weights=[1, 1.5, 2, 3], 
                            max_value_dist = {6: 1.0, 1: 0.5}, 
                            
                            max_run_sec=0.0):
    """
    """

    
    nec = graphutil.NodeEqualityCompare(check_atomicno=True, 
                                        check_observed=check_observed, 
                                        check_value = check_value, 
                                        check_splitting = check_splitting, 
                                        bond_weights=bond_weights, 
                                        max_value_dist = max_value_dist
                                        ) 
    compare_mat = nec(gmain, gsub)
    gmain_colors = graphutil.compat_mat_to_colors(compare_mat)
                                        

    full_adj = graphutil.igraph_to_adj(gmain)
    sub_adj = graphutil.igraph_to_adj(gsub)

    bond_weight_pos_mapping = {w : i+1 for i, w in enumerate(bond_weights)}
    bond_weight_pos_mapping[0] = 0

    def to_mapping(a):
        a_int = np.zeros((a.shape[0], 
                          a.shape[1]), dtype=np.int32)
        for i in range(a.shape[0]):
            for j in range(a.shape[1]):
                a_int[i, j] = a[i, j] * 2 # bond_weight_pos_mapping[a[i, j]]
        return a_int
    full_adj_int = to_mapping(full_adj)
    sub_adj_int = to_mapping(sub_adj)

    N = gmain.vcount()
    PW = len(bond_weights)

    ### just check gsub is actually subiso to main

    is_subisomorphic, mapping = is_res_subisomorphic(gmain, gsub, 
                                                     check_observed=check_observed, 
                                                     check_value = check_value, 
                                                     check_splitting=check_splitting, 
                                                     bond_weights=bond_weights, 
                                                     max_value_dist = max_value_dist,
                                                     return_mapping=True)
    if not is_subisomorphic:
        return np.zeros((N, N, PW), dtype=np.int32)


    to_skip = graphutil.which_edges_to_skip(gmain, gsub)
    class_to_skip = graphutil.edge_type_exist_tgt(gmain, gmain_colors)
    to_skip = to_skip | class_to_skip

    to_skip = to_skip.astype(np.int32)

#    bw_lut = np.arange(len(bond_weights), dtype=np.int32) + 1
    bw_lut = np.array([2, 3, 4, 6], dtype=np.int32)

    #print("ARE WE SKIPPING (3, 4)", to_skip[3, 4])
    try:
        out= cythontest.py_which_edges_subiso_labeled(full_adj_int, sub_adj_int, 
                                                      gmain_colors, 
                                                      to_skip,
                                                      bw_lut, 
                                                      max_run_sec=max_run_sec)
    except RuntimeError:
        raise TimeoutError()
    
    #assert np.sum(np.tril(out, 0)) == 0

    out = out + out.swapaxes(1,0)

    assert out.min() >= 0
    assert out.max() <= 1
    
    return out


class SubIsoCalculator:
    def __init__(self, check_atomicno =True, 
                 check_observed=True, 
                 check_max_degree = False,
                 check_value = True, 
                 check_splitting=True, 
                 bond_weights=[1, 1.5, 2, 3], 
                 max_value_dist = {6: 1.0, 1: 0.5}, 
                 max_run_sec=0.0):

        self.check_atomicno = check_atomicno
        self.check_observed = check_observed
        self.check_max_degree = False
        self.check_value = check_value
        self.check_splitting = check_splitting
        self.bond_weights = bond_weights
        self.max_value_dist = max_value_dist
        self.max_run_sec = max_run_sec

        self.nec = graphutil.NodeEqualityCompare(check_atomicno=self.check_atomicno, 
                                        check_observed=self.check_observed, 
                                        check_value = self.check_value, 
                                        check_splitting = self.check_splitting, 
                                        bond_weights=self.bond_weights, 
                                        max_value_dist = self.max_value_dist
                                        ) 

    def get_node_colors(self, gmain, gsub):
        assert len(gmain.vs) == len(gsub.vs)
        compare_mat = self.nec(gmain, gsub)
        gmain_colors = graphutil.compat_mat_to_colors(compare_mat)

        return gmain_colors

    def is_subiso(self, gmain, gsub, return_mapping=False, max_run_sec=None):
        """
        Convenience function to check if gsub is a subgraph of molecule
        graph gmain. 

        // FIXME we assume gmain and gsub have the SAME vertices

        """
        # assert len(gmain.vs) == len(gsub.vs)
        # compare_mat = self.nec(gmain, gsub)
        # gmain_colors = graphutil.compat_mat_to_colors(compare_mat)
        gmain_colors = self.get_node_colors(gmain, gsub)

        full_adj = graphutil.igraph_to_adj(gmain)
        sub_adj = graphutil.igraph_to_adj(gsub)

        bond_weight_pos_mapping = {w : i+1 for i, w in enumerate(self.bond_weights)}
        bond_weight_pos_mapping[0] = 0

        def to_mapping(a):
            a_int = np.zeros((a.shape[0], 
                              a.shape[1]), dtype=np.int32)
            for i in range(a.shape[0]):
                for j in range(a.shape[1]):
                    a_int[i, j] = a[i, j] * 2 # bond_weight_pos_mapping[a[i, j]]
            return a_int
        full_adj_int = to_mapping(full_adj)
        sub_adj_int = to_mapping(sub_adj)

        N = gmain.vcount()
        PW = len(self.bond_weights)


        gsub_adj = (sub_adj * 2 ).astype(np.int32) 
        gmain_adj = (full_adj * 2 ).astype(np.int32)

        if max_run_sec is None:
            max_run_sec = self.max_run_sec

        wasiso, mapping = cythontest.lemon_subiso_vf2(
            gsub_adj, gmain_colors, 
            gmain_adj, gmain_colors, 
            weighted_edges=True, max_run_sec=max_run_sec)


        if return_mapping:
            return wasiso, mapping

        return wasiso 


    
    def which_edges_subiso(self, gmain, gsub, max_run_sec = None):
        
        
        # compare_mat = self.nec(gmain, gsub)
        # gmain_colors = graphutil.compat_mat_to_colors(compare_mat)
        gmain_colors = self.get_node_colors(gmain, gsub)


        full_adj = graphutil.igraph_to_adj(gmain)
        sub_adj = graphutil.igraph_to_adj(gsub)

        bond_weight_pos_mapping = {w : i+1 for i, w in enumerate(self.bond_weights)}
        bond_weight_pos_mapping[0] = 0

        def to_mapping(a):
            a_int = np.zeros((a.shape[0], 
                              a.shape[1]), dtype=np.int32)
            for i in range(a.shape[0]):
                for j in range(a.shape[1]):
                    a_int[i, j] = a[i, j] * 2 # bond_weight_pos_mapping[a[i, j]]
            return a_int
        full_adj_int = to_mapping(full_adj)
        sub_adj_int = to_mapping(sub_adj)

        N = gmain.vcount()
        PW = len(self.bond_weights)

        ### just check gsub is actually subiso to main
        try:
            is_subisomorphic, mapping = self.is_subiso(gmain, gsub,
                                                       return_mapping=True, 
                                                       max_run_sec=max_run_sec)
        except:
            raise TimeoutError()

        if not is_subisomorphic:
            return np.zeros((N, N, PW), dtype=np.int32)


        to_skip = graphutil.which_edges_to_skip(gmain, gsub)
        class_to_skip = graphutil.edge_type_exist_tgt(gmain, gmain_colors)
        to_skip = to_skip | class_to_skip

        to_skip = to_skip.astype(np.int32)

    #    bw_lut = np.arange(len(bond_weights), dtype=np.int32) + 1
        bw_lut = np.array([2, 3, 4, 6], dtype=np.int32)

        #print("ARE WE SKIPPING (3, 4)", to_skip[3, 4])
        if max_run_sec is None:
            max_run_sec = self.max_run_sec
        try:
            out= cythontest.py_which_edges_subiso_labeled(full_adj_int, sub_adj_int, 
                                                          gmain_colors, 
                                                          to_skip,
                                                          bw_lut, 
                                                          max_run_sec=max_run_sec)
        except RuntimeError:
            raise TimeoutError()

        #assert np.sum(np.tril(out, 0)) == 0

        out = out + out.swapaxes(1,0)

        assert out.min() >= 0
        assert out.max() <= 1

        return out

                 

if __name__ == "__main__":
    print("none")

