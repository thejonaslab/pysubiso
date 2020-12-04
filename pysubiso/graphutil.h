#include <utility>
#include <iostream>
#include <vector>
#include <string>
#include <tuple>
#include <inttypes.h>
#include <random>


#pragma once

typedef uint32_t vertex_t; 
typedef std::pair<vertex_t, vertex_t> edge_t;
typedef std::vector<edge_t> edgelist_t;
typedef std::vector<bool> fixedlist_t; 

typedef std::mt19937 rng_t;

std::string hello_world(std::string sayit); 

bool is_connected(edgelist_t el,
                  int vertex_n);


std::vector<int> ordered_edge_count_list(edgelist_t in,
                                 edgelist_t match);

std::vector<int> random_distinct_int(int EDGE_N, int m);

bool edges_equal(edge_t e1, edge_t e2);

int vert_labeled_mcmc_multi_mutate(edgelist_t & el,
                                   fixedlist_t fixed,
                                   int vertex_n,
                                   int max_multi, 
                                   int iters, 
                                   bool onlyconnected,
                                   bool debug);

edgelist_t vert_labeled_mcmc_multi(const edgelist_t & el,
                                   fixedlist_t fixed,
                                   int vertex_n,
                                   int max_multi, 
                                   int iters, 
                                   bool onlyconnected,
                                   bool debug);

edgelist_t test_el_return(int i);

inline auto source(edge_t e) {
    return std::get<0>(e); 
}

inline auto target(edge_t e) {
    return std::get<1>(e); 
}

int count_unique(std::vector<int> vals); 

bool edge_sanity_check(edgelist_t el, int vert_n); 

inline auto order_edge(edge_t e) {
    if(source(e) <= target(e)) {
        return e;
    } else {
        return edge_t(target(e), source(e));
    }
}
