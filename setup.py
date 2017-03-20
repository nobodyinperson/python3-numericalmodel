#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# System modules
import os
from setuptools import setup, find_packages

def read_file(file):
    """ Read file relative to this file
    """
    with open(os.path.join(os.path.dirname(__file__),file)) as f:
        return f.read()

# run setup
# take metadata from setup.cfg
setup( 
    name = 'numericalmodel',
    version = '0.0.1',
    description = 'abstract classes to set up and run a numerical model',
    long_description = read_file("README.md"),
    keywords = [ 'modelling' ],
    license = 'GPLv3',
    author = 'Yann Büchau',
    author_email = 'yann.buechau@web.de',
    url = 'https://github.com/nobodyinperson/python3-numericalmodel',
    classifiers = [
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3.5',
            'Operating System :: OS Independent',
            'Topic :: Scientific / Engineering',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    test_suite = 'tests',
    tests_require = [ 'numpy' ],
    install_requires = [ 'numpy', 'scipy' ],
    packages = find_packages(exclude=['tests']),
    )
