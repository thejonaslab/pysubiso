import numpy as np
import networkx as nx


from pysubiso import riwrapper

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
    if name == 'RI':
        return RIMatch()

    elif name == 'NX':
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

    def is_indsubiso(self, g_sub_adj, g_sub_color, 
                     g_main_adj, g_main_color, timeout=1.0):
        """


        """

        return riwrapper.c_is_indsubiso(g_sub_adj, g_sub_color,
                                        g_main_adj, g_main_color, timeout)
        
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

        out_array = np.zeros(len(candidate_edges), dtype=np.int32)

        try:
            riwrapper.c_which_edges_indsubiso(g_sub_adj, g_sub_color, 
                                              g_main_adj, g_main_color, 
                                              candidate_edges, out_array,
                                              timeout)
        except Exception as e:  # FIXME clean up this exception handling
            if str(e) == 'timeout':
                raise TimeoutError()
            raise 
        return out_array > 0

                
# class NXMatch(Match):  THIS IS NOT INDUCED SUBISOMORPHISM 
#     """
#     Very simple wrapper for equivalent networkx
#     functionality. To be used as the reference implementation, 
#     but since on each invocation it creates a graph, is VERY SLOW
    

#     """ 
#     def __init__(self):
#         pass

#     def create_g(self, adj, color):
#         G = nx.from_numpy_matrix(adj)
#         print(type(G))
#         for i, v in enumerate(color):
#             print('node colors', i, v)
#             G.nodes[i]['color'] = v

#         for e in G.edges:
#             print("edge=", e, 'color=', adj[e[0], e[1]])
#             G.edges[e]['color'] = adj[e[0], e[1]]
#         return G


#     def _node_match(self, n1, n2):
#         return n1['color'] == n2['color']

#     def _edge_match(self, e1, e2):
#         return e1['color'] == e2['color']

#     def is_indsubiso(self, g_sub_adj, g_sub_color, 
#                      g_main_adj, g_main_color, timeout=1.0):
#         """
        
#         """
#         g_sub = self.create_g(g_sub_adj, g_sub_color)
#         g_main = self.create_g(g_main_adj, g_main_color)
        

#         nm = nx.algorithms.isomorphism.GraphMatcher(g_main, g_sub,
#                                                     node_match = self._node_match,
#                                                     edge_match = self._edge_match)

#         return nm.subgraph_is_isomorphic()
