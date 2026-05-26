import json
import os
import sys
from datetime import datetime
from os import path

import gi
import ollama

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gdk, Gio, Gtk

# This whole system will definitely break and crash if it is fed bad files.
# So for now just don't touch the config files ever. I don't know why you would anyway.
languages = {"active": "", "registered": []}
preferences = {"ollama_url": "http://localhost:11434"}
lang_opts = {"model": "", "sys_prompt": "", "chat_model": "", "resources": {}}


def get_languages_json():
    global languages
    return languages


def save_languages_json(l):
    global languages
    languages = l
    with open(path.join(get_config_dir(), "languages.json"), "w") as f:
        json.dump(languages, f)
    load_lang_opts()


def load_lang_opts():
    global languages
    global lang_opts
    opts_path = path.join(get_config_dir(), languages["active"], "lang_opts.json")
    if path.exists(opts_path):
        with open(opts_path, "r") as f:
            lang_opts = json.loads(f.read().strip())
    else:
        models = ollama.list()
        lang_name = languages["active"]
        lang_opts = {
            "chat_model": "",
            "model": "",
            "sys_prompt": f"""The following is writing in {lang_name}. \
Check the writing for mistakes and give advice to the user on how to improve their writing. \
Write in {lang_name} only. Here is the writing:""",
            "resources": {},
        }
        if models:
            lang_opts["model"] = (
                models.models[0].model
                if models.models and models.models[0].model
                else ""
            )
        lang_opts["chat_model"] = lang_opts["model"]
        save_lang_opts(lang_opts)


def get_lang_opts():
    global lang_opts
    return lang_opts


def save_lang_opts(l):
    global lang_opts
    with open(
        path.join(get_config_dir(), languages["active"], "lang_opts.json"), "w"
    ) as f:
        json.dump(lang_opts, f)


def get_config_dir():
    return path.join(path.expanduser("~"), ".var/app/com.github.DrewCodesBadly.LangTool")


def lang_dir():
    global languages
    if languages["active"]:
        active = languages["active"]
        # ignore type error it doesn't get json
        return path.join(get_config_dir(), active)
    else:
        # just uhh don't worry about it
        return get_config_dir()


def get_active_lang():
    global languages
    return languages["active"]


def set_active_lang(l):
    global languages
    languages["active"] = l
    save_languages_json(languages)
    load_lang_opts()


def open_file(file):
    folder = Gio.File.new_for_path(file)
    launcher = Gtk.FileLauncher(file=folder)
    launcher.launch()


def get_ollama_url():
    global preferences
    return preferences["ollama_url"]


def models_gtk_list():
    models = ollama.list()
    model_names = (
        [model.model for model in models.models] if models and models.models else []
    )
    list = Gtk.StringList()
    for name in model_names:
        list.append(name)

    return list


def get_archive_folder():
    folder = path.join(lang_dir(), "archive")
    if not path.exists(folder):
        os.makedirs(folder)
    return folder


def save_writing_archive(title, content, response, sources):
    dir = get_archive_folder()
    json_dat = {
        "title": title,
        "content": content,
        "response": response,
        "sources": sources if sources else "None",
    }

    current_date = datetime.now().strftime("%m-%d-%y")
    filename = f"{title.replace(' ', '_')}_-_{current_date}.json"
    file_path = path.join(dir, filename)

    if not path.exists(dir):
        os.makedirs(dir)

    with open(file_path, "w") as f:
        json.dump(json_dat, f)
