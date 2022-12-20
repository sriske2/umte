"""
Copyright (C) 2012 Skyler Riske 
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from gi.repository import Gtk, Vte, GLib, Gdk
import os

class Term(Vte.Terminal):
    def __init__(self, program, *args, **kwds):
        super(Term, self).__init__(*args, **kwds)
        self.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            [program],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None)
        self.set_allow_bold(True)
