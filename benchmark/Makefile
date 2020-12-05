all: profile


profile:
	rm -Rf build && /usr/bin/python3 -m pip install .	
	LD_PRELOAD=/usr/lib/gcc/x86_64-linux-gnu/7/libasan.so /usr/bin/python3 benchmark/benchmark_standalone.py 2> mem.log
	python benchmark/parse_leaks.py mem.log  rimatch.cc

