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
#include "ritest.h"
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



using namespace rilib;


void usage(char* args0);




int old_read_egfu(const char* fileName, FILE* fd, Graph* graph){
	char str[STR_READ_LENGTH];
	int i,j;

	if (fscanf(fd,"%s",str) != 1){	//#graphname
		return -1;
	}
	if (fscanf(fd,"%d",&(graph->nof_nodes)) != 1){//nof nodes
		return -1;
	}

	//node labels
	graph->nodes_attrs = (void**)malloc(graph->nof_nodes * sizeof(void*));
	char *label = new char[STR_READ_LENGTH];
	for(i=0; i<graph->nof_nodes; i++){
		if (fscanf(fd,"%s",label) != 1){
			return -1;
		}
    graph->nodes_attrs[i] = (char*)malloc((strlen(label) + 1) * sizeof(char));
    strcpy((char*)graph->nodes_attrs[i], label);
	}

	//edges
	graph->out_adj_sizes = (int*)calloc(graph->nof_nodes, sizeof(int));
	graph->in_adj_sizes = (int*)calloc(graph->nof_nodes, sizeof(int));

	egr_neighs_t **ns_o = (egr_neighs_t**)malloc(graph->nof_nodes * sizeof(egr_neighs_t));
  egr_neighs_t **ns_i = (egr_neighs_t**)malloc(graph->nof_nodes * sizeof(egr_neighs_t));
	for(i=0; i<graph->nof_nodes; i++){
		ns_o[i] = NULL;
    ns_i[i] = NULL;
	}
	int temp = 0;
	if (fscanf(fd,"%d",&temp) != 1){//number of edges
		return -1;
	}

	int es = 0, et = 0;
	for(i=0; i<temp; i++){
		if (fscanf(fd,"%d",&es) != 1){//source node
			return -1;
		}
		if (fscanf(fd,"%d",&et) != 1){//target node
			return -1;
		}
		if (fscanf(fd,"%s",label) != 1){
			return -1;
		}

		graph->out_adj_sizes[es]++;
		graph->in_adj_sizes[et]++;

		if(ns_o[es] == NULL){
			ns_o[es] = (egr_neighs_t*)malloc(sizeof(egr_neighs_t));
			ns_o[es]->nid = et;
			ns_o[es]->next = NULL;
			ns_o[es]->label = (char*)malloc((strlen(label) + 1) * sizeof(char));
      strcpy(ns_o[es]->label, label);
		}
		else{
			egr_neighs_t* n = (egr_neighs_t*)malloc(sizeof(egr_neighs_t));
			n->nid = et;
			n->next = (struct egr_neighs_t*)ns_o[es];
      n->label = (char*)malloc((strlen(label) + 1) * sizeof(char));
      strcpy(n->label, label);
			ns_o[es] = n;
		}

		graph->out_adj_sizes[et]++;
		graph->in_adj_sizes[es]++;

		if(ns_o[et] == NULL){
			ns_o[et] = (egr_neighs_t*)malloc(sizeof(egr_neighs_t));
			ns_o[et]->nid = es;
			ns_o[et]->next = NULL;
      ns_o[et]->label = (char*)malloc((strlen(label) + 1) * sizeof(char));
      strcpy((char*)ns_o[et]->label, label);
		}
		else{
			egr_neighs_t* n = (egr_neighs_t*)malloc(sizeof(egr_neighs_t));
			n->nid = es;
			n->next = (struct egr_neighs_t*)ns_o[et];
      n->label = (char*)malloc((strlen(label) + 1) * sizeof(char));
      strcpy((char*)n->label, label);
			ns_o[et] = n;
		}

	}


	graph->out_adj_list = (int**)malloc(graph->nof_nodes * sizeof(int*));
	graph->in_adj_list = (int**)malloc(graph->nof_nodes * sizeof(int*));
	graph->out_adj_attrs = (void***)malloc(graph->nof_nodes * sizeof(void**));

	int* ink = (int*)calloc(graph->nof_nodes, sizeof(int));
	for (i=0; i<graph->nof_nodes; i++){
		graph->in_adj_list[i] = (int*)calloc(graph->in_adj_sizes[i], sizeof(int));

	}
	for (i=0; i<graph->nof_nodes; i++){
		// reading degree and successors of vertex i
		graph->out_adj_list[i] = (int*)calloc(graph->out_adj_sizes[i], sizeof(int));
		graph->out_adj_attrs[i] = (void**)malloc(graph->out_adj_sizes[i] * sizeof(void*));

		egr_neighs_t *n = ns_o[i];
		for (j=0; j<graph->out_adj_sizes[i]; j++){
			graph->out_adj_list[i][j] = n->nid;
			graph->out_adj_attrs[i][j] = n->label;

			graph->in_adj_list[n->nid][ink[n->nid]] = i;

			ink[n->nid]++;

			n = n->next;
		}
	}

//	graph->sort_edges();



	for(int i=0; i<graph->nof_nodes; i++){
		if(ns_o[i] != NULL){
			egr_neighs_t *p = NULL;
			egr_neighs_t *n = ns_o[i];
			for (j=0; j<graph->out_adj_sizes[i]; j++){
				if(p!=NULL)
					free(p);
				p = n;
				n = n->next;
			}
			if(p!=NULL)
			free(p);
		}

		if(ns_i[i] != NULL){
			egr_neighs_t *p = NULL;
			egr_neighs_t *n = ns_i[i];
			for (j=0; j<graph->out_adj_sizes[i]; j++){
				if(p!=NULL)
					free(p);
				p = n;
				n = n->next;
			}
			if(p!=NULL)
			free(p);
		}


//			free(ns_o);
//			free(ns_i);
	}
  
  free(ns_o);
  free(ns_i);
  free(ink);
  delete[] label;
	return 0;
};

int read_egfu_adj(int N, int * adj, int * vertlabel, 
                  Graph* graph){
	char str[STR_READ_LENGTH];
	int i,j;

	// if (fscanf(fd,"%s",str) != 1){	//#graphname
	// 	return -1;
	// }
	// if (fscanf(fd,"%d",&(graph->nof_nodes)) != 1){//nof nodes
	// 	return -1;
	// }
    graph->nof_nodes = N;

    
	//node labels
    // FIXME integers or arrays of integers? 
	graph->nodes_attrs = (void**)malloc(graph->nof_nodes * sizeof(void*));
	// char *label = new char[STR_READ_LENGTH];
    for(i=0; i<graph->nof_nodes; i++){
        graph->nodes_attrs[i] = (int*)malloc(sizeof(int));
        *((int*)graph->nodes_attrs[i]) = vertlabel[i]; 
	}

	//edges
	graph->out_adj_sizes = (int*)calloc(graph->nof_nodes, sizeof(int));
	graph->in_adj_sizes = (int*)calloc(graph->nof_nodes, sizeof(int));

	egr_neighs_t **ns_o = (egr_neighs_t**)malloc(graph->nof_nodes * sizeof(egr_neighs_t));
    egr_neighs_t **ns_i = (egr_neighs_t**)malloc(graph->nof_nodes * sizeof(egr_neighs_t));
	for(i=0; i<graph->nof_nodes; i++){
		ns_o[i] = NULL;
        ns_i[i] = NULL;
	}
	int temp = 0;
    for (i = 0; i < N; i++) {
        for (j = i + 1; j < N; j++) {
            if (adj[i * N + j]  > 0) {
                temp += 1; 
            }
        }
    }

    for (i = 0; i < N; i++) {
        for (j = i + 1; j < N; j++) {
            int label = adj[i * N + j]; 
            if (label  > 0) {
                
                int es = i;
                int et = j;

                // one direction
                graph->out_adj_sizes[es]++;
                graph->in_adj_sizes[et]++;

                if(ns_o[es] == NULL){
                    ns_o[es] = (egr_neighs_t*)malloc(sizeof(egr_neighs_t));
                    ns_o[es]->nid = et;
                    ns_o[es]->next = NULL;
                    ns_o[es]->label = (char*)malloc(sizeof(int));
                    *(ns_o[es]->label) = label;
                }
                else{
                    egr_neighs_t* n = (egr_neighs_t*)malloc(sizeof(egr_neighs_t));
                    n->nid = et;
                    n->next = (struct egr_neighs_t*)ns_o[es];
                    n->label =  (char*)malloc(sizeof(int));
                    *(n->label) = label; 
                    ns_o[es] = n;
                }

                // the other direction
                graph->out_adj_sizes[et]++;
                graph->in_adj_sizes[es]++;
                
                if(ns_o[et] == NULL){
                    ns_o[et] = (egr_neighs_t*)malloc(sizeof(egr_neighs_t));
                    ns_o[et]->nid = es;
                    ns_o[et]->next = NULL;
                    ns_o[et]->label = (char*)malloc(sizeof(int));
                    *(ns_o[et]->label) = label; 
                }
                else{
                    egr_neighs_t* n = (egr_neighs_t*)malloc(sizeof(egr_neighs_t));
                    n->nid = es;
                    n->next = (struct egr_neighs_t*)ns_o[et];
                    n->label =  (char*)malloc(sizeof(int));
                    *(n->label) = label; 
                    ns_o[et] = n;
                }
            }
        }
        
	}


	graph->out_adj_list = (int**)malloc(graph->nof_nodes * sizeof(int*));
	graph->in_adj_list = (int**)malloc(graph->nof_nodes * sizeof(int*));
	graph->out_adj_attrs = (void***)malloc(graph->nof_nodes * sizeof(void**));

	int* ink = (int*)calloc(graph->nof_nodes, sizeof(int));
	for (i=0; i<graph->nof_nodes; i++){
		graph->in_adj_list[i] = (int*)calloc(graph->in_adj_sizes[i], sizeof(int));

	}
	for (i=0; i<graph->nof_nodes; i++){
		// reading degree and successors of vertex i
		graph->out_adj_list[i] = (int*)calloc(graph->out_adj_sizes[i], sizeof(int));
		graph->out_adj_attrs[i] = (void**)malloc(graph->out_adj_sizes[i] * sizeof(void*));

		egr_neighs_t *n = ns_o[i];
		for (j=0; j<graph->out_adj_sizes[i]; j++){
			graph->out_adj_list[i][j] = n->nid;
			graph->out_adj_attrs[i][j] = n->label;
			graph->in_adj_list[n->nid][ink[n->nid]] = i;

			ink[n->nid]++;

			n = n->next;
		}
	}

//	graph->sort_edges();


    
	for(int i=0; i<graph->nof_nodes; i++){
		if(ns_o[i] != NULL){
			egr_neighs_t *p = NULL;
			egr_neighs_t *n = ns_o[i];
			for (j=0; j<graph->out_adj_sizes[i]; j++){
				if(p!=NULL)
					free(p);
				p = n;
				n = n->next;
			}
			if(p!=NULL)
			free(p);
		}

		if(ns_i[i] != NULL){
			egr_neighs_t *p = NULL;
			egr_neighs_t *n = ns_i[i];
			for (j=0; j<graph->out_adj_sizes[i]; j++){
				if(p!=NULL)
					free(p);
				p = n;
				n = n->next;
			}
			if(p!=NULL)
			free(p);
		}


//			free(ns_o);
//			free(ns_i);
	}
  
  free(ns_o);
  free(ns_i);
  free(ink);
  //delete[] label;
  return 0;
};


int othermain(int argc, char* argv[]){


	MATCH_TYPE matchtype;
	GRAPH_FILE_TYPE filetype;
	std::string reference;
	std::string query;

	// std::string par = argv[1];
	// if(par=="iso"){
	// 	matchtype = MT_ISO;
	// }
	// else if(par=="ind"){
	// 	matchtype = MT_INDSUB;
	// }
	// else if(par=="mono"){
    matchtype = MT_MONO;
	// }
	// else{
	// 	usage(argv[0]);
	// 	return -1;
	// }

	// par = argv[2];
	// if(par=="gfu"){
	// 	filetype = GFT_GFU;
	// }
	// else if(par=="gfd"){
	// 	filetype = GFT_GFD;
	// }
	// else if(par=="gfda"){
	// 		filetype = GFT_GFDA;
	// 	}
	// else if(par=="geu"){
    filetype = GFT_EGFU;
	// }
	// else if(par=="ged"){
	// 	filetype = GFT_EGFD;
	// }
	// else if(par=="vfu"){
	// 	filetype = GFT_VFU;
	// }
	// else{
	// 	usage(argv[0]);
	// 	return -1;
	// }

	reference = argv[3];
	query = argv[4];

	//return match(matchtype, filetype, reference, query);
};





void usage(char* args0){
	std::cout<<"usage "<<args0<<" [iso ind mono] [gfu gfd gfda geu ged vfu] reference query\n";
	std::cout<<"\tmatch type:\n";
	std::cout<<"\t\tiso = isomorphism\n";
	std::cout<<"\t\tind = induced subisomorphism\n";
	std::cout<<"\t\tmono = monomorphism\n";
	std::cout<<"\tgraph input format:\n";
	std::cout<<"\t\tgfu = undirect graphs with labels on nodes\n";
	std::cout<<"\t\tgfd = direct graphs with labels on nodes\n";
	std::cout<<"\t\tgfd = direct graphs with one single label on nodes\n";
	std::cout<<"\t\tgeu = undirect graphs with labels both on nodes and edges\n";
	std::cout<<"\t\tged = direct graphs with labels both on nodes and edges\n";
	std::cout<<"\t\tvfu = VF2Lib undirect unlabeled format\n";
	std::cout<<"\treference file contains one or more reference graphs\n";
	std::cout<<"\tquery contains the query graph (just one)\n";
};


// int old_match(
//               // MATCH_TYPE 			matchtype,
//               // GRAPH_FILE_TYPE 	filetype,
//               std::string& 		referencefile,
//               std::string& 	queryfile){
    
//     MATCH_TYPE 			matchtype= MT_MONO; 
//     GRAPH_FILE_TYPE 	filetype = GFT_EGFU;
    
// 	TIMEHANDLE load_s, load_s_q, make_mama_s, match_s, total_s;
// 	double load_t=0;double load_t_q=0; double make_mama_t=0; double match_t=0; double total_t=0;
// 	total_s=start_time();

// 	bool takeNodeLabels = false;
// 	bool takeEdgesLabels = false;
// 	int rret;

// 	AttributeComparator* nodeComparator;			//to compare node labels
// 	AttributeComparator* edgeComparator;			//to compare edge labels
// 	switch(filetype){
// 		case GFT_GFU:
// 		case GFT_GFD:
// 			// only nodes have labels and they are strings
// 			nodeComparator = new StringAttrComparator();
// 			edgeComparator = new DefaultAttrComparator();
// 			takeNodeLabels = true;
// 			break;
// 		case GFT_GFDA:
// 			nodeComparator = new DefaultAttrComparator();
// 			edgeComparator = new DefaultAttrComparator();
// 			takeNodeLabels = true;
// 			break;
// 		case GFT_EGFU:
// 		case GFT_EGFD:
// 			//labels on nodes and edges, both of them are strings
// 			nodeComparator = new StringAttrComparator();
// 			edgeComparator = new StringAttrComparator();
// 			takeNodeLabels = true;
// 			takeEdgesLabels = true;
// 			break;
// 		case GFT_VFU:
// 			//no labels
// 			nodeComparator = new DefaultAttrComparator();
// 			edgeComparator = new DefaultAttrComparator();
// 			break;
//     default:
//       return -1;
// 	}

// 	TIMEHANDLE tt_start;
// 	double tt_end;



// 	//read the query graph
// 	load_s_q=start_time();
// 	Graph *query = new Graph();
// 	rret = read_graph(queryfile.c_str(), query, filetype);
// 	load_t_q+=end_time(load_s_q);
// 	if(rret !=0){
// 		std::cout<<"error on reading query graph\n";
// 	}

// 	make_mama_s=start_time();
// 	MaMaConstrFirst* mama = new MaMaConstrFirst(*query);
// 	mama->build(*query);
// 	make_mama_t+=end_time(make_mama_s);

// 	//mama->print();

// 	long 	steps = 0,				//total number of steps of the backtracking phase
// 			triedcouples = 0, 		//nof tried pair (query node, reference node)
// 			matchcount = 0, 		//nof found matches
// 			matchedcouples = 0;		//nof mathed pair (during partial solutions)
// 	long tsteps = 0, ttriedcouples = 0, tmatchedcouples = 0;

// 	FILE *fd = open_file(referencefile.c_str(), filetype);
// 	if(fd != NULL){
// #ifdef PRINT_MATCHES
// 		//to print found matches on screen
// 		MatchListener* matchListener=new ConsoleMatchListener();
// #else
// 		//do not print matches, just count them
// 		MatchListener* matchListener=new EmptyMatchListener();
// #endif
// 		int i=0;
// 		bool rreaded = true;
// 		do{//for each reference graph inside the input file
// #ifdef PRINT_MATCHES
// 			std::cout<<"#"<<i<<"\n";
// #endif
// 			//read the next reference graph
// 			load_s=start_time();
// 			Graph * rrg = new Graph();
// 			int rret = read_dbgraph(referencefile.c_str(), fd, rrg, filetype);
// 			rreaded = (rret == 0);
// 			load_t+=end_time(load_s);
// 			if(rreaded){

// 					//run the matching
// 					match_s=start_time();
// 					match(	*rrg,
// 							*query,
// 							*mama,
// 							*matchListener,
// 							matchtype,
// 							*nodeComparator,
// 							*edgeComparator,
// 							&tsteps,
// 							&ttriedcouples,
// 							&tmatchedcouples);
// 					match_t+=end_time(match_s);

// 					//see rilib/Solver.h
// //					steps += tsteps;
// //					triedcouples += ttriedcouples;
// 					matchedcouples += tmatchedcouples;

// 				}
//         delete rrg;
				
// 			i++;
// 		}while(rreaded);

// 		matchcount = matchListener->matchcount;

// 		delete matchListener;

// 		fclose(fd);
// 	}
// 	else{
// 		std::cout<<"unable to open reference file\n";
// 		return -1;
// 	}

// 	total_t=end_time(total_s);

// #ifdef CSV_FORMAT
// 	std::cout<<referencefile<<"\t"<<queryfile<<"\t";
// 	std:cout<<load_t_q<<"\t"<<make_mama_t<<"\t"<<load_t<<"\t"<<match_t<<"\t"<<total_t<<"\t"<<steps<<"\t"<<triedcouples<<"\t"<<matchedcouples<<"\t"<<matchcount;
// #else
// 	std::cout<<"reference file: "<<referencefile<<"\n";
// 	std::cout<<"query file: "<<queryfile<<"\n";
// 	std::cout<<"total time: "<<total_t<<"\n";
// 	std::cout<<"matching time: "<<match_t<<"\n";
// 	std::cout<<"number of found matches: "<<matchcount<<"\n";
// 	std::cout<<"search space size: "<<matchedcouples<<"\n";
// #endif

// //	delete mama;
// //	delete query;

//   delete mama;
//   delete query;
  
//   delete nodeComparator;
//   delete edgeComparator;
  
// 	return 0;
// };


int is_subiso(int query_N, int * query_adj, int * query_vertlabel,               
              int ref_N, int * ref_adj, int * ref_vertlabel, float max_time)
{

    MATCH_TYPE     matchtype = MT_MONO;
    GRAPH_FILE_TYPE filetype = GFT_EGFU;
    
	TIMEHANDLE load_s, load_s_q, make_mama_s, match_s, total_s;
	double load_t=0;double load_t_q=0; double make_mama_t=0; double match_t=0; double total_t=0;
	total_s=start_time();

	int rret;

	AttributeComparator* nodeComparator;			//to compare node labels
	AttributeComparator* edgeComparator;			//to compare edge labels
    nodeComparator = new IntAttrComparator();
    edgeComparator = new IntAttrComparator();

    
	TIMEHANDLE tt_start;
	double tt_end;



	//read the query graph
	//load_s_q=start_time();
	Graph *query = new Graph();
    read_egfu_adj(query_N, query_adj, query_vertlabel, query); 
    // for(int i = 0; i <  query->nof_nodes; ++i) {
    //     std::cout << query-> out_adj_sizes[i] << std::endl; 
        
    // }
	// rret = read_graph(queryfile.c_str(), query, filetype);
	// load_t_q+=end_time(load_s_q);
	// if(rret !=0){
	// 	std::cout<<"error on reading query graph\n";
	// }

	make_mama_s=start_time();
	MaMaConstrFirst* mama = new MaMaConstrFirst(*query);
	mama->build(*query);
	make_mama_t+=end_time(make_mama_s);

	//mama->print();

	long 	steps = 0,				//total number of steps of the backtracking phase
			triedcouples = 0, 		//nof tried pair (query node, reference node)
			matchcount = 0, 		//nof found matches
			matchedcouples = 0;		//nof mathed pair (during partial solutions)
	long tsteps = 0, ttriedcouples = 0, tmatchedcouples = 0;

    //do not print matches, just count them
    //MatchListener* matchListener=new ConsoleMatchListener();
    
    MatchListener* matchListener=new EmptyMatchListener(max_time);

    int i=0;
    bool rreaded = true;
    //load_s=start_time();
    Graph * rrg = new Graph();
    read_egfu_adj(ref_N, ref_adj, ref_vertlabel, rrg); 

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
    
//	delete mama;
//	delete query;
    
    delete mama;
    delete query;
    
    delete nodeComparator;
    delete edgeComparator;

	matchcount = matchListener->matchcount;
        
    if (matchListener->timeout) {
        throw std::runtime_error("timeout"); 
    }
	return matchcount > 0 ;
};





