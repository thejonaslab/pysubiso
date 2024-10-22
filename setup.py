import os
import sys
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy

## use gcc on osx
# os.environ['CC'] = '/usr/local/gcc/10.2.0/bin/gcc'
# os.environ['CXX'] = '/usr/local/gcc/10.2.0/bin/g++'


__version__ = '0.0.1'

COMPILE_ARGS = ["-O3", '-std=c++17', '-g',  
                '-fno-omit-frame-pointer', '-fPIC', '-g3', ]

LD_FLAGS = []

USE_SANITIZER = False
if USE_SANITIZER:
    COMPILE_ARGS.append('-fsanitize=address')
    LD_FLAGS.append('-fsanitize=address')


extensions = []
# if sys.platform == 'darwin':
#     COMPILE_ARGS.append('-stdlib=libc++')

ri_sourcefiles = ['pysubiso/riwrapper.pyx', 'pysubiso/rimatch.cc']
extensions += [Extension("pysubiso.riwrapper", ri_sourcefiles,
                         include_dirs=['ri/include', 'ri/rilib', numpy.get_include()],
                         language="c++",
                         extra_compile_args=COMPILE_ARGS,
                         extra_link_args = LD_FLAGS, )]



lemon_sourcefiles = ["pysubiso/lemonwrapper.pyx", "pysubiso/lemonmatch.cc", "pysubiso/graphutil.cc"]
extensions += [Extension("pysubiso.lemonwrapper", lemon_sourcefiles,
                         include_dirs=['lemon/', numpy.get_include()],
                         language="c++",
                         extra_compile_args=COMPILE_ARGS, 
                         extra_link_args = LD_FLAGS, )]

fastutil_sourcefiles = ["pysubiso/fastutils.pyx"]
extensions += [Extension("pysubiso.fastutils", fastutil_sourcefiles,
                         include_dirs=[numpy.get_include()],
                         language="c++",
                         extra_compile_args=COMPILE_ARGS, 
                         extra_link_args = LD_FLAGS, )]
setup(
    name='pysubiso',
    version=__version__,
    description='Lightweight Python library wrapping various graph subisomorphism libraries'
                'and adding a few other useful functions.',
    author='Eric Jonas',
    author_email='ericj@uchicago.edu',
    url='https://github.com/thejonaslab/pysubiso',
    license='MIT',
    packages=['pysubiso'], 
    # install_requires=[
    #     'Cython>=0.29.21',
    #     'numpy>=1.19.2',
    # ],
    ext_modules = cythonize(extensions),
    include_package_data=True,
)
