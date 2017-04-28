#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# System modules
import os
from setuptools import setup, find_packages

from numericalmodel import __version__

def read_file(filename):
    with open(filename) as f:
        return f.read()

# run setup
# take metadata from setup.cfg
setup( 
    name = "numericalmodel",
    description = "abstract classes to set up and run a numerical model",
    author = "Yann Büchau",
    author_email = "yann.buechau@web.de",
    keywords = "modelling",
    license = "GPLv3",
    version = __version__,
    url = 'https://github.com/nobodyinperson/python3-numericalmodel',
    download_url = ("https://github.com/nobodyinperson/" 
        "python3-numericalmodel/archive/v{}.tar.gz").format(__version__),
    long_description = read_file("README.rst"),
    classifiers = [
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3.5',
            'Operating System :: OS Independent',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    test_suite = 'tests',
    tests_require = [ 'numpy' ],
    extras_require = { 
        "gui": ["matplotlib"],
        },
    install_requires = [ 'numpy', 'scipy' ],
    packages = find_packages(exclude=['tests']),
    )
