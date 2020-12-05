## Graph isomorphism and subgraph isomorphism

This is a library which attempts to unify all of our graph isomorphism
and subisomorphism code into one library with extensive tests and benchmarking, 
all from Python. 

Currently it wraps RI https://github.com/InfOmics/RI

but we would eventually like to wrap LEMON
https://lemon.cs.elte.hu/trac/lemon/wiki/Documentation

There are three "classes" of isomorphism we'll consider:

isomorphism: graphs are the same under some vertex permutation
- [graph isomorphism](https://en.wikipedia.org/wiki/Graph_isomorphism)
- [subgraph isomorphism](https://en.wikipedia.org/wiki/Subgraph_isomorphism_problem) : 
- [induced subgraph isomorphism](https://en.wikipedia.org/wiki/Induced_subgraph_isomorphism_problem)


We are mostly interested in the inducsed subgraph isomorphism problem, 
where a graph g can be subisomorphic even if it doesn't have all the edges
that G has. For example:

G : A - B - C -D

g : A - B   C 

g has induced graph subisomorphism to G but not "subgraph isomorphism" (as the
existence of an edge between B and C in G would not match the absence
of said edge in g. 

We assume our graphs are:
1. small
2. vertex-colored (unsigned ints)
3. edge-colored (unsigned ints)


Every function in our library takes an optional timeout
duration (in seconds) and will raise a pysubiso.TimeOut exception
if it is exceeded. 

Throughout this code, `gsub` is the smaller graph and `gmain`
is the graph we're trying to match to. 

API: 
```
m = pysubsio.Matcher(method='RI')

m.is_iso(g_sub_adj, g_sub_color,
         g_main_adj, g_main_color, timeout=1.0)
m.is_indsubsio(g_sub_adj, g_sub_color, 
               g_main_adj, g_main_color, timeout=1.0)
               
m.edge_add_indsubsio(g_sub_adj, g_sub_color, 
                            g_main_adj, g_main_color, 
                            possible_edges, timeout=1.0)
```

1. We do not allow self-loops
2. All graphs are undirected, and we only consider the upper-triangular
portion of the passed in adjaceny matrices
3. adj[i, j] = 0 means no edge, all other integers > 0 are edge labels. 



## TODO 
[x] Settle on an API which can switch between backends
[x] basic migration of RI code to new API 
[x] ~Write networkx impl [IMPOSSIBLE does not support induced subiso]~
[ ] port test suite to good file format
[x] migrate existing tests to new API
[x] Create tests 
[x] check subiso between differently-sized graphs
[ ] rename everything
[ ] fix timeout on subiso matching
[ ] normalize / unify test suite function naming
[x] split out nx helper funcs to a different module
[x] port lemon over
[ ] benchmark both
[ ] Clean up code to explort canonical graphs to benchmark

## Development
Option 1: Local Cython setup
- Install requirements
  - `python -m pip install -r requirements.txt`
- Build Cython extension locally
  - `python -m setup.py build_ext --inplace`

Option 2: Use setup.py
- `python setup.py build`
- `python setup.py install`

Running tests (after installation):
- `python test.py`

## Installation
- `python -m pip install -r requirements.txt`
- `python -m pip install -e .`

## Usage
- `import ripy`
- `import riwrapper`
- `riwrapper.c_is_subiso`

## Lemon notes

