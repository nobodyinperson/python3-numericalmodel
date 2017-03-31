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
""")

__doc__ = \
""" 
Graphical user interface for a NumericalModel. This module is only useful
if the system package ``python3-gi`` is installed to provide the :mod:`gi`
module.

""" + instructions

try: 
    import gi
    gi.require_version('Gtk','3.0')
    from gi.repository import Gtk
    from gi.repository import GLib

    GTK_INSTALLED = True # importing worked
except: # importing didn't work
    GTK_INSTALLED = False 

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
            print("python3-gi seems not installed."+instructions)
            sys.exit()

        self.setup_signals(
            signals = [signal.SIGINT, signal.SIGTERM, signal.SIGHUP],
            handler = self.quit
        )
        # can't use Gtk.main() because of a bug that prevents proper SIGINT
        # handling. use Glib.MainLoop() directly instead.
        self.mainloop = GLib.MainLoop() # main loop
    
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

    # build the gui
    def load_builder(self):
        """ 
        Load the GTK gui elements from a gladefile
        """
        # get a GTK builder
        self.builder = Gtk.Builder()
        # load the gladefile
        self.builder.add_from_file(resource_filename(__name__,"gui.glade"))

    def setup_gui(self):
        """ 
        Set up the GTK gui elements
        """
        # load the builder
        self.load_builder()

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
        self.mainloop.run()
        self.logger.debug("mainloop is over")

    def quit(self, *args):
        """ 
        Stop the gui
        """
        self.logger.debug("received quitting signal")
        self.logger.debug("stopping mainloop...")
        self.mainloop.quit()
        self.logger.debug("mainloop stopped")

    def __getitem__(self, key):
        """ 
        When indexed, return the corresponding Glade gui element

        Args:
            key (str): the Glade gui element name
        """
        return self.builder.get_object( key )
