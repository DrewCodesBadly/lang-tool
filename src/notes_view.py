import asyncio
import os
import subprocess

import gi
import mistune
import ollama
from gi.repository import Adw, Gdk, Gio, Gtk, WebKit

import config
import ollama_thread
from ollama_thread import build_webview_widget, render_message_response
from pages import LangToolPage


class NotesView(LangToolPage):
    def __init__(self):
        super().__init__("Notes", "notepad-symbolic")
        self.set_child(Gtk.Label(label="Coming soon!"))
