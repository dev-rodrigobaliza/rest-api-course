"""
libs.i18n

By default, uses `en-us.json` file inside the `strings` top-level folder.

If language changes, set `libs.i18n.default_locale` and run `libs.i18n.refresh()`
"""
import json

default_locale = "en-us"
cached_strings = {}


def refresh():
    global cached_strings
    with open(f"strings/{default_locale}.json", "r") as file_object:
        cached_strings = json.load(file_object)


def get_text(name: str) -> str:
    return cached_strings[name]
