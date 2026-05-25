import json
import os
import subprocess

import gi
import mistune
import ollama
from gi.repository import Adw, Gdk, Gio, Gtk

import config
from ollama_thread import build_webview_widget, webview_set_md
from pages import LangToolPage


class ArchiveView(LangToolPage):
    def __init__(self):
        super().__init__("Writing Archive", "file-manager-symbolic")
        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_margin_bottom(12)
        self.content_bin = Adw.Bin()
        self.split_view.set_content(self.content_bin)
        self.split_view.set_sidebar_position(Gtk.PackType.END)
        self.build()
        self.content_bin.set_child(
            Adw.StatusPage(
                description="Select a file on the right to open...",
                title="No File Selected",
                icon_name="folder-open-symbolic",
            )
        )
        self.set_child(self.split_view)

    def build(self):
        frame = Gtk.Frame()
        frame.set_child(self.build_sidebar())
        self.split_view.set_sidebar(frame)

    def build_sidebar(self):
        sidebar = Adw.ToolbarView()
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        list_box.set_margin_start(12)
        list_box.set_margin_end(12)
        list_box.set_css_classes(["navigation-sidebar"])
        list_box.set_hexpand(True)

        directory_path = config.get_archive_folder()
        for filename in os.listdir(directory_path):
            file_extension = os.path.splitext(filename)
            if file_extension[1] == ".json":
                list_box_row = Gtk.ListBoxRow()
                label = Gtk.Label(label=file_extension[0].replace("_", " "))

                list_box_row.set_child(label)

                list_box.append(list_box_row)

        def on_list_box_row_activated(box, row):
            file_name = row.get_child().get_text().replace(" ", "_") + ".json"
            dir = config.get_archive_folder()
            path = os.path.join(dir, file_name)
            self.content_bin.set_child(self.build_content(path))

        list_box.connect("row-selected", on_list_box_row_activated)
        sidebar.set_content(list_box)

        return sidebar

    def build_content(self, file_path):
        scroll_window = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        scroll_window.set_child(box)
        scroll_window.set_margin_end(6)

        with open(file_path, "r") as file:
            content = file.read()
            json_data = json.loads(content)

            # Add two labels and a separator to the box
            label1 = Gtk.Label(
                label=f"Title: {json_data['title']}", halign=Gtk.Align.START
            )
            label2 = Gtk.Label(
                label=f"Sources: {json_data['sources']}", halign=Gtk.Align.START
            )

            box.append(label1)
            box.append(label2)

            separator = Gtk.Separator()
            box.append(separator)

            # 2 webviews
            input_label = Gtk.Label(label="Writing:", halign=Gtk.Align.START)
            response_label = Gtk.Label(label="Grader Response:", halign=Gtk.Align.START)
            input_view = build_webview_widget()

            response_view = build_webview_widget()
            box.append(input_label)
            webview_set_md(json_data["content"], input_view.get_child())
            box.append(input_view)
            box.append(response_label)
            webview_set_md(json_data["response"], response_view.get_child())
            box.append(response_view)

        return scroll_window
