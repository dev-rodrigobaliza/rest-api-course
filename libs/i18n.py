"""
libs.i18n

By default, uses `en-us.json` file inside the `strings` top-level folder.

If language changes, run `libs.i18n.change_locale()`
"""
import json

default_locale = "en-us"
cached_strings = {}


def change_locale(locale: str) -> None:
    global cached_strings
    global default_locale
    default_locale = locale
    with open(f"strings/{default_locale}.json", encoding="utf-8") as file_object:
        cached_strings = json.load(file_object)


def get_text(name: str) -> str:
    return cached_strings[name]
