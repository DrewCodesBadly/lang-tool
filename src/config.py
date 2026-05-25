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
