import os
import subprocess

import gi
import mistune
import ollama
from gi.repository import Adw, Gdk, Gio, Gtk

import config
from pages import LangToolPage


class LanguagesView(LangToolPage):
    def __init__(self):
        super().__init__("Languages", "translate-symbolic")

        self.connect("show", lambda _: print("hi"))

        boxed_list = Gtk.ListBox()
        boxed_list.set_selection_mode(Gtk.SelectionMode.NONE)
        boxed_list.set_css_classes(["boxed-list-separate"])

        self.row = Adw.ComboRow(title="Selected Language: ")

        def on_selection_changed(row, _pspec):
            lang = row.get_selected_item().get_string()
            config.set_active_lang(lang)

        self.row.connect("notify::selected-item", on_selection_changed)
        boxed_list.append(self.row)

        file_open_row = Adw.ActionRow(title="Open Language Folder", activatable=True)

        def open_lang_folder(_widget):
            config.open_file(config.lang_dir())

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
        self.remove_lang_row = Adw.ComboRow(title="Language to Remove: ")
        remove_language_group.add_row(self.remove_lang_row)
        remove_button_row = Adw.ButtonRow(title="Remove this language")
        remove_button_row.connect("activated", self.on_remove_language_activate)
        remove_language_group.add_row(remove_button_row)

        boxed_list.append(add_language_group)
        boxed_list.append(remove_language_group)
        self.set_child(boxed_list)

        self.build()

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

        self.build()

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
            for root, dirs, files in os.walk(
                os.path.join(config_dir, name), topdown=False
            ):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(os.path.join(config_dir, name))

        self.build()

    def build(self):
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
        self.remove_lang_row.set_model(list_model)
        index = 0 if cur_lang not in lang_opts else lang_opts.index(cur_lang)
        self.row.set_selected(index)
        self.remove_lang_row.set_selected(index)

    def on_remove_language_activate(self, button):
        lang_name = self.remove_lang_row.get_selected_item().get_string()
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
            self.remove_lang(self.remove_lang_row.get_selected_item().get_string())
