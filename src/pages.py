import os
import subprocess

import gi

import config

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import ollama
from gi.repository import Adw, Gdk, Gio, Gtk


def list_pages():
    return [
        ResourcesView(),
        NotesView(),
        ChatView(),
        WritingView(),
        ArchiveView(),
        LanguagesView(),
    ]


class LangToolPage(Adw.Bin):
    def __init__(self, name, icon_name):
        super().__init__()
        self.name = name
        self.icon_name = icon_name


class ResourcesView(LangToolPage):
    def __init__(self):
        super().__init__("Resources", "symbolic-link-symbolic")


class NotesView(LangToolPage):
    def __init__(self):
        super().__init__("Notes", "notepad-symbolic")


class ChatView(LangToolPage):
    def __init__(self):
        super().__init__("Chat", "chat-symbolic")


class WritingView(LangToolPage):
    def __init__(self):
        super().__init__("Writing", "edit-symbolic")


class ArchiveView(LangToolPage):
    def __init__(self):
        super().__init__("Writing Archive", "file-manager-symbolic")


class LanguagesView(LangToolPage):
    def __init__(self):
        super().__init__("Languages", "translate-symbolic")

        boxed_list = Gtk.ListBox()
        boxed_list.set_selection_mode(Gtk.SelectionMode.NONE)
        boxed_list.set_css_classes(["boxed-list-separate"])
        scrolled_window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        scrolled_window.set_margin_start(24)  # Add margin on the left
        scrolled_window.set_margin_end(24)  # Add margin on the right
        scrolled_window.set_child(boxed_list)

        self.row = Adw.ComboRow(title="Selected Language: ")

        boxed_list.append(self.row)

        file_open_row = Adw.ActionRow(title="Open Language Folder", activatable=True)

        def open_lang_folder(_widget):
            folder = config.lang_dir()
            subprocess.Popen(
                ["xdg-open", folder],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        file_open_row.connect("activated", open_lang_folder)
        file_open_row.set_icon_name("folder-open-symbolic")
        boxed_list.append(file_open_row)

        add_language_group = Adw.ExpanderRow(title="Add Language")
        entry_row = Adw.EntryRow(title="Language Name")
        add_language_group.add_row(entry_row)
        button_row = Adw.ButtonRow(title="Add this language")
        button_row.connect(
            "activated", lambda _widget: self.add_lang(entry_row.get_text())
        )
        add_language_group.add_row(button_row)

        remove_language_group = Adw.ExpanderRow(title="Remove Language")
        self.combo_row = Adw.ComboRow(title="Language to Remove: ")
        remove_language_group.add_row(self.combo_row)
        remove_button_row = Adw.ButtonRow(title="Remove this language")
        remove_button_row.connect("activated", self.on_remove_language_activate)
        remove_language_group.add_row(remove_button_row)

        boxed_list.append(add_language_group)
        boxed_list.append(remove_language_group)
        self.set_child(scrolled_window)

        self.update_lang_select_list()

    def add_lang(self, name):
        languages = config.get_languages_json()
        if name in languages["registered"]:
            return
        languages["active"] = name
        languages["registered"].append(name)
        config.save_languages_json(languages)
        # make dir
        config_dir = config.get_config_dir()
        if not os.path.exists(os.path.join(config_dir, name)):
            os.makedirs(os.path.join(config_dir, name))

        self.update_lang_select_list()

    def remove_lang(self, name):
        languages = config.get_languages_json()
        if name not in languages["registered"]:
            return
        languages["registered"].remove(name)
        if languages["active"] == name:
            languages["active"] = (
                languages["registered"][0] if languages["registered"] else ""
            )
        config.save_languages_json(languages)
        # remove dir
        config_dir = config.get_config_dir()
        if os.path.exists(os.path.join(config_dir, name)):
            os.rmdir(os.path.join(config_dir, name))

        self.update_lang_select_list()

    def update_lang_select_list(self):
        languages = config.get_languages_json()
        cur_lang = languages["active"]  # string
        lang_opts = languages["registered"]  # string array
        list_model = Gtk.StringList()
        if not lang_opts:
            list_model.append("None")
        else:
            for lang in lang_opts:
                list_model.append(lang)
        self.row.set_model(list_model)
        self.combo_row.set_model(list_model)
        index = 0 if cur_lang not in lang_opts else lang_opts.index(cur_lang)
        self.row.set_selected(index)
        self.combo_row.set_selected(index)

    def on_remove_language_activate(self, button):
        lang_name = self.combo_row.get_selected_item().get_string()
        dialog = Adw.AlertDialog(
            heading="Confirm Remove",
            body=f"Are you sure you want to remove {lang_name}? This action cannot be undone and will delete all associated files.",
        )

        dialog.add_response("cancel", "Cancel")
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        dialog.add_response("confirm", "Confirm")
        dialog.set_response_appearance("confirm", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.present(self.get_root())
        dialog.connect("response", self.on_dialog_response)

    def on_dialog_response(self, _dialog, response):
        if response == "confirm":
            self.remove_lang(self.combo_row.get_selected_item().get_string())
