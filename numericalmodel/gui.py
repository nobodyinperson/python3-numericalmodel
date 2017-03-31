#!/usr/bin/env python3
# system modules
import logging
import textwrap

# internal modules
from . import utils

# external modules


instructions = textwrap.dedent(""" 
To install, use your system's package manager and install ``python3-gi``.

On Debian/Ubuntu::

    sudo apt-get install python3-gi
""")

__doc__ = \
""" 
Graphical user interface for a NumericalModel. This module only contains classes
if the system package ``python3-gi`` is installed to provide the :mod:`gi`
module.

""" + instructions

try: 
    import gil
    gi.require_version('Gtk','3.0')
    from gi.repository import Gtk

    GTK_INSTALLED = True # importing worked
except ImportError: # importing didn't work
    GTK_INSTALLED = False 

# only if gtk is installed
if GTK_INSTALLED: 
    pass

