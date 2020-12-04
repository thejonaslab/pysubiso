import os
import sys
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize

__version__ = '0.0.1'

COMPILE_ARGS = ["-O3", '-std=c++17']
if sys.platform == 'darwin':
    COMPILE_ARGS.append('-stdlib=libc++')

sourcefiles = ['pysubiso/riwrapper.pyx', 'pysubiso/rimatch.cc']
extensions = [Extension("pysubiso.riwrapper", sourcefiles,
                        include_dirs=['ri/include', 'ri/rilib'],
                        language="c++",
                        extra_compile_args=COMPILE_ARGS)]

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
