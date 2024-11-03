# coding=utf-8
import time
import sys, os
import traceback
import gzip, json
from os.path import dirname, join, isdir, expanduser, abspath

__author__ = "noEmbryo"


def _(text):  # for future gettext support
    return text


APP_NAME = "KOHighlights"
APP_DIR = dirname(abspath(__file__))
try:
    # noinspection PyUnresolvedReferences,PyProtectedMember
    BASE_DIR = sys._MEIPASS
except AttributeError:  # loading from py, not an exe
    BASE_DIR = APP_DIR
os.chdir(BASE_DIR)  # Set the current working directory to the app's directory

USE_QT6 = False  # select between PySide2/Qt5 and Pyside6/Qt6 if both are installed

if USE_QT6:
    from PySide6.QtCore import qVersion
else:
    from PySide2.QtCore import qVersion

# noinspection PyTypeChecker
qt_version = qVersion().split(".")[0]
QT5 = qt_version == "5"
QT6 = qt_version == "6"
if QT6 and QT5 and USE_QT6:
    QT5 = False

PORTABLE = False
if sys.platform == "win32":  # Windows
    import win32api
    import win32event
    from winerror import ERROR_ALREADY_EXISTS

    class SingleInstance:
        """ Limits application to single instance
        """
        def __init__(self, name):
            self.mutex = win32event.CreateMutex(None, False, name)
            self.lasterror = win32api.GetLastError()

        def already_running(self):
            return self.lasterror == ERROR_ALREADY_EXISTS

        def __del__(self):
            import win32api  # needed otherwise raises Exception AttributeError
            win32api.CloseHandle(self.mutex) if self.mutex else None

    my_app = SingleInstance(APP_NAME)
    if my_app.already_running():  # another instance is running
        sys.exit(0)
    try:
        # noinspection PyUnresolvedReferences
        portable_arg = sys.argv[1]
        PORTABLE = portable_arg == "-p"
    except IndexError:  # no arguments in the call
        pass
    PROFILE_DIR = join(os.environ[str("APPDATA")], APP_NAME)
    PORTABLE_DIR = join(APP_DIR, "portable_settings")
    SETTINGS_DIR = PORTABLE_DIR if PORTABLE else PROFILE_DIR
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
        app_socket.bind(str(f"\0{APP_NAME}_lock_port"))
    except socket.error:  # port in use - another instance is running
        sys.exit(0)
    SETTINGS_DIR = join(expanduser("~"), ".config", APP_NAME)
os.makedirs(SETTINGS_DIR) if not isdir(SETTINGS_DIR) else None


def except_hook(class_type, value, trace_back):
    """ Print the error to a log file
    """
    name = join(SETTINGS_DIR, f"error_log_{time.strftime(str('%Y-%m-%d'))}.txt")
    with open(name, "a", encoding="utf8") as log:
        log.write(f"\nCrash@{time.strftime(str('%Y-%m-%d %H:%M:%S'))}\n")
    traceback.print_exception(class_type, value, trace_back, file=open(name, str("a")))
    sys.__excepthook__(class_type, value, trace_back)


sys.excepthook = except_hook
FIRST_RUN = False
# noinspection PyBroadException
try:
    with gzip.GzipFile(join(SETTINGS_DIR, "settings.json.gz")) as settings:
        app_config = json.loads(settings.read().decode("utf8"))
except Exception:  # IOError on first run or everything else
    app_config = {}
    FIRST_RUN = True


BOOKS_VIEW, HIGHLIGHTS_VIEW, SYNC_VIEW = range(3)  # app views
CHANGE_DB, NEW_DB, RELOAD_DB = range(3)  # db change mode
(TITLE, AUTHOR, TYPE, PERCENT, RATING,
 HIGH_COUNT, MODIFIED, PATH) = range(8)  # file_table columns
PAGE, HIGHLIGHT_TEXT, DATE, PAGE_ID, COMMENT = range(5)  # high_list item data
(HIGHLIGHT_H, COMMENT_H, DATE_H, TITLE_H,
 AUTHOR_H, PAGE_H, CHAPTER_H, PATH_H) = range(8)  # high_table columns
(MANY_TEXT, ONE_TEXT, MANY_HTML, ONE_HTML,
 MANY_CSV, ONE_CSV, MANY_MD, ONE_MD) = range(8)  # save_actions
DB_MD5, DB_DATE, DB_PATH, DB_DATA = range(4)  # db data (columns)
FILTER_ALL, FILTER_HIGH, FILTER_COMM, FILTER_TITLES = range(4)  # filter type
(THEME_NONE_OLD, THEME_NONE_NEW, THEME_DARK_OLD, THEME_DARK_NEW,
 THEME_LIGHT_OLD, THEME_LIGHT_NEW) = range(6)  # theme idx
ACT_PAGE, ACT_DATE, ACT_TEXT, ACT_CHAPTER, ACT_COMMENT = range(5)  # show items actions
HI_DATE, HI_COMMENT, HI_TEXT, HI_PAGE, HI_CHAPTER = range(5)  # highlight items
DEL_META, DEL_BOOKS, DEL_MISSING = range(3)


NO_TITLE = _("NO TITLE FOUND")
NO_AUTHOR = _("NO AUTHOR FOUND")
OLD_TYPE = _("OLD TYPE FILE")
DO_NOT_SHOW = _("Don't show this again")
DB_VERSION = 0
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
TOOLTIP_MERGE = _("Merge the highlights from the same book in two different\ndevices, "
                  "and/or sync their reading position.\nActivated only if two entries "
                  "of the same book are selected.")
TOOLTIP_SYNC = _("Start the sync process for all enabled groups")
HIGH_COL_NAMES = ["Highlight", "Comment", "Date", "Title",
                  "Author", "Page", "Chapter", "Path"]
SYNC_FILE = join(SETTINGS_DIR, "sync_groups.json")
SPLITTER = " ▸ "

CSV_HEAD = "Title\tAuthors\tPage\tDate\tChapter\tHighlight\tComment\n"
CSV_KEYS = ["title", "authors", "page", "date", "chapter", "text", "comment"]
MD_HEAD = "\n---\n## {0}  \n##### {1}  \n---\n"
MD_HIGH = "*Page {3} [{0}]:*  \n***{4}***  \n  \n{2}  \n● {1}  \n&nbsp;  \n\n"
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
    <h4>%(chapter)s</h4>
    <p>%(highlight)s</p>
    <p>%(comment)s</p>
</div>
"""
