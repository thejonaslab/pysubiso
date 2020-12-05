Many of the libraries, especially RI, are written with explicit memory allocation
and pointer manipulation. As we want to use the resulting code
deep inside ML training loops (where leaks can be fatal) I wanted to
use mechanisms to validate we had no leaks. 


Address Sanitization is a relatively new feature built into gcc and clang to help
with this, but we're challenged by the fact that it's somewhat tempermental
on shared objects. People have written about this extensively: 

https://stackoverflow.com/questions/55692357/address-sanitizer-on-a-python-extension
https://jonasdevlieghere.com/sanitizing-python-modules/

I could only get it working properly under linux, and to do so I had to do the following

```
CFLAGS = ["-O3", '-std=c++17', '-g',  '-fsanitize=address',
                '-fno-omit-frame-pointer', '-fPIC', '-g3']
LD_FLAGS = ['-fsanitize=address',]
```
I then had to build with the system (not anaconda) python

```
rm -Rf build && /usr/bin/python3 -m pip install .
```

Note that I had to use pip to install since I don't actually have root on the
machine, and pip does a proper local install. 

Then to run it:

```
LD_PRELOAD=/usr/lib/gcc/x86_64-linux-gnu/7/libasan.so /usr/bin/python3 benchmark/benchmark_standalone.py > mem.log 2>&1 
```

Then, there will be lots of false positives as by default the python interpreter does
a lot of sketchy things with memory. 
