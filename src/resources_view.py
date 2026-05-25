import os
import subprocess

import gi
import mistune
import ollama
from gi.repository import Adw, Gdk, Gio, Gtk

import config
from pages import LangToolPage


class ResourcesView(LangToolPage):
    def __init__(self):
        super().__init__("Resources", "symbolic-link-symbolic")
