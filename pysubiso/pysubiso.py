import numpy as np
import networkx as nx


from pysubiso import riwrapper
from pysubiso import lemonwrapper
from pysubiso import util
class TimeoutError(Exception):
    pass

class Match:
    def __init__(self):
        pass

    def is_iso(self, g_sub_adj, g_sub_color,
               g_main_adj, g_main_color,
               timeout = 1.0):
        """


        """

        raise NotImplementedError()

    
    def is_indsubiso(self, g_sub_adj, g_sub_color, 
                     g_main_adj, g_main_color, timeout=1.0):
        """

        
        """
        raise NotImplementedError()
    
    def edge_add_indsubiso(self, g_sub_adj, g_sub_color, 
                           g_main_adj, g_main_color, 
                           possible_edges, timeout=1.0):
        """
        possible_edges: N x 3 list of edges. If we add
        edge i to g_sub is the result indsubiso to g_main? 
        
        Of course we could just set the value in the adj mat
        and call ind_subiso but this might be faster in some situations,
        including moving the loop over possible_edges into C.
        """

        raise NotImplementedError()
    
               

def create_match(name):
    name = name.lower()
    if name == 'ri':
        return RIMatch()

    elif name == 'lemon':
        return LemonMatch()
    elif name == 'nx':
        return NXMatch()

    raise NotImplementedError(f"unkown {name} matcher")

class RIMatch(Match):
    def __init__(self):
        pass

    def is_iso(self, g_sub_adj, g_sub_color,
               g_main_adj, g_main_color,
               timeout = 1.0):
        """


        """
        return riwrapper.c_is_match(g_sub_adj, g_sub_color,
                                    g_main_adj, g_main_color, timeout,
                                    match_type=0)

    def is_indsubiso(self, g_sub_adj, g_sub_color, 
                     g_main_adj, g_main_color, timeout=1.0):
        """


        """

        return riwrapper.c_is_match(g_sub_adj, g_sub_color,
                                    g_main_adj, g_main_color, timeout,
                                    match_type=1)
        

    def edge_add_indsubiso(self, g_sub_adj, g_sub_color, 
                           g_main_adj, g_main_color, 
                           candidate_edges, timeout=1.0):
        """
        candidate_edges: N x 3 list of edges. If we add
        edge i,j,c to g_sub is the result indsubiso to g_main? 
        
        Of course we could just set the value in the adj mat
        and call ind_subiso but this might be faster in some situations,
        including moving the loop over possible_edges into C.
        """

        np.testing.assert_array_equal(g_sub_adj, g_sub_adj.T)
        np.testing.assert_array_equal(g_main_adj, g_main_adj.T)

        out_array = np.zeros(len(candidate_edges), dtype=np.int32)

        try:
            out_array = riwrapper.c_which_edges_indsubiso_incremental(g_sub_adj, g_sub_color, 
                                                                      g_main_adj, g_main_color, 
                                                                      candidate_edges, 
                                                                      timeout)
            return out_array > 0 
        except Exception as e:  # FIXME clean up this exception handling
            if str(e) == 'timeout':
                raise TimeoutError()
            raise 
    
class LemonMatch(Match):
    def __init__(self):
        pass

    def is_indsubiso(self, g_sub_adj, g_sub_color, 
                     g_main_adj, g_main_color, timeout=1.0):
        """


        """

        
        wasiso, mapping = lemonwrapper.lemon_subiso_vf2(
            g_sub_adj, g_sub_color, 
            g_main_adj, g_main_color, 
            weighted_edges=True, max_run_sec=timeout)

        return wasiso

    def edge_add_indsubiso(self, g_sub_adj, g_sub_color, 
                           g_main_adj, g_main_color, 
                           candidate_edges, timeout=1.0):
        """
        candidate_edges: N x 3 list of edges. If we add
        edge i,j,c to g_sub is the result indsubiso to g_main? 
        
        Of course we could just set the value in the adj mat
        and call ind_subiso but this might be faster in some situations,
        including moving the loop over possible_edges into C.
        """


        try:
            out_array = lemonwrapper.which_edges_indsubiso(g_sub_adj, g_sub_color, 
                                                         g_main_adj, g_main_color, 
                                                         candidate_edges, 
                                                         timeout)
        except Exception as e:  # FIXME clean up this exception handling
            if str(e) == 'timeout':
                raise TimeoutError()
            raise 
        return out_array > 0
    


class NXMatch(Match):
    """
    Just a NetworkX wrapper that supports isomorphism 
    calculation (because NX does not support induced
    subisomoprhism calculations, only classic subisomorphism)
    """
    
    def __init__(self):
        pass

    def is_iso(self, g_sub_adj, g_sub_color,
               g_main_adj, g_main_color,
               timeout = 1.0):
        """


        """

        
        g_sub = util.adj_colors_to_nx_graph(g_sub_adj, g_sub_color)
        g_main = util.adj_colors_to_nx_graph(g_main_adj, g_main_color)
        GM = nx.algorithms.isomorphism.GraphMatcher(g_sub, g_main,
                                      node_match = lambda n1, n2: n1['color'] == n2['color'],
                                      edge_match = lambda e1, e2: e1['color'] == e2['color'],
        )
        

        return GM.is_isomorphic()
        
