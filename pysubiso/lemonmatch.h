#pragma once

extern "C" int numpy_test(float * x, int N);

extern "C" int subiso_vf2(int * g1_in, int * g1_label_in, int g1_n,  // g1 is the subiso query,
                          int * g2_in, int * g2_label_in, int g2_n,  // g2 is the bigger graph,
                          int * matched_nodes, int * matched_nodes_n); 


int which_edges_subiso(int * g_full_in,
                       int * g_sub_in,
                       int * g_label_in, 
                       int * g_skip, int g_n,
                       int * possible_edge_out);

int which_edges_subiso_labeled(int * g_full_in,
                               int * g_sub_in,
                               int * g_label_in, 
                               int * g_skip, int g_n,
                               int * possible_weights,
                               int possible_weight_n, 
                               int * possible_edge_out, float max_run_sec); 


extern "C" int subiso_vf2_multi(// g1 is the subiso query,
                                int * g1_in, int * g1_label_in, int g1_n,
                                // g2 is the bigger graph,
                                int * g2_in, int * g2_label_in, int g2_n,
                                int * matched_nodes, int * matched_nodes_n); 


extern "C" int subiso_vf2_weighted(// g1 is the subiso query,
                                   int * g1_in, int * g1_label_in, int g1_n,
                                   // g2 is the bigger graph,
                                   int * g2_in, int * g2_label_in, int g2_n,
                                   int * matched_nodes,
                                   int * matched_nodes_n,
                                   double max_time_secs); 

