#include <utility>
#include <iostream>
#include <vector>

#include "graphutil.h"


rng_t rng; 

std::string hello_world(std::string sayit) {
    return "hello world: " + sayit; 

}


float rand_01(rng_t & rng) {
    std::uniform_real_distribution<float> dist01(0.0,1.0);
    return dist01(rng); 

}

std::vector<vertex_t> get_neighbors(edgelist_t el, vertex_t v)
{
    // FIXME VERY INEFFICIENT
    
    std::vector<vertex_t> out; 
    for(auto e : el) {
        if(source(e) == v) {
            out.push_back(target(e));
        } else if (target(e) == v) {
            out.push_back(source(e)); 
        }
    }
    return out; 
}


bool is_connected(edgelist_t el,
               int vertex_n)
{
    // Is this graph connected
    
    if(el.empty()) {
        return false;
    }

    std::vector<bool> visited(vertex_n);

    vertex_t start_node = source(el[0]);
    std::vector<vertex_t> to_visit;
    to_visit.push_back(start_node);
    while(to_visit.size() > 0) {
        auto v = to_visit.back();
        to_visit.pop_back();
        if (visited[v]) {
            continue;
        }
        visited[v] = true;
        for(auto new_v: get_neighbors(el, v))  {
            if(!visited[new_v]) { 
                to_visit.push_back(new_v); 
            }
        }
    }
    for(auto v : visited) {
        if (!v) {
            return false; 
        }
    }
    return true;     
        
}

std::vector<int> ordered_edge_count_list(edgelist_t in,
                                 edgelist_t match) {
    /*
      how many times does each edge in match occur
      in the list

    */

    std::vector<int> out(match.size());
    for( auto & e : in) { 
        for(int i =0; i < match.size(); ++i) {
            // Ideally both would be ordered
            if (match[i] == e) {
                out[i] += 1; 
            }
            
        }
    }
    return out; 
}

std::vector<int> random_distinct_int(int N, int m) {
    std::vector<int> out(m); 
    std::uniform_int_distribution<int> dist(0, N-1);
    if (m > N) {
        throw std::runtime_error("m > N");
    }
        
    for(int i =0; i < m; ++i) {
        if(i == 0) {
            out[i] = dist(rng); 
        } else {
            bool val_unique = false;
            while (!val_unique) {
                val_unique = true; 
                out[i] = dist(rng);
                for(int j = 0; j< i; j++) {
                    if(out[j] == out[i]) {
                        val_unique = false;
                        break; 
                    }
                }

            }
        }
    }
    return out; 
}

bool edges_equal(edge_t e1, edge_t e2) {
    return e1 == e2; 
}

int count_unique(std::vector<int> vals) {
    int unique = 0;
    std::vector<bool> seen_before(vals.size());
    
    for(int i = 0; i < vals.size(); ++i) {
        bool none_equal = true;
        if(seen_before[i]) {
            continue; 
        }
        for(int j = 0; j < vals.size(); ++j) {
            if((j != i) && (vals[i] == vals[j]) && (!seen_before[j])) {
                
                none_equal = false;
                seen_before[j] = true; 
            }
        }
        if (none_equal || !seen_before[i]) {
            unique += 1;

        }
            
        seen_before[i] = true; 

    }
    return unique; 

}


bool edge_sanity_check(edgelist_t el, int vert_n) {
    /*
      Are the edges (lower, upper)
      does lower != upper (no multigraphs)
      Are all 0 <= verticies < vert_n 
    */
    for(auto e: el) {
        if (source(e) >= target(e) ) {
            return false;
        }

        if((source(e) < 0 ) || (source(e) >= vert_n)){
            return false;
        }

        if((target(e) < 0 ) || (target(e) >= vert_n)){
            return false;
        }
        
        
    }
    return true; 
}

edgelist_t vert_labeled_mcmc_multi(const edgelist_t & el,
                                   fixedlist_t fixed,
                                   int vertex_n,
                                   int max_multi, 
                                   int iters,
                                   bool onlyconnected,
                                   bool debug)
{
    edgelist_t new_el(el);
    vert_labeled_mcmc_multi_mutate(new_el,
                                   fixed, vertex_n,
                                   max_multi,
                                   iters, onlyconnected,
                                   debug);
    return new_el; 

}

int vert_labeled_mcmc_multi_mutate(edgelist_t & el,
                                   fixedlist_t fixed,
                                   int vertex_n,
                                   int max_multi, 
                                   int iters,
                                   bool onlyconnected,
                                   bool debug)
{

    /*
      MCMC to sample virtex-labeled multigraphs with a degree list with a given
      max number of edges between two nodes. 
      
      This is algorthm SM1 from Johan paper.       
      
      edgelist_t : graph edges
      we assume that an edge is ordered (low, high)
      There can be no self-edges (no loops)

      fixed : is this edge fixed or not. If not we will not swap it. 

      vertex_n : number of verticies
      
      we assume vertices are numberd [0, vertex_n-1]

      We do not check for connectivity at input unless debug=true
      
      Goals:
      fast 
      vectorizable / use SIMD
      cache-friendly

      should be callable in a loop with no real overhead
    */


    // identify free edges
    std::vector<int> free_edges_idx; ;
    for(int i = 0; i < fixed.size(); ++i) {
        if(!fixed[i]) {
            free_edges_idx.push_back(i); 
        }
    }

    if(el.size() != fixed.size()) {
        throw std::runtime_error("edgelist and fixed must have same length");
    }
    if (debug) {
        if (!edge_sanity_check(el, vertex_n)) {
            throw std::runtime_error("failed edge sanity check"); 
        }
        

        if (onlyconnected && !is_connected(el, vertex_n)) {
            throw std::runtime_error("onlyconnected specified but input graph was not connected"); 
        }
            
        // FIXME check there are enough edges
        if (free_edges_idx.size()< 2) {
            throw std::runtime_error("insufficient free edges for swap"); 
        }
        
    }


    for (int i = 0; i < iters; ++i) {

        // randomly pick two edges
        auto random_edges_idx = random_distinct_int(free_edges_idx.size(), 2); 
        int e_idx_1 = free_edges_idx[random_edges_idx[0]]; 
        int e_idx_2 = free_edges_idx[random_edges_idx[1]]; 
            
        edge_t e_1 = el[e_idx_1];
        edge_t e_2 = el[e_idx_2];
        // std::cout << "e_idx_1 " << e_idx_1 << " e_idx_2=" << e_idx_2 << std::endl; 
        // std::cout << "e_1=" << source(e_1) << "-" << target(e_1) << " e_2=" << source(e_2) << "-" << target(e_2) << std::endl;

        if (e_1 == e_2) {
            continue; 
        }
        if (rand_01(rng) < 0.5) {
            // swap e_1 endpoints
            e_1 = std::make_pair(target(e_1), source(e_1));
            // FIXME is canonicalizing the ordering of edges' nodes going to result in biased
            // sampling later down the line? 
        }

        if (rand_01(rng) < 0.5) {
            // swap e_2 endpoints because why not
            e_2 = std::make_pair(target(e_2), source(e_2));
            // FIXME is canonicalizing the ordering of edges' nodes going to result in biased
            // sampling later down the line? 
        }

        vertex_t u = source(e_1);
        vertex_t v = target(e_1);
        vertex_t x = source(e_2);
        vertex_t y = target(e_2);
        
        if (u == x) {
            continue; 
        }

        if (v == y) {
            continue;
        }


        // fixme does this include fixed edges?
        edgelist_t possible_edges = {order_edge(edge_t(u, v)), 
                                     order_edge(edge_t(x, y)), 
                                     order_edge(edge_t(u, x)), 
                                     order_edge(edge_t(v, y))};
        
        auto counts = ordered_edge_count_list(el, possible_edges) ;
        int w_uv = counts[0];
        int w_xy = counts[1];
        int w_ux = counts[2];
        int w_vy = counts[3];

        if ((w_ux >= max_multi) || (w_vy >= max_multi)) {
            continue;
            
        }
        std::vector<int> uniques = {int(x), int(y), int(u), int(v)}; 
        int unique_n = count_unique(uniques); 
        float swaps_to = 0.0;
        float swaps_from = 0.0;

        if(unique_n == 4) {
            swaps_to = w_uv * w_xy;
            swaps_from = (w_ux+1)*(w_vy+1);

        } else if (unique_n == 3) {
            if( (u == v) || (x == y)) { 
                swaps_to = 2 * w_uv * w_xy; 
                swaps_from = (w_ux + 1)*(w_vy + 1);
            } else { 
                swaps_to =  w_uv * w_xy; 
                swaps_from = 2*(w_ux + 1)*(w_vy + 1);
            }
        } else if (unique_n == 2) {
            std::cout << "i=" << i << std::endl; 
            std::cout << "unique_n=" << unique_n << std::endl;
            std::cout << "x=" << x << "y=" << y << "u=" << u << "v=" << v << std::endl;
            throw std::runtime_error("we should never get here, edges are same");
        } else {
            continue; 
        }

        swaps_to = std::max(0.00001f, swaps_to); // avoid divide by zero
        float p = std::min(1.0f, float(swaps_from)/swaps_to);

        if (rand_01(rng) < p) {
            // do the swap
            edge_t old_e_1 = el[e_idx_1];
            edge_t old_e_2 = el[e_idx_2];
            
            el[e_idx_1] = order_edge(std::make_pair(u, x));
            el[e_idx_2] = order_edge(std::make_pair(v, y));
            
            // check connectivity
            if (onlyconnected) {
                if (!is_connected(el, vertex_n) ) {
                    // return to original 
                    el[e_idx_1] = old_e_1;
                    el[e_idx_2] = old_e_2; 
                }

            }
            
        }
        
    }
    
}      

edgelist_t test_el_return(int i) {
    edgelist_t el; 
    for(int j = 0; j < i; j++) {
        el.push_back(std::make_pair(j, j+1)); 
    }
    return el;
    
}
