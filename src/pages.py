import os
import subprocess

import gi
import mistune
import ollama
from gi.repository import Adw, Gdk, Gio, Gtk

import config


class LangToolPage(Gtk.ScrolledWindow):
    def __init__(self, name, icon_name):
        super().__init__()
        self.name = name
        self.icon_name = icon_name
        self.set_margin_start(24)  # Add margin on the left
        self.set_margin_end(24)  # Add margin on the right
        self.vexpand = True
        self.hexpand = True

    def build(self):
        pass


class NotesView(LangToolPage):
    def __init__(self):
        super().__init__("Notes", "notepad-symbolic")


class ChatView(LangToolPage):
    def __init__(self):
        super().__init__("Chat", "chat-symbolic")
