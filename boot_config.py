# coding=utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import time
import sys, os
import traceback
import gzip, json
from os.path import dirname, join, isdir, expanduser

APP_NAME = "KoHighlights"
APP_DIR = dirname(os.path.abspath(sys.argv[0]))
os.chdir(APP_DIR)  # Set the current working directory to the app's directory

if sys.platform == "win32":  # Windows
    class SingleInstance:
        """ Limits application to single instance
        """
        def __init__(self, name):
            import win32event
            import win32api
            self.mutex = win32event.CreateMutex(None, False, name)
            self.lasterror = win32api.GetLastError()

        def already_running(self):
            from winerror import ERROR_ALREADY_EXISTS
            return self.lasterror == ERROR_ALREADY_EXISTS

        def __del__(self):
            import win32api
            win32api.CloseHandle(self.mutex) if self.mutex else None

    my_app = SingleInstance(APP_NAME)
    if my_app.already_running():  # another instance is running
        sys.exit(0)
    SETTINGS_DIR = join(os.environ["APPDATA"], APP_NAME)
elif sys.platform == "darwin":  # MacOS 2check: needs to be tested
    import socket
    app_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        app_socket.bind(("127.0.0.1", 42001))  # use a specific port
        # app_socket.listen(1)
    except socket.error:  # port in use - another instance is running
        sys.exit(0)
    SETTINGS_DIR = join(expanduser("~"), "Library", "Application Support", APP_NAME)
else:  # Linux+
    try:
        import socket
        app_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # Create an abstract socket, by prefixing it with null.
        app_socket.bind(str("\0{}_lock_port".format(APP_NAME)))
    except socket.error:  # port in use - another instance is running
        sys.exit(0)
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


PYTHON2 = True if not sys.version_info >= (3, 0) else False
FIRST_RUN = False
# noinspection PyBroadException
try:
    with gzip.GzipFile(join(SETTINGS_DIR, "settings.json.gz")) as settings:
        j_text = settings.read() if PYTHON2 else settings.read().decode("utf8")
        app_config = json.loads(j_text)
except Exception:  # IOError on first run or everything else
    app_config = {}
    FIRST_RUN = True


BOOKS_VIEW, HIGHLIGHTS_VIEW = range(2)  # app views
TITLE, AUTHOR, TYPE, PERCENT, MODIFIED, PATH = range(6)  # file_table columns
PAGE, HIGHLIGHT_TEXT, DATE, PAGE_ID, COMMENT = range(5)  # high_list item data
(HIGHLIGHT_H, COMMENT_H,
 DATE_H, TITLE_H, PAGE_H, AUTHOR_H, PATH_H) = range(7)  # high_table columns
MANY_TEXT, ONE_TEXT, MANY_HTML, ONE_HTML, MERGED_HIGH = range(5)  # save_actions
DB_MD5, DB_DATE, DB_PATH, DB_DATA = range(4)  # db data (columns)

DB_VERSION = 0
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {background-color: white;}
        .book-block {
            border: 2px solid rgba(20, 20, 20, 0.5);
            padding: 20px;
            padding-top: 5px;
            background-color: #cdcdcd;
            border-radius: 25px;
        }
        .high-block {
            border: 2px solid rgba(115, 173, 33, 0.5);
            padding: 20px;
            background-color: #ebebeb;
            border-radius: 20px;
        }
    </style>
    <title>KoHighlights</title>
</head>
<body>
"""
BOOK_BLOCK = """
<div class="book-block">

<div align="center">
    <h2 style="display: inline;">%(title)s</h2><br/>
    <h3 style="display: inline;">%(authors)s</h3>
</div>
"""
HIGH_BLOCK = """
<div class="high-block">
    <p style="text-align:left;float:left;padding:1px; margin:0;">%(page)s</p>
    <p style="text-align:right;float:right;padding:1px; margin:0;">%(date)s</p>
    <hr style="clear:both;"/>
    <p>%(highlight)s</p>
    <p>%(comment)s</p>
</div>
"""
