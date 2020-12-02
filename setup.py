import os
import sys
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize

__version__ = '0.0.1'

sourcefiles = ['pysubiso/riwrapper.pyx', 'pysubiso/ritest.cc']
extensions = [Extension("pysubiso", sourcefiles,
                        include_dirs=['ri/include', 'ri/rilib'],
                        language="c++",
                        extra_compile_args=["-O3", '-std=c++17'])]

setup(
    name='pysubiso',
    version=__version__,
    description='Lightweight Python library wrapping various graph subisomorphism libraries'
                'and adding a few other useful functions.',
    author='Eric Jonas',
    author_email='ericj@uchicago.edu',
    url='https://github.com/thejonaslab/pysubiso',
    license='MIT',
    packages=find_packages(),
    # install_requires=[
    #     'Cython>=0.29.21',
    #     'numpy>=1.19.2',
    # ],
    ext_modules = cythonize(extensions),
    include_package_data=True,
)
