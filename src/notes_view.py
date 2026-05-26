import gi
from gi.repository import Gtk

from .pages import LangToolPage


class NotesView(LangToolPage):
    def __init__(self):
        super().__init__("Notes", "notepad-symbolic")
        self.set_child(Gtk.Label(label="Coming soon!"))
