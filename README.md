## Graph isomorphism and subgraph isomorphism

This is a library which attempts to unify all of our graph isomorphism
and subisomorphism code into one library with extensive tests and benchmarking, 
all from Python. 

Currently it wraps RI https://github.com/InfOmics/RI

but we would eventually like to wrap LEMON
https://lemon.cs.elte.hu/trac/lemon/wiki/Documentation

## TODO 
[ ] Settle on an API which can switch between backends
[ ] Create tests 
[ ] check subiso between differently-sized graphs
[ ] rename everything

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

