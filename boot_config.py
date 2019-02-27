# coding=utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import time
import sys, os
import traceback
from os.path import dirname, join, isdir, expanduser

APP_NAME = "KoHighlights"
APP_DIR = dirname(os.path.abspath(sys.argv[0]))
os.chdir(APP_DIR)  # Set the current working directory to the app's directory
if sys.platform == "win32":  # Windows
    SETTINGS_DIR = join(os.environ["APPDATA"], APP_NAME)
elif sys.platform == "darwin":  # MacOS
    SETTINGS_DIR = join(expanduser("~"), "Library",
                        "Application Support", APP_NAME)
else:  # Linux+
    SETTINGS_DIR = join(expanduser("~"), ".config", APP_NAME)
os.makedirs(SETTINGS_DIR) if not isdir(SETTINGS_DIR) else None


def except_hook(class_type, value, trace_back):
    """ Print the error to a log file
    """
    name = join(SETTINGS_DIR, "error_log_{}.txt".format(time.strftime(str("%Y-%m-%d"))))
    with open(name, "a") as log:
        log.write(str("\nCrash@{}\n").format(time.strftime(str("%Y-%m-%d %H:%M:%S"))))
    traceback.print_exception(class_type, value, trace_back, file=open(name, "a"))
    sys.__excepthook__(class_type, value, trace_back)


sys.excepthook = except_hook

import gzip, json

try:
    with gzip.GzipFile(join(SETTINGS_DIR, "settings.json.gz"), "rb") as settings:
        app_config = json.loads(settings.read())
except IOError:  # first run
    app_config = {}

FIRST_RUN = not bool(app_config)
PAGE, HIGHLIGHT_TEXT, DATE, PAGE_ID, COMMENT = range(5)  # highlights_list item data
TITLE, AUTHOR, TYPE, PERCENT, MODIFIED, PATH = range(6)  # highlight_table columns
HIGHLIGHT_H, COMMENT_H, DATE_H, TITLE_H, PAGE_H, AUTHOR_H = range(6)  # -//- item data
