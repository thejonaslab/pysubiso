#pragma once

int is_indsubiso(int query_N, int * query_adj, int * query_vertlabel,               
              int ref_N, int * ref_adj, int * ref_vertlabel, float maxtime);
int old_match(std::string& referencefile,	std::string& queryfile);
