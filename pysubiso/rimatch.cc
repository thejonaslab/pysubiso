/*
Copyright (c) 2014 by Rosalba Giugno

This library contains portions of other open source products covered by separate
licenses. Please see the corresponding source files for specific terms.

RI is provided under the terms of The MIT License (MIT):

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>
#include <ctime>


#include <stdio.h>
#include <stdlib.h>
#include "rimatch.h"
#include "c_textdb_driver.h"
#include "timer.h"


#include "AttributeComparator.h"
#include "AttributeDeconstructor.h"
#include "Graph.h"
#include "MatchingMachine.h"
#include "MaMaConstrFirst.h"
#include "Match.h"

//#define FIRST_MATCH_ONLY  //if setted, the searching process stops at the first found match
#include "Solver.h"
#include "IsoGISolver.h"
#include "SubGISolver.h"
#include "InducedSubGISolver.h"

#define PRINT_MATCHES
//#define CSV_FORMAT


#include <set>
#include <vector>

using namespace rilib;


void usage(char* args0);

/*
  A quick guide to graph:

  Graph appears to represent the graph as an array
  o

  nof_nodes : number of nodes (int)
  node_attrs: array of pointers to whatever the node labels are 
              (in our case ints)


  unsigned int* out_adj_sizes : array of the number of out-edges for each node
  unsigned int* in_adj_sizes; array of the number of in-edges for each node

  these are the same due to our graphs being undirected

  int** out_adj_list : array of arrays of out edges 
  int** in_adj_list : array of arrays of in edges
  void*** out_adj_attrs; array of arrays of pointers to edge properties

 */


int read_adj(unsigned int N, int * adj, int * vertlabel, 
             Graph* graph, int extra_edge_pad = 0){
    /*
      New code for reading an adjaceny matrix of labeled nodes
      and edges. 

      extra_edge_pad adds that many entries onto every array
      designed to handle some number of edges, so we can 
      later do incremental edge addition and removal 
      
     */
    
    graph->nof_nodes = N;

    
	// Allocate the space for the node labels and set the values.
    // Our node labels are only integers

	graph->nodes_attrs = (void**)malloc(graph->nof_nodes * sizeof(void*));
    for(unsigned int i=0; i<graph->nof_nodes; i++){
        graph->nodes_attrs[i] = (int*)malloc(sizeof(int));
        *((int*)graph->nodes_attrs[i]) = vertlabel[i]; 
	}


	// edge size arrays
	graph->out_adj_sizes = (unsigned int*)calloc(graph->nof_nodes, sizeof(int));
	graph->in_adj_sizes = (unsigned int*)calloc(graph->nof_nodes, sizeof(int));

    unsigned int * out_current_pos = (unsigned int*)calloc(graph->nof_nodes, sizeof(int));
    unsigned int * in_current_pos = (unsigned int*)calloc(graph->nof_nodes, sizeof(int));

    // count in edges and out edges
    for (unsigned int i = 0; i < N; i++) {
        for (unsigned int j = 0; j < N; j++) {
            int label = adj[i * N + j];
            if (label > 0) {
                graph->out_adj_sizes[i]++; 
                graph->in_adj_sizes[j]++; 
            }
        }
    }

    
    graph->out_adj_list = (int**)malloc(graph->nof_nodes * sizeof(int*));
    graph->in_adj_list = (int**)malloc(graph->nof_nodes * sizeof(int*));
    graph->out_adj_attrs = (void***)malloc(graph->nof_nodes * sizeof(void**));

    // allocate them all first
    for (unsigned int i=0; i < N; i++){
        //reading degree and successors of vertex i
        // out_adj_list is just an array that maps node-> list of out edge node ids
        
        graph->out_adj_list[i] = (int*)calloc(graph->out_adj_sizes[i] + extra_edge_pad, sizeof(int));
     	graph->out_adj_attrs[i] = (void**)malloc((graph->out_adj_sizes[i] + extra_edge_pad) * sizeof(void*));

     	graph->in_adj_list[i] = (int*)calloc(graph->in_adj_sizes[i] + extra_edge_pad, sizeof(int));
    }
    for (unsigned int i=0; i < N; i++){
    
        for (unsigned int j=0; j < N; j++) {
            int label =  adj[i * N + j];
            if (label > 0) {
                graph->out_adj_list[i][out_current_pos[i]] = j;
                int * labelp = (int*)malloc(sizeof(int));
                *labelp = label; 
                graph->out_adj_attrs[i][out_current_pos[i]] = labelp;
                
                out_current_pos[i]++;
                
                graph->in_adj_list[j][in_current_pos[j]] = i;
                in_current_pos[j]++; 
               
            }
        }
    }
    

    free(out_current_pos);
    free(in_current_pos);

  return 0;
};




std::ostream& operator<<(std::ostream& os, const std::set<int> &s)
{
    for (auto const& i: s) {
        os << i << " ";
    }
    return os;
}

std::set<int> array_to_set(int * a, int N) {
    std::set<int> s;
    for(int i = 0; i < N; ++i) {
        s.insert(a[i]); 

    }
    return s;

}

void compare_graphs(Graph * g1, Graph * g2) {
    //std::cout << "comparing graphs: --------------------" << std::endl; 
    if (g1->nof_nodes == g2->nof_nodes) {
        //std::cout << "nof_nodes matches" << std::endl; 
    } else {
        std::cout << "g1.nof_nodes =" << g1->nof_nodes << " g2.nof_nodes=" << g2->nof_nodes<<std::endl; 
    }
    for (unsigned int i = 0; i < g1->nof_nodes; ++i) {
        if (g1->out_adj_sizes[i] != g2->out_adj_sizes[i]) {
            std::cout << "out_adj_size mismatch at " << i << std::endl; 
        }
        if (g1->in_adj_sizes[i] != g2->in_adj_sizes[i]) {
            std::cout << "in_adj_size mismatch at " << i << std::endl; 
        }

        auto g1_out_set = array_to_set(g1->out_adj_list[i], g1->out_adj_sizes[i]); 
        auto g2_out_set = array_to_set(g2->out_adj_list[i], g2->out_adj_sizes[i]);
        if (g1_out_set != g2_out_set) {
            std::cout << "i=" << i << " out sets don't match: "
                      << g1_out_set << " " << g2_out_set << std::endl; 
        }
        auto g1_in_set = array_to_set(g1->in_adj_list[i], g1->in_adj_sizes[i]); 
        auto g2_in_set = array_to_set(g2->in_adj_list[i], g2->in_adj_sizes[i]);
        if (g1_in_set != g2_in_set) {
            std::cout << "i=" << i << " in sets don't match: "
                      << g1_in_set << " " << g2_in_set << std::endl; 
        }
        
    }
    

}




int is_match(int query_N, int * query_adj, int * query_vertlabel,               
             int ref_N, int * ref_adj, int * ref_vertlabel,
             float max_time, int match_type)
{

    MATCH_TYPE     matchtype; 
    if (match_type == 0) {
        matchtype = MT_ISO;
    } else{
        matchtype = MT_MONO;
    }
    //GRAPH_FILE_TYPE filetype = GFT_EGFU;
    
	TIMEHANDLE //load_s, load_s_q,
        make_mama_s, match_s, total_s;
	//double load_t=0; //double load_t_q=0;
    double make_mama_t=0; double match_t=0; //double total_t=0;
	total_s=start_time();

	//int rret;

	AttributeComparator* nodeComparator;			//to compare node labels
	AttributeComparator* edgeComparator;			//to compare edge labels
    nodeComparator = new IntAttrComparator("node");
    edgeComparator = new IntAttrComparator("edge");

    
	Graph *query = new Graph();
    read_adj(query_N, query_adj, query_vertlabel, query);


	make_mama_s=start_time();
	MaMaConstrFirst* mama = new MaMaConstrFirst(*query);
	mama->build(*query);
	make_mama_t+=end_time(make_mama_s);


	long matchcount = 0; 		//nof found matches
        
	long tsteps = 0, ttriedcouples = 0, tmatchedcouples = 0;

    MatchListener* matchListener=new EmptyMatchListener(max_time);


    Graph * rrg = new Graph();
    read_adj(ref_N, ref_adj, ref_vertlabel, rrg); 

    //run the matching
    match_s=start_time();
    match(	*rrg,
            *query,
            *mama,
            *matchListener,
            matchtype,
            *nodeComparator,
            *edgeComparator,
            &tsteps,
            &ttriedcouples,
            &tmatchedcouples);
    match_t+=end_time(match_s);
    
    delete mama;
    delete query;
    delete rrg; 
    
    delete nodeComparator;
    delete edgeComparator;

	matchcount = matchListener->matchcount;
        
    if (matchListener->timeout) {
        delete matchListener;         
        throw std::runtime_error("timeout"); 
    }

    double total_t = 0.0;
    total_t += end_time(total_s);
    double pct_not_in_match = (1 - match_t / total_t) * 100;

    delete matchListener; 
	return matchcount > 0 ;
};


int which_edges_indsubiso_incremental(int query_N, int * query_adj, int * query_vertlabel,               
                                      int ref_N, int * ref_adj, int * ref_vertlabel,
                                      int possible_edges_N, int * possible_edges,
                                      int * possible_edges_out, 
                                      float max_time)
{

    MATCH_TYPE     matchtype = MT_MONO;
    
	TIMEHANDLE match_s, total_s;
    double make_mama_t=0;
    double match_t=0; //double total_t=0;
	total_s=start_time();

    match_s = start_time(); 
    AttributeComparator* nodeComparator;			//to compare node labels
    AttributeComparator* edgeComparator;			//to compare edge labels
    nodeComparator = new IntAttrComparator("node");
    edgeComparator = new IntAttrComparator("edge");

    Graph * rrg = new Graph();
    read_adj(ref_N, ref_adj, ref_vertlabel, rrg); 

    Graph *query = new Graph();
    read_adj(query_N, query_adj, query_vertlabel, query, 2);
    
    
    for (unsigned int possible_i = 0; possible_i < possible_edges_N; ++possible_i) {

        


        int new_i = possible_edges[possible_i * 3 + 0];
        int new_j = possible_edges[possible_i * 3 + 1];
        int new_c = possible_edges[possible_i * 3 + 2];

        int * edge_i_label = (int*)malloc(sizeof(int));
        *edge_i_label = new_c;

        query->out_adj_list[new_i][query->out_adj_sizes[new_i]] = new_j;
        query->out_adj_attrs[new_i][query->out_adj_sizes[new_i]] = edge_i_label;
        query->out_adj_sizes[new_i]++;

        query->in_adj_list[new_j][query->in_adj_sizes[new_j]] = new_i; 
        query->in_adj_sizes[new_j]++; 

        int * edge_j_label = (int*)malloc(sizeof(int));
        *edge_j_label = new_c;
        query->out_adj_list[new_j][query->out_adj_sizes[new_j]] = new_i;
        query->out_adj_attrs[new_j][query->out_adj_sizes[new_j]] = edge_j_label;
        query->out_adj_sizes[new_j]++;
        
        query->in_adj_list[new_i][query->in_adj_sizes[new_i]] = new_j; 
        query->in_adj_sizes[new_i]++;

        MaMaConstrFirst* mama = new MaMaConstrFirst(*query);
        mama->build(*query);

        long matchcount = 0; 		
        double thus_far_t = end_time(match_s);
        if (thus_far_t > max_time) {
            delete mama;
            delete query;
            delete rrg; 
            
            delete nodeComparator;
            delete edgeComparator;

            
            throw std::runtime_error("timeout"); 

        }
        
        MatchListener* matchListener=new EmptyMatchListener(max_time - thus_far_t);
        long tsteps = 0, ttriedcouples = 0, tmatchedcouples = 0;


        match(	*rrg,
                *query,
                *mama,
                *matchListener,
                matchtype,
                *nodeComparator,
                *edgeComparator,
                &tsteps,
                &ttriedcouples,
                &tmatchedcouples);

        matchcount = matchListener->matchcount;

        possible_edges_out[possible_i] = (matchcount > 0);

        if (matchListener->timeout) {
            delete mama;
            delete matchListener;
            delete query;
            delete rrg; 
            
            delete nodeComparator;
            delete edgeComparator;

            throw std::runtime_error("timeout"); 
        }
        

        // then undo this
        query->out_adj_sizes[new_i]--; 
        query->out_adj_sizes[new_j]--;
        query->in_adj_sizes[new_i]--;
        query->in_adj_sizes[new_j]--; 
        free(edge_i_label);
        free(edge_j_label); 
        
        delete mama;
        delete matchListener;

    }
        
    delete query;
    delete rrg; 

    delete nodeComparator;
    delete edgeComparator;
        


        

    double total_t = 0.0;
    total_t += end_time(total_s);
    double pct_not_in_match = (1 - match_t / total_t) * 100;


	return 0; 
};









