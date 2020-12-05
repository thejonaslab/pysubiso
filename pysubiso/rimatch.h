#pragma once

int is_indsubiso(int query_N, int * query_adj, int * query_vertlabel,               
              int ref_N, int * ref_adj, int * ref_vertlabel, float maxtime);

int which_edges_indsubiso_incremental(int query_N, int * query_adj, int * query_vertlabel,               
                                      int ref_N, int * ref_adj, int * ref_vertlabel,
                                      int possible_edges_N, int * possible_edges,
                                      int * possible_edges_out, 
                                      float max_time);
