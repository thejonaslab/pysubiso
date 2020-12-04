/*

Now you should use our fork, github.com/thejonaslab/lemon

mkdir build
cd build

cmake -DCMAKE_INSTALL_PREFIX=`pwd`/../build-output  ../

# if you want shared libs (you probably don't, you can just link in 
# the static lib to a .so you're building
cmake -DCMAKE_INSTALL_PREFIX=`pwd`/../build-output -DBUILD_SHARED_LIBS=TRUE ../

make -j 8 
*/

#include <iostream>
#include <lemon/list_graph.h>

#include <lemon/vf2.h>
#include <lemon/vf2pp.h>
#include <lemon/concepts/digraph.h>
#include <lemon/smart_graph.h>
#include <lemon/lgf_reader.h>
#include <lemon/concepts/maps.h>
#include <lemon/concepts/maps.h>

#include <sstream>
#include <vector>
#include <assert.h>
#include <chrono>

using namespace lemon;
using namespace std;


#include "lemonmatch.h"

bool is_subiso_multi(SmartGraph & g1,
                     SmartGraph::NodeMap<int> & l1,
                     SmartGraph::EdgeMap<int> & w1, 
                     SmartGraph & g2,
                     SmartGraph::NodeMap<int> & l2,
                     SmartGraph::EdgeMap<int> & w2,
                     SmartGraph::NodeMap<SmartGraph::Node> & iso_out)  ; 

bool is_subiso_weighted(SmartGraph & g1,
                        SmartGraph::NodeMap<int> & l1,
                        SmartGraph::EdgeMap<int> & w1, 
                        SmartGraph & g2,
                        SmartGraph::NodeMap<int> & l2,
                        SmartGraph::EdgeMap<int> & w2,
                        SmartGraph::NodeMap<SmartGraph::Node> & iso_out,
                        double max_runtime_secs)  ; 


template<class G1, class G2, class I>
void checkSubIso(const G1 &g1, const G2 &g2, const I &i) {
  std::set<typename G2::Node> image;
  for (typename G1::NodeIt n(g1);n!=INVALID;++n){
      check(i[n]!=INVALID, "Wrong isomorphism: incomplete mapping.");
      check(image.count(i[n])==0,"Wrong isomorphism: not injective.");
      image.insert(i[n]);
  }
  for (typename G1::EdgeIt e(g1);e!=INVALID;++e) {
      check(findEdge(g2,i[g1.u(e)],i[g1.v(e)])!=INVALID,
          "Wrong isomorphism: missing edge(checkSub).");
  }
}

template<class G1,class G2,class T>
bool checkSub(const G1 &g1, const G2 &g2, const T &vf2) {
  typename G1:: template NodeMap<typename G2::Node> iso(g1,INVALID);
  if (const_cast<T&>(vf2).mapping(iso).run()) {
    checkSubIso(g1,g2,iso);
    return true;
  }
  return false;
}

extern "C" int extern_test() {
    //
    return 1234;
}

extern "C" int numpy_test(float * x, int N) {
    //
    int pos = 0; 
    for(int i =0; i < N; ++i) {
        for(int j =0; j <N; ++j) {
            std::cout << x[pos] << " ";
            pos++; 
        }
        std::cout << std::endl; 
    }
    return 0; 
}

void array_to_g(int * g, int * label, int N, SmartGraph & gout,
                SmartGraph::NodeMap<int> & labelout,
                SmartGraph::NodeMap<int> & posout,
                SmartGraph::EdgeMap<int> & wout) {

    std::vector<SmartGraph::Node> vs;
    
    for(int i = 0; i < N; ++i) {
        auto n = gout.addNode();
        labelout[n] = label[i]; 
        vs.push_back(n);

        posout[n] = i; 
    }
    int pos = 0; 
    for(int i =0; i < N; ++i) {
        for(int j =0; j <N; ++j) { 
            if (j >= i) {
                if(g[pos] > 0) {
                    
                    auto e = gout.addEdge(vs[i], vs[j]);
                    wout[e] = g[pos];
                }
            }
            pos++;
        }
    }

}


template<class G1, class G2, class I>
bool my_checksubiso(const G1 &g1, const G2 &g2, const I &i) {
  std::set<typename G2::Node> image;
  for (typename G1::NodeIt n(g1);n!=INVALID;++n){
      if(i[n] ==INVALID) {
          //std::cout << "Wrong isomorphism: incomplete mapping." << std::endl;
          return false; 
      }
      
      if(image.count(i[n]) !=0) {
          //std::cout << "Wrong isomorphism: not injective." << std::endl;
          return false; 
      }
      image.insert(i[n]);
  }
  for (typename G1::EdgeIt e(g1);e!=INVALID;++e) {
      if(findEdge(g2,i[g1.u(e)],i[g1.v(e)]) ==INVALID) {
          //std::cout << "Wrong isomorphism: missing edge(checkSub)." << std::endl;
          return false; 
      }
          
  }
  return true; 
}

extern "C" int subiso_vf2(int * g1_in, int * g1_label_in, int g1_n,  // g1 is the subiso query,
                          int * g2_in, int * g2_label_in, int g2_n, // g2 is the bigger graph,
                          int *mapping_out, int * mapped_nodes)
{
    SmartGraph g1; 
    SmartGraph::NodeMap<int> l1(g1);
    SmartGraph::NodeMap<int> p1(g1);
    SmartGraph::EdgeMap<int> e1(g1); 
    
    array_to_g(g1_in, g1_label_in, g1_n, g1, l1, p1, e1);
   
    SmartGraph g2; 
    SmartGraph::NodeMap<int> l2(g2);
    SmartGraph::NodeMap<int> p2(g2);
    SmartGraph::EdgeMap<int> e2(g2); 
    
    array_to_g(g2_in, g2_label_in, g2_n, g2, l2, p2, e2);

    auto vf2obj = vf2pp(g1, g2);

    SmartGraph::NodeMap<SmartGraph::Node> iso(g1,INVALID);
    vf2obj.mapping(iso).nodeLabels(l1, l2).run();

    *mapped_nodes = 0; 
    bool is_subiso =  my_checksubiso(g1, g2, iso);
    if(is_subiso) {
        for (SmartGraph::NodeIt n(g1); n!=INVALID; ++n){
            if(iso[n] ==INVALID) {
                assert(false);
                // we should never get here, there should always
                // be a mapping
            }
            mapping_out[p1[n]] =  p2[iso[n]]; 
        }
        *mapped_nodes = g1_n; 
    }

    return is_subiso; 

    
}


extern "C" int
subiso_vf2_multi(// g1 is the subiso query,
                 int * g1_in, int * g1_label_in, int g1_n,
                 // g2 is the bigger graph,
                 int * g2_in, int * g2_label_in, int g2_n,
                 int *mapping_out, int * mapped_nodes)
{
    SmartGraph g1; 
    SmartGraph::NodeMap<int> l1(g1);
    SmartGraph::NodeMap<int> p1(g1);
    SmartGraph::EdgeMap<int> w1(g1);
    array_to_g(g1_in, g1_label_in, g1_n, g1, l1, p1, w1);
   
    SmartGraph g2; 
    SmartGraph::NodeMap<int> l2(g2);
    SmartGraph::NodeMap<int> p2(g2);
    SmartGraph::EdgeMap<int> w2(g2);
    
    array_to_g(g2_in, g2_label_in, g2_n, g2, l2, p2, w2);

    SmartGraph::NodeMap<SmartGraph::Node> iso_g1_to_g2(g1,INVALID);
    *mapped_nodes = 0;

    bool is_subiso = is_subiso_multi(g1, l1, w1,
                                     g2, l2, w2, iso_g1_to_g2);
    
    if (is_subiso) { 
        for (SmartGraph::NodeIt n(g1); n!=INVALID; ++n){
            if(iso_g1_to_g2[n] ==INVALID) {
                assert(false);
                // we should never get here, there should always
                // be a mapping
            }
            mapping_out[p1[n]] =  p2[iso_g1_to_g2[n]]; 
        }
        *mapped_nodes = g1_n; 
        return 1;
    }
    return 0; 
    
    
}

extern "C" int
subiso_vf2_weighted(// g1 is the subiso query,
                    int * g1_in, int * g1_label_in, int g1_n,
                    // g2 is the bigger graph,
                    int * g2_in, int * g2_label_in, int g2_n,
                    int *mapping_out, int * mapped_nodes,
                    double max_duration_secs = 0.0)
{
    SmartGraph g1; 
    SmartGraph::NodeMap<int> l1(g1);
    SmartGraph::NodeMap<int> p1(g1);
    SmartGraph::EdgeMap<int> w1(g1);
    array_to_g(g1_in, g1_label_in, g1_n, g1, l1, p1, w1);
   
    SmartGraph g2; 
    SmartGraph::NodeMap<int> l2(g2);
    SmartGraph::NodeMap<int> p2(g2);
    SmartGraph::EdgeMap<int> w2(g2);
    
    array_to_g(g2_in, g2_label_in, g2_n, g2, l2, p2, w2);

    SmartGraph::NodeMap<SmartGraph::Node> iso_g1_to_g2(g1,INVALID);
    *mapped_nodes = 0;

    bool is_subiso = is_subiso_weighted(g1, l1, w1,
                                        g2, l2, w2, iso_g1_to_g2,
                                        max_duration_secs);
    
    if (is_subiso) { 
        for (SmartGraph::NodeIt n(g1); n!=INVALID; ++n){
            if(iso_g1_to_g2[n] ==INVALID) {
                assert(false);
                // we should never get here, there should always
                // be a mapping
            }
            mapping_out[p1[n]] =  p2[iso_g1_to_g2[n]]; 
        }
        *mapped_nodes = g1_n; 
        return 1;
    }
    return 0; 
    
    
}


bool is_subiso(SmartGraph & g1, SmartGraph::NodeMap<int> & l1, // smaller
               SmartGraph & g2, SmartGraph::NodeMap<int> & l2) // bigger
{
    auto vf2obj = vf2pp(g1, g2);

    SmartGraph::NodeMap<SmartGraph::Node> iso(g1,INVALID);
    vf2obj.mapping(iso).nodeLabels(l1, l2).run();
    
    return my_checksubiso(g1, g2, iso);
    
}

int which_edges_subiso(int * g_full_in,
                       int * g_sub_in,
                       int * g_label_in, 
                       int * g_skip, int g_n,
                       int * possible_edge_out)
{
    /*
      which edges could we add to 
     */
    SmartGraph full_g; 
    SmartGraph::NodeMap<int> full_g_l(full_g);
    SmartGraph::NodeMap<int> full_g_pos(full_g);
    SmartGraph::EdgeMap<int> full_g_w(full_g); 
    array_to_g(g_full_in, g_label_in, g_n, full_g,
               full_g_l, full_g_pos, full_g_w);

    SmartGraph sub_g; 
    SmartGraph::NodeMap<int> sub_g_l(sub_g);
    SmartGraph::NodeMap<int> sub_g_pos(sub_g);
    SmartGraph::EdgeMap<int> sub_g_w(sub_g);
    
    array_to_g(g_sub_in, g_label_in,
               g_n,
               sub_g, sub_g_l,
               sub_g_pos, sub_g_w);

    // sanity check
    assert(is_subiso(sub_g, sub_g_l, full_g, full_g_l)); 


    SmartGraph::EdgeMap<int> out_map(sub_g);


    for (SmartGraph::NodeIt u(sub_g); u != INVALID; ++u) { 
        for (SmartGraph::NodeIt v(sub_g); v != INVALID; ++v) {
            size_t out_edge_ij = sub_g_pos[u] * g_n + sub_g_pos[v];
            // std::cout << "out_edge_ij=" << out_edge_ij << " sub_g_l[u]=" << sub_g_l[u]
            //           << " sub_g_l[v]=" << sub_g_l[v] << std::endl; 
            if (!(u < v)) {
                // not an edge
                possible_edge_out[out_edge_ij] = 0; 
                continue; 
            }

            if (g_skip[out_edge_ij] > 0) {
                // not an edge
                possible_edge_out[out_edge_ij] = 0; 
                continue; 
            }

            // copy the graph FIXME is this a place we could use checkpointing?
            
            SmartGraph candidate_g; 
            
            SmartGraph::NodeMap<SmartGraph::Node> nr(sub_g);
            SmartGraph::NodeMap<int> candidate_g_l(candidate_g);
            SmartGraph::EdgeMap<int> candidate_g_w(candidate_g);
            GraphCopy<SmartGraph, SmartGraph>
                cg(sub_g, candidate_g); 
            cg.nodeRef(nr)
                .nodeMap(sub_g_l, candidate_g_l)
                .edgeMap(sub_g_w, candidate_g_w)
                .run();
                
            SmartGraph::Edge new_edge = findEdge(candidate_g,
                                                 nr[u], nr[v]); 
            if(new_edge == INVALID) {
                // edge does not exist
                new_edge = candidate_g.addEdge(nr[u], nr[v]);
            }
            candidate_g_w[new_edge] += 1;

            SmartGraph::NodeMap<SmartGraph::Node>
                dummy_iso(candidate_g, INVALID); 
            if(is_subiso_multi(candidate_g, candidate_g_l, candidate_g_w,
                               full_g, full_g_l, full_g_w, dummy_iso)) {
                possible_edge_out[out_edge_ij] = 1;
            } else {
                possible_edge_out[out_edge_ij] = 0;                
            }
                
            
        }
    }
    
    
    return 0; 

}


void weighted_to_bipartite(SmartGraph & g_in,
                           SmartGraph::NodeMap<int> & l_in,
                           SmartGraph::EdgeMap<int> & w_in,
                           SmartGraph & g_out,
                           SmartGraph::NodeMap<int> & l_out,
                           SmartGraph::NodeMap<SmartGraph::Node> &node_out_in,
                           SmartGraph::NodeMap<int> & debug_out_pos, bool weight_to_multiedge)
{
    /*
      Turn the labeled input undirected weighted graph g into 
      a labeled unweighted bipartite graph 
    */

    // GraphCopy<SmartGraph, SmartGraph>
    //     cg(g_in, g_out); 
    // cg.nodeMap(l_in, l_out).run();
    SmartGraph::NodeMap<SmartGraph::Node> n_in_to_out(g_in);
    int pos = 0; 
    for (SmartGraph::NodeIt u(g_in); u != INVALID; ++u) {
        auto n_g_out = g_out.addNode();
        n_in_to_out[u] = n_g_out;
        l_out[n_g_out] = l_in[u];
        node_out_in[n_g_out] = u; 
        if(l_in[u] < 0) {
            throw std::runtime_error("labels can't be negative"); 
        }

        debug_out_pos[n_g_out] = pos;
        pos++; 
    }

    for (SmartGraph::EdgeIt e(g_in); e != INVALID; ++e) {
        // for this edge
        auto n1 = n_in_to_out[g_in.u(e)];
        auto n2 = n_in_to_out[g_in.v(e)];
        int weight = w_in[e];
        if (weight_to_multiedge) {
            // multiple nodes per weight
            for (int j = 0; j < weight; ++j) { 
                auto n_g_out = g_out.addNode();
                l_out[n_g_out] = 1000; // FIXME is there some better sentinel value? should these be connected? 
                g_out.addEdge(n1, n_g_out);
                g_out.addEdge(n_g_out, n2);
                debug_out_pos[n_g_out] = -1; 
            }
        } else {
            auto n_g_out = g_out.addNode();
            l_out[n_g_out] = 1000 + weight; // FIXME is there some better sentinel value? should these be connected? 
            g_out.addEdge(n1, n_g_out);
            g_out.addEdge(n_g_out, n2);
            debug_out_pos[n_g_out] = -1; 
        }
    }

}


bool is_subiso_multi(SmartGraph & g1,
                     SmartGraph::NodeMap<int> & l1,
                     SmartGraph::EdgeMap<int> & w1, // smaller
                     SmartGraph & g2,
                     SmartGraph::NodeMap<int> & l2,
                     SmartGraph::EdgeMap<int> & w2,
                     SmartGraph::NodeMap<SmartGraph::Node> & iso_out)
{
    /*
      take in two weighted graphs and see if they are subisomorphic by
      adding per-edge label types

      note the mapping might be a bit wonky and we should investigate
     */

    SmartGraph g1_bp; 
    SmartGraph::NodeMap<int> g1_bp_l(g1_bp);
    SmartGraph::NodeMap<int> g1_bp_pos(g1_bp, -1); 
    SmartGraph::NodeMap<SmartGraph::Node> g1_bp_to_g1(g1_bp, INVALID); 
    weighted_to_bipartite(g1, l1, w1,
                          g1_bp, g1_bp_l, g1_bp_to_g1,
                          g1_bp_pos, true); 
        
    SmartGraph g2_bp; 
    SmartGraph::NodeMap<int> g2_bp_l(g2_bp);
    SmartGraph::NodeMap<int> g2_bp_pos(g2_bp, -1); 
    SmartGraph::NodeMap<SmartGraph::Node> g2_bp_to_g2(g2_bp, INVALID); 

    weighted_to_bipartite(g2, l2, w2,
                          g2_bp, g2_bp_l,
                          g2_bp_to_g2, g2_bp_pos, true); 

    auto vf2obj = vf2pp(g1_bp, g2_bp);

    SmartGraph::NodeMap<SmartGraph::Node> iso_bp(g1_bp, INVALID);
    vf2obj.mapping(iso_bp).nodeLabels(g1_bp_l, g2_bp_l).run();

    bool is_subiso = my_checksubiso(g1_bp, g2_bp, iso_bp);
    int pos = 0; 
    if(is_subiso) {
        for (SmartGraph::NodeIt n(g1_bp); n!=INVALID; ++n){

            if(iso_bp[n] ==INVALID) {
                assert(false);
                // we should never get here, there should always
                // be a mapping
            }
            if (g1_bp_to_g1[n] == INVALID) {
                continue;
            }
            if (g2_bp_to_g2[iso_bp[n]] == INVALID) {
                continue;
            }

            if (g1_bp_pos[n] >= 0) { 
                iso_out[g1_bp_to_g1[n]] = g2_bp_to_g2[iso_bp[n]]; 
            }
            pos++; 
        }
    }
    
    return is_subiso; 
}

// bool is_subiso_multi2(SmartGraph & g1,
//                      SmartGraph::NodeMap<int> & l1,
//                      SmartGraph::EdgeMap<int> & w1, // smaller
//                      SmartGraph & g2,
//                      SmartGraph::NodeMap<int> & l2,
//                      SmartGraph::EdgeMap<int> & w2,
//                      SmartGraph::NodeMap<SmartGraph::Node> & iso_out)
// {
//     /*
//       can we find multiple subisomorphisms
//      */

//     SmartGraph g1_bp; 
//     SmartGraph::NodeMap<int> g1_bp_l(g1_bp);
//     SmartGraph::NodeMap<int> g1_bp_pos(g1_bp, -1); 
//     SmartGraph::NodeMap<SmartGraph::Node> g1_bp_to_g1(g1_bp, INVALID); 
//     weighted_to_bipartite(g1, l1, w1,
//                           g1_bp, g1_bp_l, g1_bp_to_g1,
//                           g1_bp_pos, true); 
        
//     SmartGraph g2_bp; 
//     SmartGraph::NodeMap<int> g2_bp_l(g2_bp);
//     SmartGraph::NodeMap<int> g2_bp_pos(g2_bp, -1); 
//     SmartGraph::NodeMap<SmartGraph::Node> g2_bp_to_g2(g2_bp, INVALID); 

//     weighted_to_bipartite(g2, l2, w2,
//                           g2_bp, g2_bp_l,
//                           g2_bp_to_g2, g2_bp_pos, true); 

//     concepts::ReadWriteMap<SmartGraph::Node,
//                            SmartGraph::Node> r;

//     SmartGraph::NodeMap<SmartGraph::Node> iso_bp(g1_bp, INVALID);
    
//     Vf2pp<SmartGraph,SmartGraph,
//           //concepts::ReadWriteMap<SmartGraph::Node, SmartGraph::Node>,
//           SmartGraph::NodeMap<SmartGraph::Node>, 
//           SmartGraph::NodeMap<int>,
//           SmartGraph::NodeMap<int> >
        
//         myVf2pp(g1_bp, g2_bp, iso_bp, g1_bp_l, g2_bp_l);

//     myVf2pp.find(); 


//     bool is_subiso = my_checksubiso(g1_bp, g2_bp, iso_bp);
//     int pos = 0; 
//     if(is_subiso) {
//         for (SmartGraph::NodeIt n(g1_bp); n!=INVALID; ++n){

//             if(iso_bp[n] ==INVALID) {
//                 assert(false);
//                 // we should never get here, there should always
//                 // be a mapping
//             }
//             if (g1_bp_to_g1[n] == INVALID) {
//                 continue;
//             }
//             if (g2_bp_to_g2[iso_bp[n]] == INVALID) {
//                 continue;
//             }

//             if (g1_bp_pos[n] >= 0) { 
//                 iso_out[g1_bp_to_g1[n]] = g2_bp_to_g2[iso_bp[n]]; 
//             }
//             pos++; 
//         }
//     }
    
//     return is_subiso; 
// }

bool is_subiso_weighted(SmartGraph & g1,
                        SmartGraph::NodeMap<int> & l1,
                        SmartGraph::EdgeMap<int> & w1, // smaller
                        SmartGraph & g2,
                        SmartGraph::NodeMap<int> & l2,
                        SmartGraph::EdgeMap<int> & w2,
                        SmartGraph::NodeMap<SmartGraph::Node> & iso_out,
                        double max_duration_sec = 0.0)
{
    /*
      take in two weighted graphs and see if they are subisomorphic by
      adding per-edge label types

      note the mapping might be a bit wonky and we should investigate
     */

    SmartGraph g1_bp; 
    SmartGraph::NodeMap<int> g1_bp_l(g1_bp);
    SmartGraph::NodeMap<int> g1_bp_pos(g1_bp, -1); 
    SmartGraph::NodeMap<SmartGraph::Node> g1_bp_to_g1(g1_bp, INVALID); 
    weighted_to_bipartite(g1, l1, w1,
                          g1_bp, g1_bp_l, g1_bp_to_g1,
                          g1_bp_pos, false); 
        
    SmartGraph g2_bp; 
    SmartGraph::NodeMap<int> g2_bp_l(g2_bp);
    SmartGraph::NodeMap<int> g2_bp_pos(g2_bp, -1); 
    SmartGraph::NodeMap<SmartGraph::Node> g2_bp_to_g2(g2_bp, INVALID); 

    weighted_to_bipartite(g2, l2, w2,
                          g2_bp, g2_bp_l,
                          g2_bp_to_g2, g2_bp_pos, false); 

    auto vf2obj = vf2pp(g1_bp, g2_bp);

    SmartGraph::NodeMap<SmartGraph::Node> iso_bp(g1_bp, INVALID);
    vf2obj.mapping(iso_bp).nodeLabels(g1_bp_l, g2_bp_l).run(max_duration_sec);

    bool is_subiso = my_checksubiso(g1_bp, g2_bp, iso_bp);
    int pos = 0; 
    if(is_subiso) {
        for (SmartGraph::NodeIt n(g1_bp); n!=INVALID; ++n){

            if(iso_bp[n] ==INVALID) {
                assert(false);
                // we should never get here, there should always
                // be a mapping
            }
            if (g1_bp_to_g1[n] == INVALID) {
                continue;
            }
            if (g2_bp_to_g2[iso_bp[n]] == INVALID) {
                continue;
            }

            if (g1_bp_pos[n] >= 0) { 
                iso_out[g1_bp_to_g1[n]] = g2_bp_to_g2[iso_bp[n]]; 
            }
            pos++; 
        }
    }
    
    return is_subiso; 
}

int which_edges_subiso_labeled(int * g_full_in,
                               int * g_sub_in,
                               int * g_label_in, 
                               int * g_skip, int g_n,
                               int * possible_weights,
                               int possible_weight_n, 
                               int * possible_edge_out,
                               float max_run_sec)
{
    /*
      Which edges can we add between various nodes
      that are not currently connected. 

      output will be g_n * g_n * possible_weight_n
      
     */


    auto time_start = std::chrono::steady_clock::now();


    SmartGraph full_g; 
    SmartGraph::NodeMap<int> full_g_l(full_g);
    SmartGraph::NodeMap<int> full_g_pos(full_g);
    SmartGraph::EdgeMap<int> full_g_w(full_g); 
    array_to_g(g_full_in, g_label_in, g_n, full_g,
               full_g_l, full_g_pos, full_g_w);

    SmartGraph sub_g; 
    SmartGraph::NodeMap<int> sub_g_l(sub_g);
    SmartGraph::NodeMap<int> sub_g_pos(sub_g);
    SmartGraph::EdgeMap<int> sub_g_w(sub_g);
    
    array_to_g(g_sub_in, g_label_in,
               g_n,
               sub_g, sub_g_l,
               sub_g_pos, sub_g_w);

    // sanity check
    assert(is_subiso(sub_g, sub_g_l, full_g, full_g_l)); 


    SmartGraph::EdgeMap<int> out_map(sub_g);


    for (SmartGraph::NodeIt u(sub_g); u != INVALID; ++u) { 
        for (SmartGraph::NodeIt v(sub_g); v != INVALID; ++v) {
            for (int weight_i = 0; weight_i < possible_weight_n; ++weight_i) {
                int proposed_weight = possible_weights[weight_i]; 
                size_t out_edge_ij = sub_g_pos[u] * g_n + sub_g_pos[v]; 
                size_t out_edge_ijw = sub_g_pos[u] * g_n * possible_weight_n + sub_g_pos[v]*possible_weight_n + weight_i;

                //std::cout << std::endl << "examiing"  <<  "(" << sub_g_pos[u] << "," << sub_g_pos[v] << ","
                //          << weight_i <<  " val=" << proposed_weight << ")" ; 
                if (!(u < v)) {
                    // not an edge
                    possible_edge_out[out_edge_ijw] = 0;
                    //std::cout << " symmetric" ;
                    continue; 
                }
                
                if (g_skip[out_edge_ijw] > 0) {
                    // not an edge
                    possible_edge_out[out_edge_ijw] = 0; 
                    //std::cout << " skip" ; 
                    continue; 
                }
                //std::cout << " checking (" << sub_g_pos[u]  << "," << sub_g_pos[v] << ")" << std::endl; ; 
                
                // copy the graph FIXME is this a place we could use checkpointing?
            
                SmartGraph candidate_g; 


                auto time_end = std::chrono::steady_clock::now();
                auto duration_ns = std::chrono::duration_cast<std::chrono::nanoseconds> (time_end - time_start);
                double duration_sec = double(duration_ns.count())/1e9;
                double remaining_time_sec = max_run_sec - duration_sec; 
                if( (max_run_sec > 0) & (remaining_time_sec <= 0)) {
                    return -1; 
                }
                
                SmartGraph::NodeMap<SmartGraph::Node> nr(sub_g);
                SmartGraph::NodeMap<int> candidate_g_l(candidate_g);
                SmartGraph::EdgeMap<int> candidate_g_w(candidate_g);
                GraphCopy<SmartGraph, SmartGraph>
                    cg(sub_g, candidate_g); 
                cg.nodeRef(nr)
                    .nodeMap(sub_g_l, candidate_g_l)
                    .edgeMap(sub_g_w, candidate_g_w)
                    .run();
                
                SmartGraph::Edge new_edge = findEdge(candidate_g,
                                                     nr[u], nr[v]);
                assert(new_edge == INVALID); 
                new_edge = candidate_g.addEdge(nr[u], nr[v]);
                candidate_g_w[new_edge] = proposed_weight;
                SmartGraph::NodeMap<SmartGraph::Node>
                    dummy_iso(candidate_g, INVALID);

                auto calc_time_start =  std::chrono::steady_clock::now();
                try {
                    if(is_subiso_weighted(candidate_g, candidate_g_l, candidate_g_w,
                                          full_g, full_g_l, full_g_w, dummy_iso, remaining_time_sec)) {
                        //std::cout << " is subiso"; 
                        possible_edge_out[out_edge_ijw] = 1;
                    } else {
                        //std::cout << " is not subiso"; 
                        possible_edge_out[out_edge_ijw] = 0;                
                    }
                } catch (const std::runtime_error& error) {
                    return -1; 
                }
                auto calc_time_end =  std::chrono::steady_clock::now();

                auto calc_duration_ns = std::chrono::duration_cast<std::chrono::nanoseconds> (calc_time_end - calc_time_start);
                float calc_dur_ms = float(calc_duration_ns.count())/1e6;
                if (calc_dur_ms > 10.0) { 
                    // std::cout << "checking " << sub_g_pos[u]
                    //           << " " << sub_g_pos[v]
                    //           << " " <<  weight_i << " took " << calc_dur_ms
                    //           << " was subiso? " << possible_edge_out[out_edge_ijw] << std::endl ;
                }
                

            }
        }
    }
    
    
    return 0; 

}
