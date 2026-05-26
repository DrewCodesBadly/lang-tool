import asyncio
import os
import subprocess

import gi
import mistune
import ollama
from gi.repository import Adw, Gdk, Gio, Gtk, WebKit

from .config import (
    get_lang_opts,
    models_gtk_list,
    save_lang_opts,
    save_writing_archive,
)
from .ollama_thread import build_webview_widget, render_message_response
from .pages import LangToolPage


class WritingView(LangToolPage):
    def __init__(self):
        super().__init__("Writing", "edit-symbolic")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_bottom(12)

        opts_boxed_list = Gtk.ListBox()
        opts_boxed_list.set_css_classes(["boxed-list-separate"])
        llm_boxed_list = Gtk.ListBox()
        llm_boxed_list.set_css_classes(["boxed-list-separate"])
        opts_boxed_list.set_selection_mode(Gtk.SelectionMode.NONE)
        llm_boxed_list.set_selection_mode(Gtk.SelectionMode.NONE)

        self.model_select_row = Adw.ComboRow(title="Model to use for checking:")

        self.title_row = Adw.EntryRow(title="Writing Title")
        self.sources_row = Adw.EntryRow(title="Writing Source(s), or leave blank")
        self.sys_prompt_row = Adw.EntryRow(title="Grader Prompt")
        submit_row = Adw.ButtonRow(title="Submit Writing")
        submit_row.connect("activated", self.submit_writing)

        opts_boxed_list.append(self.title_row)
        opts_boxed_list.append(self.sources_row)
        llm_boxed_list.append(self.model_select_row)
        llm_boxed_list.append(self.sys_prompt_row)
        llm_boxed_list.append(submit_row)

        box.append(opts_boxed_list)

        label = Gtk.Label()
        label.set_text("Write your text here...")
        box.append(label)
        scrollview = Gtk.ScrolledWindow()
        self.textview = Gtk.TextView(vexpand=True)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        scrollview.set_child(self.textview)
        scrollview.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        box.append(scrollview)

        box.append(llm_boxed_list)

        self.set_child(box)

    def build(self):
        models = models_gtk_list()
        self.model_select_row.set_model(models)
        cfg = get_lang_opts()
        model_index = models.find(cfg["model"])

        self.model_select_row.set_selected(model_index)
        self.sys_prompt_row.set_text(cfg["sys_prompt"])

    def submit_writing(self, _):
        selected_model = self.model_select_row.get_selected_item().get_string()
        opts = get_lang_opts()
        opts["model"] = selected_model
        opts["sys_prompt"] = self.sys_prompt_row.get_text()
        save_lang_opts(opts)

        dialog = Adw.Dialog(halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
        dialog.set_follows_content_size(True)
        dialog.set_size_request(500, 700)
        dialog.set_title("Grader Response")

        # Build dialog UI
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        dialog.set_child(Adw.ToolbarView())
        dialog.get_child().add_top_bar(Adw.HeaderBar())
        dialog.get_child().set_content(box)
        frame = build_webview_widget()
        box.append(frame)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_top(24)
        box.set_margin_bottom(24)

        self.grader_response = ""

        def on_save(_):
            dialog.close()
            self.save_writing()

        save_button = Gtk.Button(label="Save Writing to Archive")
        save_button.connect("clicked", on_save)
        save_button.set_css_classes(["suggested-action"])
        save_button.set_sensitive(False)
        box.append(save_button)

        # run the chat
        buffer = self.textview.get_buffer()

        stream = ollama.chat(
            model=opts["model"],
            messages=[
                {
                    "role": "user",
                    "content": f"{opts['sys_prompt']}\n\n{buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)}",
                }
            ],
            stream=True,
        )

        def on_finished_callback(r):
            self.grader_response = r
            save_button.set_sensitive(True)

        render_message_response(
            stream, frame.get_child(), on_finished=on_finished_callback
        )

        dialog.present(self.get_root())

    def save_writing(self):
        save_writing_archive(
            self.title_row.get_text(),
            self.textview.get_buffer().get_text(
                self.textview.get_buffer().get_start_iter(),
                self.textview.get_buffer().get_end_iter(),
                False,
            ),
            self.grader_response,
            self.sources_row.get_text(),
        )
