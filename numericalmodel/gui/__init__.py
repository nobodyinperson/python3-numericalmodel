#!/usr/bin/env python3
# system modules
import os, sys
import logging
import signal
import textwrap
from pkg_resources import resource_filename

# internal modules
from .. import utils

# external modules


instructions = textwrap.dedent(""" 
To install, use your system's package manager and install ``python3-gi``.

On Debian/Ubuntu::

    sudo apt-get install python3-gi

.. note:: If you don't have system privileges, there is also the (experimental)
    :mod:`pgi` module on `PyPi <https://pypi.python.org/pypi/pgi/>`_ that you
    can install via::

        pip3 install --user pgi

    Theoretically, the :any:`NumericalModelGui` might work with this package as
    well.
""")

__doc__ = \
""" 
Graphical user interface for a NumericalModel. This module is only useful
if the system package ``python3-gi`` is installed to provide the :mod:`gi`
module.

""" + instructions

PGI = False
GTK_INSTALLED = False 
try: # try real gi module
    import gi
    gi.require_version('Gtk','3.0')
    from gi.repository import Gtk
    from gi.repository import GLib
    GTK_INSTALLED = True # importing real gi worked
except: # importing real gi didn't work
    try: # try pgi package
        import pgi
        pgi.install_as_gi()
        import gi
        gi.require_version('Gtk','3.0')
        from gi.repository import Gtk
        from gi.repository import GLib
        PGI = True
        GTK_INSTALLED = True # importing pgi worked
    except:
        pass


# only if gtk is installed
class NumericalModelGui(utils.LoggerObject):
    """ 
    class for a GTK gui to run a :any:`NumericalModel` interactively

    Args:
        numericalmodel (NumericalModel): the NumericalModel to run
    """
    def __init__(self, numericalmodel):
        # check for GTK
        if not GTK_INSTALLED: 
            print("Gtk3.0 bindings seem not installed.\n"+instructions)
            sys.exit()

        self.setup_signals(
            signals = [signal.SIGINT, signal.SIGTERM, signal.SIGHUP],
            handler = self.quit
        )

    ##################
    ### Properties ###
    ##################
    @property
    def builder(self):
        """ 
        The gui's ``GtkBuilder``. This is a read-only property.
        
        :getter: Return the ``GtkBuilder``, load the :any:`gladefile` if
            necessary.
        :type: ``GtkBuilder``
        """
        try: 
            self._builder
        except AttributeError: 
            self._builder = Gtk.Builder() # new builder
            # load the gladefile
            self._builder.add_from_file( self.gladefile )
        return self._builder

    @property
    def gladefile(self):
        """ 
        The gui's Glade file. This is a read-only property.

        :type: :any:`str`
        """
        return resource_filename(__name__, "gui.glade")

    
    ###############
    ### Methods ###
    ###############
    def setup_signals(self, signals, handler):
        """
        This is a workaround to signal.signal(signal, handler)
        which does not work with a ``GLib.MainLoop`` for some reason.
        Thanks to: http://stackoverflow.com/a/26457317/5433146

        Args:
            signals (list): the signals (see :any:`signal` module) to
                connect to
            handler (callable): function to be executed on these signals
        """
        def install_glib_handler(sig): # add a unix signal handler
            GLib.unix_signal_add( GLib.PRIORITY_HIGH, 
                sig, # for the given signal
                handler, # on this signal, run this function
                sig # with this argument
                )

        for sig in signals: # loop over all signals
            GLib.idle_add( # 'execute'
                install_glib_handler, sig, # add a handler for this signal
                priority = GLib.PRIORITY_HIGH  )

    def setup_gui(self):
        """ 
        Set up the GTK gui elements
        """
        # connect signals
        self.handlers = {
            "CloseApplication": self.quit,
            }
        self.builder.connect_signals(self.handlers)

        # show everything
        self["main_applicationwindow"].show_all()

    def run(self):
        """ 
        Run the gui
        """
        # set up the gui
        self.setup_gui()
        # run the gui
        self.logger.debug("starting mainloop")
        Gtk.main()
        self.logger.debug("mainloop is over")

    def quit(self, *args):
        """ 
        Stop the gui
        """
        self.logger.debug("received quitting signal")
        self.logger.debug("stopping mainloop...")
        Gtk.main_quit()
        self.logger.debug("mainloop stopped")

    def __getitem__(self, key):
        """ 
        When indexed, return the corresponding Glade gui element

        Args:
            key (str): the Glade gui element name
        """
        return self.builder.get_object( key )
