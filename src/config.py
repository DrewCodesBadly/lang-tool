import json
from os import path

languages = {"active": "", "registered": []}


def get_languages_json():
    global languages
    return languages


def save_languages_json(l):
    global languages
    languages = l
    with open(path.join(get_config_dir(), "languages.json"), "w") as f:
        json.dump(languages, f)


def get_config_dir():
    return path.join(path.expanduser("~"), ".config/LangTool")


def lang_dir():
    global languages
    if languages["active"]:
        active = languages["active"]
        # ignore type error it doesn't get json
        return path.join(get_config_dir(), active)
    else:
        return None


def get_active_lang():
    global languages
    return languages["active"]


def set_active_lang(l):
    global languages
    languages["active"] = l
    save_languages_json(languages)
