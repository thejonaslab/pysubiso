from pysubiso import riwrapper


class Match:
    def __init__(self):
        pass

    def is_iso(self, g_sub_adj, g_sub_color,
               g_main_adj, g_main_color,
               timeout = 1.0):
        """


        """

        raise NotImplementedError()

    
    def is_indsubsio(self, g_sub_adj, g_sub_color, 
                     g_main_adj, g_main_color, timeout=1.0):
        """

        
        """
        raise NotImplementedError()
    
    def edge_add_indsubsio(g_sub_adj, g_sub_color, 
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

    raise NotImplementedError()

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
        
    def edge_add_indsubsio(g_sub_adj, g_sub_color, 
                           g_main_adj, g_main_color, 
                           possible_edges, timeout=1.0):
        """
        possible_edges: N x 3 list of edges. If we add
        edge i to g_sub is the result indsubiso to g_main? 
        
        Of course we could just set the value in the adj mat
        and call ind_subiso but this might be faster in some situations,
        including moving the loop over possible_edges into C.
        """
        
               


                
