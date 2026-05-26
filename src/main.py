import asyncio
import json
import os
from os import path, read

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("WebKit", "6.0")

import ollama
from gi.repository import Adw, Gdk, Gio, Gtk, WebKit

from .archive_view import ArchiveView
from .config import (
    get_config_dir,
    get_languages_json,
    load_lang_opts,
    save_languages_json,
)
from .languages_view import LanguagesView
from .notes_view import NotesView
from .ollama_thread import run_loop
from .resources_view import ResourcesView
from .writing_view import WritingView


def list_pages():
    return [
        ResourcesView(),
        NotesView(),
        WritingView(),
        ArchiveView(),
        LanguagesView(),
    ]


def build_sidebar(pages, stack, app):
    sidebar = Adw.ToolbarView()
    header_bar = Adw.HeaderBar()
    sidebar.add_top_bar(header_bar)

    menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic")

    popover_menu = Gio.Menu()
    preferences_action = Gio.SimpleAction(name="example")
    preferences_action.connect(
        "activate", lambda _act, _other: print("Example action triggered")
    )
    app.add_action(preferences_action)
    popover_menu.append("Preferences", "app.example")

    menu_button.set_menu_model(popover_menu)
    header_bar.pack_end(menu_button)

    list_box = Gtk.ListBox()
    list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
    list_box.set_margin_start(12)
    list_box.set_margin_end(12)
    list_box.set_css_classes(["navigation-sidebar"])
    list_box.set_hexpand(True)

    for page in pages:  # Example loop, adjust as needed
        list_box_row = Gtk.ListBoxRow()
        icon_image = Gtk.Image(icon_name=page.icon_name)
        label = Gtk.Label(label=page.name)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.append(icon_image)
        box.append(label)

        list_box_row.set_child(box)

        list_box.append(list_box_row)

    def on_list_box_row_activated(box, row):
        # bad for performance but idc its python
        pages[row.get_index()].build()  # rebuilds page in case selected lang changed.
        stack.set_visible_child(pages[row.get_index()])

    list_box.connect("row-selected", on_list_box_row_activated)
    sidebar.set_content(list_box)

    return sidebar


def on_activate(app):
    win = Adw.ApplicationWindow(title="LangTool", application=app)

    split_view = Adw.OverlaySplitView()
    win.set_content(split_view)

    pages = list_pages()

    view_stack_page = Adw.ToolbarView()
    view_header = Adw.HeaderBar()
    view_header.set_show_title(False)
    view_stack_page.add_top_bar(view_header)
    view_stack = Adw.ViewStack()
    view_stack_page.set_content(view_stack)
    for page in pages:
        view_stack.add_titled_with_icon(page, page.name, page.name, page.icon_name)

    view_stack.set_visible_child(pages[0])

    split_view.set_sidebar(build_sidebar(pages, view_stack, app))

    split_view.set_content(view_stack_page)

    win.present()


def main(_version):
    # Start background thread for ollama
    run_loop()

    # since markdown css is only dark atm
    sm = Adw.StyleManager.get_default()
    sm.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

    # Set up config dir, read necessary info
    languages = get_languages_json()
    config_dir = get_config_dir()
    if not path.exists(config_dir):
        os.makedirs(config_dir)

    lang_file = path.join(config_dir, "languages.json")
    if path.exists(lang_file):
        with open(lang_file, "r") as file:
            save_languages_json(json.loads(file.read().strip()))
    else:
        with open(lang_file, "w") as file:
            json_str = json.dumps(languages, indent=4)
            file.write(json_str)
    load_lang_opts()
    
    theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
    theme.add_resource_path("/com/github/DrewCodesBadly/LangTool/icons/")

    app = Adw.Application(
        application_id="com.github.DrewCodesBadly.LangTool",
        flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        resource_base_path="/com/github/DrewCodesBadly/LangTool",
    )

    app.connect("activate", on_activate)

    app.run(None)


if __name__ == "__main__":
    main()
