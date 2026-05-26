import os
import subprocess
import webbrowser

import gi
import mistune
import ollama
from gi.repository import Adw, Gtk

from .config import get_lang_opts, save_lang_opts
from .pages import LangToolPage


class ResourcesView(LangToolPage):
    def __init__(self):
        super().__init__("Resources", "symbolic-link-symbolic")
        # all in build
        self.build()

    def build(self):
        self.preferences_page = Adw.PreferencesPage()
        self.set_child(self.preferences_page)
        resources = get_lang_opts()["resources"]
        for key, value in resources.items():
            group = Adw.PreferencesGroup(title=key)
            for item in value:
                # Assuming each item has a 'name' and 'description'
                row = Adw.ActionRow(
                    title=item["name"],
                    subtitle=item["description"],
                )
                row.add_suffix(Gtk.Image(icon_name="symbolic-link-symbolic"))
                row.set_activatable(True)
                row.connect("activated", lambda _: self.open_resource(item["url"]))

                group.add(row)
            add_row = Adw.ButtonRow(
                title="Add Resource", start_icon_name="plus-symbolic"
            )
            add_row.connect("activated", lambda _, k=key: self.on_add_resource(k))
            group.add(add_row)
            self.preferences_page.add(group)

        # Add a button to add a new group
        edit_group = Adw.PreferencesGroup(title="")
        new_btn = Adw.ButtonRow(
            title="Add new group...", start_icon_name="plus-symbolic"
        )
        new_btn.connect("activated", self.on_new_group_clicked)
        del_btn = Adw.ButtonRow(
            title="Remove a group...", start_icon_name="user-trash-symbolic"
        )
        del_btn.connect("activated", self.on_del_group_clicked)
        edit_group.add(new_btn)
        edit_group.add(del_btn)
        self.preferences_page.add(edit_group)

    def on_new_group_clicked(self, _widget):
        dialog = Adw.PreferencesDialog()
        dialog.set_title("Add a New Resource Group")
        page = Adw.PreferencesPage()
        dialog.add(page)
        group = Adw.PreferencesGroup(title="")

        group_name_entry = Adw.EntryRow(title="Group name")
        group.add(group_name_entry)

        def on_activate(_widget):
            opts = get_lang_opts()
            opts["resources"][group_name_entry.get_text()] = []
            save_lang_opts(opts)
            self.build()  # Rebuild the view to reflect changes
            dialog.close()

        add_btn = Adw.ButtonRow(title="Add Group")
        add_btn.connect("activated", on_activate)
        group.add(add_btn)
        page.add(group)

        dialog.present(self.get_root())

    def on_del_group_clicked(self, _widget):
        dialog = Adw.PreferencesDialog()
        dialog.set_title("Remove an Existing Resource Group")
        page = Adw.PreferencesPage()
        dialog.add(page)
        group = Adw.PreferencesGroup(title="")

        resources = get_lang_opts()["resources"]
        model = Gtk.StringList()
        for name in resources:
            model.append(name)
        if not resources:
            model.append("None")
        group_name_entry = Adw.ComboRow(title="Group name")
        group_name_entry.set_model(model)
        group_name_entry.set_selected(0)  # Default to first item if any
        group.add(group_name_entry)

        def on_activate(_widget):
            opts = get_lang_opts()
            to_remove = group_name_entry.get_selected_item().get_string()
            if to_remove not in opts["resources"]:
                dialog.close()
                return
            del opts["resources"][to_remove]
            save_lang_opts(opts)
            self.build()  # Rebuild the view to reflect changes
            dialog.close()

        add_btn = Adw.ButtonRow(title="Remove Group")
        add_btn.connect("activated", on_activate)
        group.add(add_btn)
        page.add(group)

        dialog.present(self.get_root())

    def on_add_resource(self, group_name):
        dialog = Adw.PreferencesDialog()
        dialog.set_title("Add a New Resource")
        page = Adw.PreferencesPage()
        dialog.add(page)
        group = Adw.PreferencesGroup(title="")

        name_entry = Adw.EntryRow(title="Resource Name")
        description_entry = Adw.EntryRow(title="Resource Description")
        url_entry = Adw.EntryRow(title="Link to resource, or shell command to run:")
        group.add(name_entry)
        group.add(description_entry)
        group.add(url_entry)

        def on_activate(_widget):
            opts = get_lang_opts()
            opts["resources"][group_name].append(
                {
                    "name": name_entry.get_text(),
                    "description": description_entry.get_text(),
                    "url": url_entry.get_text(),
                }
            )
            save_lang_opts(opts)
            self.build()  # Rebuild the view to reflect changes
            dialog.close()

        add_btn = Adw.ButtonRow(title="Add Resource")
        add_btn.connect("activated", on_activate)
        group.add(add_btn)
        page.add(group)

        dialog.present(self.get_root())

    def open_resource(self, url):
        if url.startswith("http"):
            webbrowser.open(url)
        else:
            subprocess.Popen(url)
