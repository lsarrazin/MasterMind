import sys
from typing import KeysView

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

from MastermindUI import MainWindow


class MasterMind(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="github.lsarrazin.MasterMind",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.window = None


    def do_startup(self):
        Gtk.Application.do_startup(self)


    def do_activate(self):
        ''' Only one single window allowed '''
        if not self.window:
            self.window = MainWindow(application=self, title="MasterMind")


    def do_command_line(self, command_line):
        ''' No real command line '''
        self.activate()
        return 0        


if __name__ == '__main__':
    app = MasterMind()
    app.run(sys.argv)
    
