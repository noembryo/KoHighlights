# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
from boot_config import *
import os, sys, re, io
import gzip
import json
import shutil
import webbrowser
import subprocess
import argparse
from datetime import datetime
from functools import partial
from collections import defaultdict
from distutils.version import LooseVersion
from os.path import (isdir, isfile, join, basename, splitext, dirname, split,
                     getmtime, abspath)


# ___ _____________ DEPENDENCIES ____________________________________
from PySide.QtSql import QSqlDatabase, QSqlQuery
from PySide.QtCore import (Qt, QTimer, Slot,QThread, QMimeData, QModelIndex, QByteArray,
                           QPoint)
from PySide.QtGui import (QMainWindow, QApplication, QMessageBox, QIcon, QFileDialog,
                          QTableWidgetItem, QTextCursor, QMenu, QAction, QHeaderView,
                          QPixmap, QListWidgetItem)


from secondary import *
from gui_main import Ui_Base
from slppu import slppu as lua  # https://github.com/noembryo/slppu


try:  # ___ _______ PYTHON 2/3 COMPATIBILITY ________________________
    import cPickle as pickle
except ImportError:  # python 3.x
    import pickle
    # noinspection PyShadowingBuiltins
    unicode = str
from pprint import pprint


__author__ = "noEmbryo"
__version__ = "0.9.1.0"


def _(text):  # for future gettext support
    return text


def decode_data(path):
    """ Converts a lua table to a Python dict

    :type path: str|unicode
    :param path: The path to the lua file
    """
    with io.open(path, "r", encoding="utf8", newline=None) as txt_file:
        txt = txt_file.read()[39:]  # offset the first words of the file
        data = lua.decode(txt.replace("--", "—"))
        if type(data) == dict:
            return data


def encode_data(path, dict_data):
    """ Converts a Python dict to a lua table

    :type path: str|unicode
    :param path: The path to the lua file
    :type dict_data: dict
    :param dict_data: The dictionary to be encoded as lua table
    """
    with io.open(path, "w+", encoding="utf8", newline="") as txt_file:
        lua_text = "-- we can read Lua syntax here!\nreturn "
        lua_text += lua.encode(dict_data)
        txt_file.write(lua_text)


def sanitize_filename(filename):
    """ Creates a safe filename

    :type filename: str|unicode
    :param filename: The filename to be sanitized
    """
    filename = re.sub(r'[/:*?"<>|\\]', "_", filename)
    return filename


# if sys.platform.lower().startswith("win"):
#     import ctypes
#
#     def hide_console():
#         """ Hides the console window in GUI mode. Necessary for frozen application,
#         because this application support both, command line processing AND GUI mode
#         and therefor cannot be run via pythonw.exe.
#         """
#
#         win_handles = ctypes.windll.kernel32.GetConsoleWindow()
#         if win_handles != 0:
#             ctypes.windll.user32.ShowWindow(win_handles, 0)
#             # if you wanted to close the handles...
#             # ctypes.windll.kernel32.CloseHandle(win_handles)
#
#     def show_console():
#         """ UnHides console window"""
#         win_handles = ctypes.windll.kernel32.GetConsoleWindow()
#         if win_handles != 0:
#             ctypes.windll.user32.ShowWindow(win_handles, 1)


class Base(QMainWindow, Ui_Base):
    def __init__(self, parent=None):
        super(Base, self).__init__(parent)

        self.scan_thread = None
        # self.highlight_scan_thread = QThread()
        self.setupUi(self)
        self.version = __version__

        # ___ ________ SAVED SETTINGS ___________
        self.col_sort = MODIFIED
        self.col_sort_asc = False
        self.col_sort_h = DATE_H
        self.col_sort_asc_h = False
        self.highlight_width = None
        self.comment_width = None
        self.skip_version = "0.0.0.0"
        self.opened_times = 0
        self.last_dir = os.getcwd()
        self.edit_lua_file_warning = True
        self.high_merge_warning = True
        self.current_view = 0
        self.toolbar_size = 48
        self.high_by_page = False
        self.exit_msg = True
        self.date_vacuumed = datetime.now().strftime(DATE_FORMAT)
        # ___ ___________________________________

        self.file_selection = None
        self.sel_idx = None
        self.sel_indexes = []
        self.high_view_selection = None
        self.sel_high_view = []
        self.high_list_selection = None
        self.sel_high_list = []

        self.loaded_paths = set()
        self.books2reload = set()
        self.parent_book_data = {}
        self.reload_highlights = True
        self.threads = []

        self.query = None
        self.db = None
        self.db_view = False
        self.books = []

        self.file_table.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.header_main = self.file_table.horizontalHeader()
        self.header_main.setMovable(True)
        self.header_main.setDefaultAlignment(Qt.AlignLeft)

        self.high_table.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.header_high_view = self.high_table.horizontalHeader()
        self.header_high_view.setMovable(True)
        self.header_high_view.setDefaultAlignment(Qt.AlignLeft)
        # self.header_high_view.setResizeMode(HIGHLIGHT_H, QHeaderView.Stretch)

        self.info_fields = [self.title_txt, self.author_txt, self.series_txt,
                            self.lang_txt, self.pages_txt, self.tags_txt]
        self.info_keys = ["title", "authors", "series", "language", "pages", "keywords"]

        self.ico_file_save = QIcon(":/stuff/file_save.png")
        self.ico_files_merge = QIcon(":/stuff/files_merge.png")
        self.ico_files_delete = QIcon(":/stuff/files_delete.png")
        self.ico_file_exists = QIcon(":/stuff/file_exists.png")
        self.ico_file_missing = QIcon(":/stuff/file_missing.png")
        self.ico_file_edit = QIcon(":/stuff/file_edit.png")
        self.ico_copy = QIcon(":/stuff/copy.png")
        self.ico_delete = QIcon(":/stuff/delete.png")
        self.ico_label_green = QIcon(":/stuff/label_green.png")
        self.ico_view_books = QIcon(":/stuff/view_books.png")
        self.ico_db_add = QIcon(":/stuff/db_add.png")
        self.ico_empty = QIcon(":/stuff/trans32.png")

        self.about = About(self)
        self.auto_info = AutoInfo(self)

        self.toolbar = ToolBar(self)
        self.tool_bar.addWidget(self.toolbar)
        self.toolbar.open_btn.setEnabled(False)
        self.toolbar.merge_btn.setEnabled(False)
        self.toolbar.delete_btn.setEnabled(False)

        self.status = Status(self)
        self.statusbar.addPermanentWidget(self.status)

        self.edit_high = TextDialog(self)
        self.edit_high.on_ok = self.edit_comment_ok
        self.edit_high.setWindowTitle(_("Comments"))

        self.description = TextDialog(self)
        self.description.setWindowTitle(_("Description"))
        self.description.high_edit_txt.setReadOnly(True)
        self.description.btn_box.hide()
        self.description_btn.setEnabled(False)

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        # noinspection PyArgumentList
        self.clip = QApplication.clipboard()

        # noinspection PyTypeChecker,PyCallByClass
        QTimer.singleShot(0, self.on_load)

        # noinspection PyTypeChecker,PyCallByClass
        QTimer.singleShot(30000, self.auto_check4update)  # check for updates

        main_timer = QTimer(self)  # cleanup threads for ever
        main_timer.timeout.connect(self.thread_cleanup)
        main_timer.start(2000)

    def on_load(self):
        """ Things that must be done after the initialization
        """
        self.init_db()
        self.settings_load()
        if FIRST_RUN:  # on first run
            self.toolbar.books_btn.click()
            self.splitter.setSizes((500, 250))
        self.toolbar.export_btn.setMenu(self.save_menu())  # assign/create menu
        self.toolbar.merge_btn.setMenu(self.merge_menu())  # assign/create menu
        self.toolbar.delete_btn.setMenu(self.delete_menu())  # assign/create menu
        self.connect_gui()
        self.passed_files()
        self.show()

    # ___ ___________________ EVENTS STUFF __________________________

    # noinspection PyUnresolvedReferences
    def connect_gui(self):
        """ Make all the signal/slots connections
        """
        self.file_selection = self.file_table.selectionModel()
        self.file_selection.selectionChanged.connect(self.file_selection_update)
        self.header_main.sectionClicked.connect(self.on_column_clicked)
        self.high_list_selection = self.high_list.selectionModel()
        self.high_list_selection.selectionChanged.connect(self.high_list_selection_update)

        self.high_view_selection = self.high_table.selectionModel()
        self.high_view_selection.selectionChanged.connect(self.high_view_selection_update)
        self.header_high_view.sectionClicked.connect(self.on_highlight_column_clicked)
        self.header_high_view.sectionResized.connect(self.on_highlight_column_resized)

        sys.stdout = LogStream()
        sys.stdout.setObjectName("out")
        sys.stdout.append_to_log.connect(self.write_to_log)
        sys.stderr = LogStream()
        sys.stderr.setObjectName("err")
        sys.stderr.append_to_log.connect(self.write_to_log)

    def keyPressEvent(self, event):
        """ Handles the key press events

        :type event: QKeyEvent
        :param event: The key press event
        """
        key, mod = event.key(), event.modifiers()
        # print(key, mod, QKeySequence(key).toString())
        if mod == Qt.ControlModifier:  # if control is pressed
            if key == Qt.Key_Backspace:
                self.toolbar.on_clear_btn_clicked()
                return True
            if key == Qt.Key_L:
                self.toolbar.on_select_btn_clicked()
                return True
            if key == Qt.Key_S:
                self.save_actions(MANY_TEXT)
                return True
            if key == Qt.Key_O:
                self.toolbar.on_info_btn_clicked()
                return True
            if key == Qt.Key_Q:
                self.close()
        if mod == Qt.AltModifier:  # if alt is pressed
            if key == Qt.Key_A:
                self.on_archive()

        if key == Qt.Key_Escape:
            self.close()
        if key == Qt.Key_Delete:  # Delete
            self.delete_actions(0)
            return True

    def closeEvent(self, event):
        """ Accepts or rejects the `exit` command

        :type event: QCloseEvent
        :param event: The `exit` event
        """
        if not self.exit_msg:
            self.bye_bye_stuff()
            event.accept()
            return
        popup = self.popup(_("Confirmation"), _("Exit KoHighlights?"), buttons=2,
                           check_text=_("Don't show this again"))
        self.exit_msg = not popup.checked
        if popup.buttonRole(popup.clickedButton()) == QMessageBox.AcceptRole:
            self.bye_bye_stuff()
            event.accept()  # let the window close
        else:
            event.ignore()

    def bye_bye_stuff(self):
        """ Things to do before exit
        """
        self.settings_save()
        self.delete_logs()

    # ___ ____________________ DATABASE STUFF __________________________

    def init_db(self):
        """ Initialize the database tables
        """
        db_exists = isfile(join(SETTINGS_DIR, "data.db"))
        # noinspection PyTypeChecker,PyCallByClass
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(join(SETTINGS_DIR, "data.db"))
        if not self.db.open():
            print("Could not open database!")
            return
        self.query = QSqlQuery()
        self.set_db_version() if not db_exists else None
        self.create_feeds_table()
        if app_config:
            self.query.exec_("""PRAGMA user_version""")
            while self.query.next():
                self.check_db_version(self.query.value(0))  # check the db version
                # self.query.exec_("""PRAGMA user_version = 1""")

    def create_feeds_table(self):
        """ Create the feeds table
        """
        self.query.exec_("""CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, 
                         md5 TEXT UNIQUE NOT NULL, date TEXT, path TEXT, data TEXT)""")

    def check_db_version(self, version):
        """ Updates the db to the last version

        :type version: int
        :param version: The db file version
        """
        if version == DB_VERSION or not isfile(join(SETTINGS_DIR, "data.db")):
            return  # the db is up to date or does not exists yet
        self.ask_upgrade(version)

    def set_db_version(self):
        """ Set the database version as current
        """
        self.query.exec_("""PRAGMA user_version = {}""".format(DB_VERSION))

    def add_books2db(self, books):
        """ Add some books to the books db table

        :type books: list
        :param books: The books to add in the db
        """
        self.db.transaction()
        self.query.prepare("""INSERT OR REPLACE into books (md5, date, path, data) 
                           VALUES (:md5, :date, :path, :data)""")
        for book in books:
            self.query.bindValue(":md5", book["md5"])
            self.query.bindValue(":date", book["date"])
            self.query.bindValue(":path", book["path"])
            self.query.bindValue(":data", book["data"])
            self.query.exec_()
        self.db.commit()

    def read_books_from_db(self):
        """ Reads the contents of the books' db table
        """
        del self.books[:]
        self.query.setForwardOnly(True)
        self.query.exec_("""SELECT * FROM books""")
        while self.query.next():
            book = [self.query.value(i) for i in range(1, 5)]  # don't read the id
            self.books.append({"md5": book[DB_MD5], "date": book[DB_DATE],
                               "path": book[DB_PATH], "data": json.loads(book[DB_DATA])})

    def update_book2db(self, data):
        """ Updates the data of a book in the db

        :type data: dict
        :param data: The changed data
        """
        self.query.prepare("""UPDATE books SET data = :data WHERE md5 = :md5""")
        self.query.bindValue(":md5", data["partial_md5_checksum"])
        self.query.bindValue(":data", json.dumps(data))
        self.query.exec_()

    def delete_books_from_db(self, ids):
        """ Deletes multiple books from the db

        :type ids: list
        :param ids: The md5s of the books to be deleted
        """
        if ids:
            self.db.transaction()
            self.query.prepare("""DELETE FROM books WHERE md5 = :md5""")
            for md5 in ids:
                self.query.bindValue(":md5", md5)
                self.query.exec_()
            self.db.commit()

    def get_db_book_count(self):
        """ Get the count of the books in the db
        """
        self.query.exec_("""SELECT Count(*) FROM books""")
        self.query.next()
        return self.query.value(0)

    def vacuum_db(self, info=True):
        self.query.exec_("""VACUUM""")
        if info:
            self.popup(_("Information"), _("The database is compacted!"),
                       QMessageBox.Information)

    # ___ ___________________ FILE TABLE STUFF ______________________

    @Slot(list)
    def on_file_table_fileDropped(self, dropped):
        """ When some items are dropped to the TableWidget

        :type dropped: list
        :param dropped: The items dropped
        """
        self.file_table.setSortingEnabled(False)
        for i in dropped:
            if splitext(i)[1] == ".lua":
                self.create_row(i)
        self.file_table.setSortingEnabled(True)
        folders = [j for j in dropped if isdir(j)]
        for folder in folders:
            # self.scan_files_thread(folder)
            text = _("Scanning for KoReader metadata files")
            self.loading_thread(Scanner, folder, text, clear=False)

    # @Slot(QTableWidgetItem)  # its called indirectly from self.file_selection_update
    def on_file_table_itemClicked(self, item, reset=True):
        """ When an item of the FileTable is clicked

        :type item: QTableWidgetItem
        :param item: The item (cell) that is clicked
        :type reset: bool
        :param reset: Select the first highlight in the list
        """
        if not item:  # empty list
            return
        row = item.row()
        data = self.file_table.item(row, TITLE).data(Qt.UserRole)

        self.high_list.clear()
        self.populate_high_list(data)
        self.populate_book_info(data, row)

        description_state = False
        if "doc_props" in data and "description" in data["doc_props"]:
            description_state = bool(data["doc_props"]["description"])
        self.description_btn.setEnabled(description_state)

        # self.high_list.sortItems()  # using XListWidgetItem for custom sorting
        self.high_list.setCurrentRow(0) if reset else None

    def populate_book_info(self, data, row):
        """ Fill in the `Book Info` fields

        :type data: dict
        :param data: The item's data
        :type row: int
        :param row: The item's row number
        """
        for key, field in zip(self.info_keys, self.info_fields):
            try:
                if key == "title" and not data["stats"][key]:
                    path = self.file_table.item(row, PATH).data(0)
                    try:
                        name = path.split("#] ")[1]
                        value = splitext(name)[0]
                    except IndexError:  # no "#] " in filename
                        value = ""
                elif key == "keywords":
                    keywords = data["doc_props"][key].split("\n")
                    value = "; ".join([i.rstrip("\\") for i in keywords])
                else:
                    value = data["stats"][key]
                try:
                    field.setText(value)
                except TypeError:  # Needs string only
                    field.setText(str(value) if value else "")  # "" if 0
            except KeyError:  # older type file or other problems
                path = self.file_table.item(row, PATH).data(0)
                stats = self.get_item_stats(path, data)
                if key == "title":
                    field.setText(stats[1])
                elif key == "authors":
                    field.setText(stats[2])
                else:
                    field.setText("")

    @Slot()
    def on_description_btn_clicked(self):
        """ The book's `Description` button is pressed
        """
        data = self.file_table.item(self.sel_idx.row(), TITLE).data(Qt.UserRole)
        description = data["doc_props"]["description"]
        self.description.high_edit_txt.setHtml(description)
        self.description.show()

    @Slot(QPoint)
    def on_file_table_customContextMenuRequested(self, point):
        """ When an item of the FileTable is right-clicked

        :type point: QPoint
        :param point: The point where the right-click happened
        """
        if not len(self.file_selection.selectedRows()):  # no items selected
            return

        menu = QMenu(self.file_table)

        row = self.file_table.itemAt(point).row()
        self.act_view_book.setEnabled(self.toolbar.open_btn.isEnabled())
        self.act_view_book.setData(row)
        menu.addAction(self.act_view_book)

        if len(self.file_selection.selectedRows()) > 1:  # many items selected
            save_menu = self.save_menu()
            save_menu.setIcon(self.ico_file_save)
            save_menu.setTitle(_("Export"))
            menu.addMenu(save_menu)
        else:  # only one item selected
            action = QAction(_("Export to text"), menu)
            action.setIcon(self.ico_file_save)
            action.triggered.connect(self.on_save_actions)
            action.setData(MANY_TEXT)
            menu.addAction(action)

            action = QAction(_("Export to html"), menu)
            action.setIcon(self.ico_file_save)
            action.triggered.connect(self.on_save_actions)
            action.setData(MANY_HTML)
            menu.addAction(action)

        if not self.db_view:
            action = QAction(_("Archive\tAlt+A"), menu)
            action.setIcon(self.ico_db_add)
            action.triggered.connect(self.on_archive)
            menu.addAction(action)

            delete_menu = self.delete_menu()
            delete_menu.setIcon(self.ico_files_delete)
            delete_menu.setTitle(_("Delete\tDel"))
            menu.addMenu(delete_menu)
        else:
            action = QAction(_("Delete\tDel"), menu)
            action.setIcon(self.ico_files_delete)
            action.triggered.connect(partial(self.delete_actions, 0))
            menu.addAction(action)

        # # noinspection PyArgumentList
        # menu.exec_(QCursor.pos())
        menu.exec_(self.file_table.mapToGlobal(point))

    @Slot(QTableWidgetItem)
    def on_file_table_itemDoubleClicked(self, item):
        """ When an item of the FileTable is double-clicked

        :type item: QTableWidgetItem
        :param item: The item (cell) that is double-clicked
        """
        row = item.row()
        meta_path = splitext(self.file_table.item(row, PATH).data(0))[0]
        book_path = self.get_book_path(meta_path)
        self.open_file(book_path)

    @staticmethod
    def get_book_path(path):
        """ Returns the filename of the book that the metadata refers to

        :type path: str|unicode
        :param path: The path of the metadata file
        """
        path, ext = splitext(path)
        path = splitext(split(path)[0])[0] + ext
        return path

    @Slot()
    def on_act_view_book_triggered(self):
        """ The View Book menu entry is pressed
        """
        row = self.sender().data()
        if self.current_view == 0:  # books view
            item = self.file_table.itemAt(row, 0)
            self.on_file_table_itemDoubleClicked(item)
        elif self.current_view == 1:  # highlights view
            data = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
            self.open_file(data["path"])

    # noinspection PyUnusedLocal
    def file_selection_update(self, selected, deselected):
        """ When a row in FileTable gets selected

        :type selected: QModelIndex
        :parameter selected: The selected row
        :type deselected: QModelIndex
        :parameter deselected: The deselected row
        """
        try:
            self.sel_indexes = self.file_selection.selectedRows()
            self.sel_idx = self.sel_indexes[-1]
        except IndexError:  # empty table
            self.sel_indexes = []
            self.sel_idx = None
        # if self.file_selection.selectedRows():
        #     idx = selected.indexes()[0]
        if self.sel_indexes:
            item = self.file_table.item(self.sel_idx.row(), self.sel_idx.column())
            self.on_file_table_itemClicked(item)
        else:
            self.high_list.clear()
            self.description_btn.setEnabled(False)
            for field in self.info_fields:
                field.setText("")
        self.toolbar.activate_buttons()

    def on_column_clicked(self, column):
        """ Sets the current sorting column

        :type column: int
        :parameter column: The column where the filtering is applied
        """
        if column == self.col_sort:
            self.col_sort_asc = not self.col_sort_asc
        else:
            self.col_sort_asc = True
        self.col_sort = column

    @Slot(bool)
    def on_fold_btn_toggled(self, pressed):
        """ Open/closes the Book info panel

        :type pressed: bool
        :param pressed: The arrow button"s status
        """
        if pressed:  # Closed
            self.fold_btn.setText(_("Show Book Info"))
            self.fold_btn.setArrowType(Qt.RightArrow)
        else:  # Opened
            self.fold_btn.setText(_("Hide Book Info"))
            self.fold_btn.setArrowType(Qt.DownArrow)
        self.book_info.setHidden(pressed)

    def on_archive(self):
        """ Add the selected books to the archive db
        """
        if not self.sel_indexes:
            return
        empty = 0
        older = 0
        added = 0
        books = []
        for idx in self.sel_indexes:
            row = idx.row()
            path = self.file_table.item(row, PATH).text()
            date = self.file_table.item(row, MODIFIED).text()
            data = self.file_table.item(row, TITLE).data(Qt.UserRole)
            if not data["highlight"]:  # no highlights, don't add
                empty += 1
                continue
            try:
                md5 = data["partial_md5_checksum"]
            except KeyError:  # older metadata, don't add
                older += 1
                continue
            data["stats"]["performance_in_pages"] = {}  # can be cluttered
            data["page_positions"] = {}  # can be cluttered
            books.append({"md5": md5, "path": path, "date": date,
                          "data": json.dumps(data)})
            added += 1
        self.add_books2db(books)

        extra = ""
        if empty:
            extra += _("\nNot added {} books with no highlights.").format(empty)
        if older:
            extra += _("\nNot added {} books with old type metadata.").format(older)

        self.popup(_("Added!"),
                   _("{} books were added/updated to the Archive from the {} processed.")
                   .format(added, len(self.sel_indexes)) + extra,
                   icon=QMessageBox.Information)

    def loading_thread(self, worker, args, text, clear=True):
        """ Populates the file_table with different contents
        """
        if clear:
            self.toolbar.on_clear_btn_clicked()
        self.file_table.setSortingEnabled(False)  # re-enable it after populating table

        self.status.animation("start")
        self.auto_info.set_text(_("{}.\nPlease Wait...").format(text))
        self.auto_info.show()

        scan_thread = QThread()
        loader = worker(args)
        loader.moveToThread(scan_thread)
        loader.found.connect(self.create_row)
        loader.finished.connect(self.scan_finished)
        loader.finished.connect(scan_thread.quit)
        loader.finished.connect(self.thread_cleanup)
        scan_thread.loader = loader
        scan_thread.started.connect(loader.process)
        scan_thread.start(QThread.IdlePriority)
        self.threads.append(scan_thread)

    def scan_finished(self):
        """ What will happen after the populating of the file_table ends
        """
        if self.current_view == 1:  # loading books from highlights view
            self.scan_highlights_thread()
        else:
            self.status.animation("stop")
            self.auto_info.hide()

        self.file_table.clearSelection()
        self.sel_idx = None
        self.sel_indexes = []
        self.file_table.resizeColumnsToContents()
        self.toolbar.activate_buttons()

        self.file_table.setSortingEnabled(True)
        order = Qt.AscendingOrder if self.col_sort_asc else Qt.DescendingOrder
        self.file_table.sortByColumn(self.col_sort, order)

    def create_row(self, filename, data=None, date=None):
        """ Creates a table row from the given file

        :type filename: str|unicode
        :param filename: The metadata file to be read
        """
        if not self.db_view:
            # if exists(filename) and splitext(filename)[1].lower() == '.lua':
            if filename in self.loaded_paths:
                return  # already loaded file
            self.loaded_paths.add(filename)
            data = decode_data(filename)
            if not data:
                print("No data here!", filename)
                return
            date = str(datetime.fromtimestamp(getmtime(filename)))
            icon, title, authors, percent = self.get_item_stats(filename, data)
        else:
            icon, title, authors, percent = self.get_item_db_stats(data)

        self.file_table.insertRow(0)

        title_item = QTableWidgetItem(icon, title)
        title_item.setToolTip(title)
        title_item.setData(Qt.UserRole, data)
        self.file_table.setItem(0, TITLE, title_item)

        author_item = QTableWidgetItem(authors)
        author_item.setToolTip(authors)
        self.file_table.setItem(0, AUTHOR, author_item)

        ext = splitext(splitext(filename)[0])[1][1:]
        book_path = splitext(self.get_book_path(filename))[0] + "." + ext
        book_exists = isfile(book_path)
        book_icon = self.ico_file_exists if book_exists else self.ico_file_missing
        type_item = QTableWidgetItem(book_icon, ext)
        type_item.setToolTip(book_path if book_exists else
                             _("The {} file is missing!").format(ext))
        type_item.setData(Qt.UserRole, (book_path, book_exists))
        self.file_table.setItem(0, TYPE, type_item)

        percent_item = QTableWidgetItem(percent)
        percent_item.setToolTip(percent)
        percent_item.setTextAlignment(Qt.AlignRight)
        self.file_table.setItem(0, PERCENT, percent_item)

        date_item = QTableWidgetItem(date)
        date_item.setToolTip(date)
        self.file_table.setItem(0, MODIFIED, date_item)

        path_item = QTableWidgetItem(filename)
        path_item.setToolTip(filename)
        self.file_table.setItem(0, PATH, path_item)

    def get_item_db_stats(self, data):
        """ Returns the title and authors of a history file

        :type data: dict
        :param data: The dict converted lua file
        """
        title = data["stats"]["title"]
        authors = data["stats"]["authors"]
        title = title if title else _("NO TITLE FOUND")
        authors = authors if authors else _("NO AUTHOR FOUND")
        try:
            percent = data["percent_finished"]
            percent = str(int(percent * 100)) + "%"
            percent = "Complete" if percent == "100%" else percent
        except KeyError:
            percent = None

        icon = self.ico_label_green if data["highlight"] else self.ico_empty
        return icon, title, authors, percent

    def get_item_stats(self, filename, data):
        """ Returns the title and authors of a metadata file

        :type filename: str|unicode
        :param filename: The filename to get the stats for
        :type data: dict
        :param data: The dict converted lua file
        """
        try:
            title = data["stats"]["title"]
            authors = data["stats"]["authors"]
        except KeyError:  # older type file
            title = splitext(basename(filename))[0]
            try:
                name = title.split("#] ")[1]
                title = splitext(name)[0]
            except IndexError:  # no "#] " in filename
                pass
            authors = _("OLD TYPE FILE")
        if not title:
            try:
                name = filename.split("#] ")[1]
                title = splitext(name)[0]
            except IndexError:  # no "#] " in filename
                title = _("NO TITLE FOUND")
        authors = authors if authors else _("NO AUTHOR FOUND")
        try:
            percent = data["percent_finished"]
            percent = str(int(percent * 100)) + "%"
            percent = "Complete" if percent == "100%" else percent
        except KeyError:
            percent = None

        icon = self.ico_label_green if data["highlight"] else self.ico_empty
        return icon, title, authors, percent

    # ___ ___________________ HIGHLIGHT TABLE STUFF _________________

    @Slot(QTableWidgetItem)
    def on_high_table_itemClicked(self, item):
        """ When an item of the high_table is clicked

        :type item: QTableWidgetItem
        :param item: The item (cell) that is clicked
        """
        row = item.row()
        data = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)

        # needed for edit "Comments" or "Find in Books" in Highlight View
        for row in range(self.file_table.rowCount()):  # 2check: need to optimize?
            if data["path"] == self.file_table.item(row, TYPE).data(Qt.UserRole)[0]:
                self.parent_book_data = self.file_table.item(row, TITLE).data(Qt.UserRole)
                break

    @Slot(QModelIndex)
    def on_high_table_doubleClicked(self, index):
        """ When an item of the high_table is double-clicked

        :type index: QTableWidgetItem
        :param index: The item (cell) that is clicked
        """
        column = index.column()
        if column == COMMENT_H:
            self.on_edit_comment()

    @Slot(QPoint)
    def on_high_table_customContextMenuRequested(self, point):
        """ When an item of the high_table is right-clicked

        :type point: QPoint
        :param point: The point where the right-click happened
        """
        if not len(self.sel_high_view):  # no items selected
            return

        menu = QMenu(self.high_table)

        row = self.high_table.itemAt(point).row()
        self.act_view_book.setData(row)
        self.act_view_book.setEnabled(self.toolbar.open_btn.isEnabled())
        menu.addAction(self.act_view_book)

        highlights = ""
        comments = ""
        for idx in self.sel_high_view:
            item_row = idx.row()
            data = self.high_table.item(item_row, HIGHLIGHT_H).data(Qt.UserRole)
            highlight = data["text"]
            if highlight:
                highlights += highlight + "\n\n"
            comment = data["comment"]
            if comment:
                comments += comment + "\n\n"

        highlights = highlights.rstrip("\n").replace("\n", os.linesep)
        comments = comments.rstrip("\n").replace("\n", os.linesep)

        high_text = _("Copy Highlights")
        com_text = _("Copy Comments")
        if len(self.sel_high_view) == 1:  # single selection
            high_text = _("Copy Highlight")
            com_text = _("Copy Comment")

            text = _("Find in Archive") if self.db_view else _("Find in Books")
            action = QAction(text, menu)
            action.triggered.connect(partial(self.find_in_books, highlights))
            action.setIcon(self.ico_view_books)
            menu.addAction(action)

            action = QAction(_("Comments"), menu)
            action.triggered.connect(self.on_edit_comment)
            action.setIcon(self.ico_file_edit)
            menu.addAction(action)

        action = QAction(high_text, menu)
        action.triggered.connect(partial(self.copy_text_2clip, highlights))
        action.setIcon(self.ico_copy)
        menu.addAction(action)

        action = QAction(com_text, menu)
        action.triggered.connect(partial(self.copy_text_2clip, comments))
        action.setIcon(self.ico_copy)
        menu.addAction(action)

        action = QAction(_("Save to text file"), menu)
        action.triggered.connect(self.on_save_actions)
        action.setData(2)
        action.setIcon(self.ico_file_save)
        menu.addAction(action)

        menu.exec_(self.high_table.mapToGlobal(point))

    def scan_highlights_thread(self):
        """ Gets all the loaded highlights
        """
        self.high_table.model().removeRows(0, self.high_table.rowCount())

        self.status.animation("start")
        self.auto_info.set_text(_("Creating Highlights table.\n"
                                  "Please Wait..."))
        self.auto_info.show()

        scan_thread = QThread()
        scanner = HighlightScanner()
        scanner.moveToThread(scan_thread)
        scanner.found.connect(self.create_highlight_row)
        scanner.finished.connect(self.scan_highlights_finished)
        scanner.finished.connect(scan_thread.quit)
        scan_thread.scanner = scanner
        scan_thread.started.connect(scanner.process)
        scan_thread.start(QThread.IdlePriority)
        self.threads.append(scan_thread)

    def scan_highlights_finished(self):
        """ What will happen after the scanning for history files ends
        """
        self.auto_info.hide()
        self.status.animation("stop")
        for col in [PAGE_H, DATE_H, AUTHOR_H, TITLE_H, PATH_H]:
            self.high_table.resizeColumnToContents(col)
        self.toolbar.activate_buttons()
        self.reload_highlights = False

        self.high_table.setSortingEnabled(True)  # re-enable, after populating table
        order = Qt.AscendingOrder if self.col_sort_asc_h else Qt.DescendingOrder
        self.high_table.sortByColumn(self.col_sort_h, order)

    def create_highlight_row(self, data):
        """ Creates a highlight table row from the given data

        :type data: dict
        :param data: The highlight data
        """
        self.high_table.setSortingEnabled(False)
        self.high_table.insertRow(0)

        text = data["text"]
        item = QTableWidgetItem(text)
        item.setToolTip("<p>{}</p>".format(text))
        item.setData(Qt.UserRole, data)
        self.high_table.setItem(0, HIGHLIGHT_H, item)

        comment = data["comment"]
        item = QTableWidgetItem(comment)
        if comment:
            item.setToolTip("<p>{}</p>".format(comment))
        self.high_table.setItem(0, COMMENT_H, item)

        date = data["date"]
        item = QTableWidgetItem(date)
        item.setToolTip(date)
        item.setTextAlignment(Qt.AlignRight)
        self.high_table.setItem(0, DATE_H, item)

        title = data["title"]
        item = QTableWidgetItem(title)
        item.setToolTip(title)
        self.high_table.setItem(0, TITLE_H, item)

        page = data["page"]
        item = XTableWidgetItem(page)
        item.setToolTip(page)
        item.setTextAlignment(Qt.AlignRight)
        item.setData(Qt.UserRole, int(page))
        self.high_table.setItem(0, PAGE_H, item)

        authors = data["authors"]
        item = QTableWidgetItem(authors)
        item.setToolTip(authors)
        self.high_table.setItem(0, AUTHOR_H, item)

        path = data["path"]
        item = QTableWidgetItem(path)
        item.setToolTip(path)
        self.high_table.setItem(0, PATH_H, item)

        self.high_table.setSortingEnabled(True)

    # noinspection PyUnusedLocal
    def high_view_selection_update(self, selected, deselected):
        """ When a row in high_table gets selected

        :type selected: QModelIndex
        :parameter selected: The selected row
        :type deselected: QModelIndex
        :parameter deselected: The deselected row
        """
        try:
            self.sel_high_view = self.high_view_selection.selectedRows()
        except IndexError:  # empty table
            self.sel_high_view = []
        self.toolbar.activate_buttons()

    def on_highlight_column_clicked(self, column):
        """ Sets the current sorting column

        :type column: int
        :parameter column: The column where the filtering is applied
        """
        if column == self.col_sort_h:
            self.col_sort_asc_h = not self.col_sort_asc_h
        else:
            self.col_sort_asc_h = True
        self.col_sort_h = column

    # noinspection PyUnusedLocal
    def on_highlight_column_resized(self, column, oldSize, newSize):
        """ Gets the column size

        :type column: int
        :parameter column: The resized column
        :type oldSize: int
        :parameter oldSize: The old size
        :type newSize: int
        :parameter newSize: The new size
        """
        if column == HIGHLIGHT_H:
            self.highlight_width = newSize
        elif column == COMMENT_H:
            self.comment_width = newSize

    def find_in_books(self, highlight):
        """ Finds the current highlight in the "Books View"

        :type highlight: str|unicode
        :parameter highlight: The highlight we searching for
        """
        data = self.parent_book_data

        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, TITLE)
            row_data = item.data(Qt.UserRole)
            try:  # find the book row
                if data["stats"]["title"] == row_data["stats"]["title"]:
                    self.on_file_table_itemClicked(item)
                    if not self.db_view:
                        self.toolbar.books_btn.click()
                    else:
                        self.toolbar.db_btn.click()
                    self.file_table.selectRow(row)  # select the book
                    for high_row in range(self.high_list.count()):  # find the highlight
                        if (self.high_list.item(high_row)
                                .data(Qt.UserRole)[HIGHLIGHT_TEXT] == highlight):
                            self.high_list.setCurrentRow(high_row)  # select the highlight
                            return
            except KeyError:  # old metadata with no "stats"
                continue

    # ___ ___________________ HIGHLIGHTS LIST STUFF _________________

    def populate_high_list(self, data):
        """ Populates the Highlights list of `Book` view

        :type data: dict
        :param data: The item's data
        """
        highlights = []
        space = (" " if self.status.act_page.isChecked() and
                 self.status.act_date.isChecked() else "")
        line_break = (":\n" if self.status.act_page.isChecked() or
                      self.status.act_date.isChecked() else "")
        for page in data["highlight"]:
            for page_id in data["highlight"][page]:
                try:
                    date = data["highlight"][page][page_id]["datetime"]
                    text4check = data["highlight"][page][page_id]["text"]
                    text = text4check.replace("\\\n", "\n")
                    comment = ""
                    for idx in data["bookmarks"]:
                        if text4check == data["bookmarks"][idx]["notes"]:
                            bkm_text = data["bookmarks"][idx].get("text", "")
                            if not bkm_text:
                                break
                            bkm_text = re.sub(r"Page \d+ "
                                              r"(.+?) @ \d+-\d+-\d+ \d+:\d+:\d+", r"\1",
                                              bkm_text, 1, re.DOTALL | re.MULTILINE)

                            if text4check != bkm_text:
                                comment = bkm_text.replace("\\\n", "\n")
                            break
                except KeyError:  # blank highlight
                    continue
                highlights.append((page, text, date, page_id, comment))
        for item in sorted(highlights, key=self.sort_high4view):
            page, text, date, page_id, comment = item
            page_text = "Page " + str(page) if self.status.act_page.isChecked() else ""
            date_text = "[" + date + "]" if self.status.act_date.isChecked() else ""
            high_text = text if self.status.act_text.isChecked() else ""
            line_break2 = "\n" if self.status.act_text.isChecked() and comment else ""
            high_comment = line_break2 + "● " + comment if line_break2 else ""
            highlight = (page_text + space + date_text + line_break +
                         high_text + high_comment + "\n")

            highlight_item = QListWidgetItem(highlight, self.high_list)
            highlight_item.setData(Qt.UserRole, item)

    @Slot(QPoint)
    def on_high_list_customContextMenuRequested(self, point):
        """ When a highlight is right-clicked

        :type point: QPoint
        :param point: The point where the right-click happened
        """
        if self.sel_high_list:
            menu = QMenu(self.high_list)

            action = QAction(_("Comments"), menu)
            action.triggered.connect(self.on_edit_comment)
            action.setIcon(self.ico_file_edit)
            menu.addAction(action)

            action = QAction(_("Copy"), menu)
            action.triggered.connect(self.on_copy_highlights)
            action.setIcon(self.ico_copy)
            menu.addAction(action)

            action = QAction(_("Delete"), menu)
            action.triggered.connect(self.on_delete_highlights)
            action.setIcon(self.ico_delete)
            menu.addAction(action)

            menu.exec_(self.high_list.mapToGlobal(point))

    @Slot()
    def on_high_list_itemDoubleClicked(self):
        """ An item on the Highlight List is double-clicked
        """
        self.on_edit_comment()

    def on_edit_comment(self):
        """ Opens a window to edit the selected highlight's comment
        """
        if self.file_table.isVisible():  # edit comments from Book View
            row = self.sel_high_list[-1].row()
            comment = self.high_list.item(row).data(Qt.UserRole)[COMMENT]
        elif self.high_table.isVisible():  # edit comments from Highlights View
            row = self.sel_high_view[-1].row()
            high_data = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
            comment = high_data["comment"]
        else:
            return
        self.edit_high.high_edit_txt.setText(comment)
        # self.edit_high.high_edit_txt.setFocus()
        self.edit_high.exec_()

    def edit_comment_ok(self):
        """ Change the selected highlight's comment
        """
        text = self.edit_high.high_edit_txt.toPlainText()
        if self.file_table.isVisible():
            high_index = self.sel_high_list[-1]
            high_row = high_index.row()
            high_data = self.high_list.item(high_row).data(Qt.UserRole)
            high_text = high_data[HIGHLIGHT_TEXT].replace("\n", "\\\n")

            row = self.sel_idx.row()
            item = self.file_table.item
            data = item(row, TITLE).data(Qt.UserRole)

            for bookmark in data["bookmarks"].keys():
                if high_text == data["bookmarks"][bookmark]["notes"]:
                    data["bookmarks"][bookmark]["text"] = text.replace("\n", "\\\n")
                    break
            item(row, TITLE).setData(Qt.UserRole, data)

            if not self.db_view:  # Books view
                path = item(row, PATH).text()
                self.save_book_data(path, data)
            else:  # Archive view
                self.update_book2db(data)
                self.on_file_table_itemClicked(item(row, 0), reset=False)
        elif self.high_table.isVisible():
            data = self.parent_book_data
            row = self.sel_high_view[-1].row()
            high_data = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
            high_text = high_data["text"].replace("\n", "\\\n")

            for bookmark in data["bookmarks"].keys():
                if high_text == data["bookmarks"][bookmark]["notes"]:
                    data["bookmarks"][bookmark]["text"] = text.replace("\n", "\\\n")
                    high_data["comment"] = text
                    break
            self.high_table.item(row, HIGHLIGHT_H).setData(Qt.UserRole, high_data)
            self.high_table.item(row, COMMENT_H).setText(text)
            book_path, ext = splitext(high_data["path"])
            path = join(book_path + ".sdr", "metadata{}.lua".format(ext))
            self.save_book_data(path, data)
        self.reload_highlights = True

    def on_copy_highlights(self):
        """ Copy the selected highlights to clipboard
        """
        clipboard_text = ""
        for highlight in sorted(self.sel_high_list):
            row = highlight.row()
            text = self.high_list.item(row).text()
            clipboard_text += text + "\n"
        self.copy_text_2clip(clipboard_text)

    def on_delete_highlights(self):
        """ The delete highlights action was invoked
        """
        if not self.db_view:
            if self.edit_lua_file_warning:
                text = _("This is an one-time warning!\n\nIn order to delete highlights "
                         "from a book, its \"metadata\" file must be edited. This "
                         "contains a small risk of corrupting that file and lose all the "
                         "settings and info of that book.\n\nDo you still want to do it?")
                popup = self.popup(_("Warning!"), text, buttons=3)
                if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
                    return
                else:
                    self.edit_lua_file_warning = False
            text = _("This will delete the selected highlights!\nAre you sure?")
        else:
            text = _("This will remove the selected highlights from the Archive!\n"
                     "Are you sure?")
        popup = self.popup(_("Warning!"), text, buttons=3)
        if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
            return
        self.delete_highlights()

    def delete_highlights(self):
        """ Delete the selected highlights
        """
        row = self.sel_idx.row()
        data = self.file_table.item(row, TITLE).data(Qt.UserRole)

        for highlight in self.sel_high_list:
            high_row = highlight.row()
            page = self.high_list.item(high_row).data(Qt.UserRole)[PAGE]
            page_id = self.high_list.item(high_row).data(Qt.UserRole)[PAGE_ID]
            del data["highlight"][page][page_id]  # delete the highlight

            # delete the associated bookmark
            text = self.high_list.item(high_row).data(Qt.UserRole)[HIGHLIGHT_TEXT]
            for bookmark in data["bookmarks"].keys():
                if text == data["bookmarks"][bookmark]["notes"]:
                    del data["bookmarks"][bookmark]

        for i in data["highlight"].keys():
            if not data["highlight"][i]:  # delete page dicts with no highlights
                del data["highlight"][i]
            else:  # renumbering the highlight keys
                contents = [data["highlight"][i][j] for j in sorted(data["highlight"][i])]
                if contents:
                    for l in data["highlight"][i].keys():  # delete all the items and
                        del data["highlight"][i][l]
                    for k in range(len(contents)):      # rewrite them with the new keys
                        data["highlight"][i][k + 1] = contents[k]

        contents = [data["bookmarks"][bookmark] for bookmark in sorted(data["bookmarks"])]
        if contents:  # renumbering the bookmarks keys
            for bookmark in data["bookmarks"].keys():  # delete all the items and
                del data["bookmarks"][bookmark]
            for content in range(len(contents)):  # rewrite them with the new keys
                data["bookmarks"][content + 1] = contents[content]

        if not data["highlight"]:  # change icon if no highlights
            item = self.file_table.item(row, 0)
            item.setIcon(self.ico_empty)

        if not self.db_view:
            path = self.file_table.item(row, PATH).text()
            self.save_book_data(path, data)
        else:
            self.update_book2db(data)
            item = self.file_table.item
            item(row, TITLE).setData(Qt.UserRole, data)
            self.on_file_table_itemClicked(item(row, 0), reset=False)
        self.reload_highlights = True

    def save_book_data(self, path, data):
        """ Saves the data of a book to its lua file

        :type path: str|unicode
        :param path: The path to the book's data file
        :type data: dict
        :param data: The book's data
        """
        times = os.stat(path)  # read the file's created/modified times
        encode_data(path, data)
        os.utime(path, (times.st_ctime, times.st_mtime))  # reapply original times
        if self.file_table.isVisible():
            self.on_file_table_itemClicked(self.file_table.item(self.sel_idx.row(), 0),
                                           reset=False)

    # noinspection PyUnusedLocal
    def high_list_selection_update(self, selected, deselected):
        """ When a highlight in gets selected

        :type selected: QModelIndex
        :parameter selected: The selected highlight
        :type deselected: QModelIndex
        :parameter deselected: The deselected highlight
        """
        self.sel_high_list = self.high_list_selection.selectedRows()

    def set_highlight_sort(self):
        """ Sets the sorting method of displayed highlights
        """
        self.high_by_page = self.sender().data()
        try:
            row = self.sel_idx.row()
            self.on_file_table_itemClicked(self.file_table.item(row, 0), False)
        except AttributeError:  # no book selected
            pass

    def sort_high4view(self, data):
        """ Sets the sorting method of displayed highlights

        :type data: tuple
        param: data: The highlight's data
        """
        return int(data[PAGE]) if self.high_by_page else data[DATE]

    def sort_high4write(self, data):
        """ Sets the sorting method of written highlights

        :type data: tuple
        param: data: The highlight's data
        """
        return int(data[3][5:]) if self.high_by_page else data[0]

    # ___ ___________________ MERGING - SYNCING STUFF _______________

    def check4merge(self):
        """ Check if the selected books' highlights can be merged
        """
        if len(self.sel_indexes) == 2:
            data = [self.file_table.item(idx.row(), idx.column()).data(Qt.UserRole)
                    for idx in self.sel_indexes]
            try:
                if data[0]["partial_md5_checksum"] == data[1]["partial_md5_checksum"]:
                    return True
            except KeyError:  # no "partial_md5_checksum" key (older metadata)
                pass
        return False

    def merge_menu(self):
        """ Creates the `Merge/Sync` button menu
        """
        menu = QMenu(self)

        action = QAction(self.ico_files_merge, _("Merge highlights"), menu)
        action.triggered.connect(self.toolbar.on_merge_btn_clicked)
        menu.addAction(action)

        action = QAction(self.ico_files_merge, _("Sync position only"), menu)
        action.triggered.connect(partial(self.merge_highlights, True, False))
        menu.addAction(action)

        return menu

    def merge_highlights(self, sync, merge=True):
        """ Merge highlights from the same book in two different devices

        :type sync: bool
        :param sync: Sync reading position too
        :type merge: bool
        :param merge: Merge the highlights
        """
        idx1, idx2 = self.sel_indexes
        data1, data2 = [self.file_table.item(idx.row(), TITLE).data(Qt.UserRole)
                        for idx in [idx1, idx2]]
        path1, path2 = [self.file_table.item(idx.row(), PATH).text()
                        for idx in [idx1, idx2]]

        if merge:  # merge highlights
            args = (data1["highlight"], data2["highlight"],
                    data1["bookmarks"], data2["bookmarks"])
            high1, high2, bkm1, bkm2 = self.get_unique_highlights(*args)
            self.update_data(data1, high2, bkm2)
            self.update_data(data2, high1, bkm1)

        if sync:  # sync position and percent
            if data1["percent_finished"] > data2["percent_finished"]:
                data2["percent_finished"] = data1["percent_finished"]
                data2["last_xpointer"] = data1["last_xpointer"]
                percent = self.file_table.item(idx1.row(), PERCENT).text()
                self.file_table.item(idx2.row(), PERCENT).setText(percent)
                self.file_table.item(idx2.row(), PERCENT).setToolTip(percent)
            else:
                data1["percent_finished"] = data2["percent_finished"]
                data1["last_xpointer"] = data2["last_xpointer"]
                percent = self.file_table.item(idx2.row(), PERCENT).text()
                self.file_table.item(idx1.row(), PERCENT).setText(percent)
                self.file_table.item(idx1.row(), PERCENT).setToolTip(percent)

        self.file_table.item(idx1.row(), TITLE).setData(Qt.UserRole, data1)
        self.file_table.item(idx2.row(), TITLE).setData(Qt.UserRole, data2)

        self.save_book_data(path1, data1)
        self.save_book_data(path2, data2)
        self.reload_highlights = True

    @staticmethod
    def get_unique_highlights(high1, high2, bkm1, bkm2):
        """ Get the highlights, bookmarks from the first book
        that do not exist in the second book and vice versa

        :type high1: dict
        :param high1: The first book's highlights
        :type high2: dict
        :param high2: The second book's highlights
        :type bkm1: dict
        :param bkm1: The first book's bookmarks
        :type bkm2: dict
        :param bkm2: The second book's bookmarks
        """
        unique_high1 = defaultdict(dict)
        for page1 in high1:
            for page_id1 in high1[page1]:
                text1 = high1[page1][page_id1]["text"]
                for page2 in high2:
                    for page_id2 in high2[page2]:
                        if text1 == high2[page2][page_id2]["text"]:
                            break  # highlight found in book2
                    else:  # highlight was not found yet in book2
                        continue  # no break in the inner loop, keep looping
                    break  # highlight already exists in book2 (there was a break)
                else:  # text not in book2 highlights, add to unique
                    unique_high1[page1][page_id1] = high1[page1][page_id1]
        unique_bkm1 = {}
        for page1 in unique_high1:
            for page_id1 in unique_high1[page1]:
                text1 = unique_high1[page1][page_id1]["text"]
                for idx in bkm1:
                    if text1 == bkm1[idx]["notes"]:  # add highlight's bookmark to unique
                        unique_bkm1[idx] = bkm1[idx]
                        break

        unique_high2 = defaultdict(dict)
        for page2 in high2:
            for page_id2 in high2[page2]:
                text2 = high2[page2][page_id2]["text"]
                for page1 in high1:
                    for page_id1 in high1[page1]:
                        if text2 == high1[page1][page_id1]["text"]:
                            break  # highlight found in book1
                    else:  # highlight was not found yet in book1
                        continue  # no break in the inner loop, keep looping
                    break  # highlight already exists in book1 (there was a break)
                else:  # text not in book1 highlights, add to unique
                    unique_high2[page2][page_id2] = high2[page2][page_id2]
        unique_bkm2 = {}
        for page2 in unique_high2:
            for page_id2 in unique_high2[page2]:
                text2 = unique_high2[page2][page_id2]["text"]
                for idx in bkm2:
                    if text2 == bkm2[idx]["notes"]:  # add highlight's bookmark to unique
                        unique_bkm2[idx] = bkm2[idx]
                        break

        return unique_high1, unique_high2, unique_bkm1, unique_bkm2

    @staticmethod
    def update_data(data, extra_highlights, extra_bookmarks):
        """ Adds the new highlights to the book's data

        :type data: dict
        :param data: The book's data
        :type extra_highlights: dict
        :param extra_highlights: The other book's highlights
        :type extra_bookmarks: dict
        :param extra_bookmarks: The other book's bookmarks
        """
        highlights = data["highlight"]
        for page in extra_highlights:
            if page in highlights:  # change page number if already exists
                new_page = page
                while new_page in highlights:
                    new_page += 1
                highlights[new_page] = extra_highlights[page]
            else:
                highlights[page] = extra_highlights[page]

        bookmarks = data["bookmarks"]
        original = bookmarks.copy()
        bookmarks.clear()
        counter = 1
        for key in original.keys():
            bookmarks[counter] = original[key]
            counter += 1
        for key in extra_bookmarks.keys():
            bookmarks[counter] = extra_bookmarks[key]
            counter += 1

    # ___ ___________________ DELETING STUFF ________________________

    def delete_menu(self):
        """ Creates the `Delete` button menu
        """
        menu = QMenu(self)
        for idx, title in enumerate([_("Selected books' info"),
                                     _("Selected books"),
                                     _("All missing books' info")]):
            action = QAction(self.ico_files_delete, title, menu)
            action.triggered.connect(self.on_delete_actions)
            action.setData(idx)
            menu.addAction(action)
        return menu

    def on_delete_actions(self):
        """ When a `Delete action` is selected
        """
        idx = self.sender().data()
        self.delete_actions(idx)

    def delete_actions(self, idx):
        """ Execute the selected `Delete action`

        :type idx: int
        :param idx: The action type
        """
        if not self.db_view:  # Books view
            if not self.sel_indexes and idx in [0, 1]:
                return
            text = ""
            if idx == 0:
                text = _("This will delete the selected books' information\n"
                         "but will keep the equivalent books.")
            elif idx == 1:
                text = _("This will delete the selected books and their information.")
            elif idx == 2:
                text = _("This will delete all the books' information "
                         "that refers to missing books.")
            popup = self.popup(_("Warning!"), text, buttons=2)
            if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
                return

            if idx == 0:  # delete selected books' info
                self.remove_sel_books()
            elif idx == 1:  # delete selected books
                self.remove_sel_books(delete=True)
            elif idx == 2:  # delete all missing books info
                self.clear_missing_info()
        else:  # Archive view
            text = _("Delete the selected books from the Archive?")
            popup = self.popup(_("Warning!"), text, buttons=2, icon=QMessageBox.Question)
            if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
                return
            ids = []
            for idx in sorted(self.sel_indexes, reverse=True):
                data = self.file_table.item(idx.row(), TITLE).data(Qt.UserRole)
                ids.append(data["partial_md5_checksum"])
                self.file_table.removeRow(idx.row())
            self.delete_books_from_db(ids)
            self.file_table.clearSelection()
        self.reload_highlights = True

    def remove_sel_books(self, delete=False):
        """ Remove the selected book entries from the file_table

        :type delete: bool
        :param delete: Delete the book file too
        """
        for index in sorted(self.sel_indexes)[::-1]:
            row = index.row()
            path = self.get_sdr_folder(row)
            shutil.rmtree(path) if isdir(path) else os.remove(path)
            if delete:  # delete the book file too
                try:
                    book_path = self.file_table.item(row, TYPE).data(Qt.UserRole)[0]
                    os.remove(book_path) if isfile(book_path) else None
                    self.remove_book_row(row)
                except AttributeError:  # empty entry
                    pass
            self.remove_book_row(row)  # remove file_table entry

    def clear_missing_info(self):
        """ Delete the book info of all entries that have no book file
        """
        for row in range(self.file_table.rowCount())[::-1]:
            try:
                book_exists = self.file_table.item(row, TYPE).data(Qt.UserRole)[1]
            except AttributeError:  # empty entry
                continue
            if not book_exists:
                path = self.get_sdr_folder(row)
                shutil.rmtree(path) if isdir(path) else os.remove(path)
                self.remove_book_row(row)

    def remove_book_row(self, row):
        """ Remove a book entry from the file table

        :type row: int
        :param row: The entry's row
        """
        self.loaded_paths.remove(self.file_table.item(row, PATH).data(0))
        self.file_table.removeRow(row)

    def get_sdr_folder(self, row):
        """ Get the .sdr folder path for a book entry

        :type row: int
        :param row: The entry's row
        """
        path = split(self.file_table.item(row, PATH).data(0))[0]
        if not path.lower().endswith(".sdr"):
            path = self.file_table.item(row, PATH).data(0)
        return path

    # ___ ___________________ SAVING STUFF __________________________

    def save_menu(self):
        """ Creates the `Save Files` button menu
        """
        menu = QMenu(self)
        for idx, item in enumerate([_("To individual text files"),
                                    _("Combined to one text file"),
                                    _("To individual html files"),
                                    _("Combined to one html file")
                                    ]):
            action = QAction(item, menu)
            action.triggered.connect(self.on_save_actions)
            action.setData(idx)
            action.setIcon(self.ico_file_save)
            menu.addAction(action)
        return menu

    def on_save_actions(self):
        """ A `Save selected...` menu item is clicked
        """
        idx = self.sender().data()
        self.save_actions(idx)

    # noinspection PyCallByClass
    def save_actions(self, idx):
        """ Execute the selected `Save action`

        :type idx: int
        :param idx: The action type
        """
        saved = 0
        if not self.sel_indexes:
            return

        if idx in [MANY_TEXT, MANY_HTML]:  # Save from file_table to different files
            text = _("Select destination folder for the saved file(s)")
            dir_path = QFileDialog.getExistingDirectory(self, text, self.last_dir,
                                                        QFileDialog.ShowDirsOnly)
            if not dir_path:
                return
            self.last_dir = dir_path
            saved = self.save_multi_files(dir_path, idx == MANY_HTML)
        elif idx in [ONE_TEXT, ONE_HTML]:  # Save from file_table, combine to one file
            html = idx == ONE_HTML
            ext = " (*.html)" if html else " (*.txt)"
            title = _("Save to HTML file") if html else _("Save to Text file")
            filename = QFileDialog.getSaveFileName(self, title, self.last_dir,
                                                   _("Text files") + ext)[0]
            if not filename:
                return
            self.last_dir = dirname(filename)
            saved = self.save_merged_file(filename, html=html)
        elif idx == MERGED_HIGH:  # Save from high_table, combine to one file
            return self.save_sel_highlights()  # exit without info popup

        self.status.animation("stop")
        all_files = len(self.file_table.selectionModel().selectedRows())
        self.popup(_("Finished!"), _("{} texts were saved from the {} processed.\n"
                                     "{} files with no highlights.")
                   .format(saved, all_files, all_files - saved),
                   icon=QMessageBox.Information)

    def save_multi_files(self, dir_path, html):
        """ Save each selected book's highlights to a different file

        :type dir_path: str|unicode
        :param dir_path: The directory where the files will be saved
        :type html: bool
        :param html: The output is html
        """
        self.status.animation("start")
        saved = 0
        title_counter = 0
        space = (" " if self.status.act_page.isChecked() and
                 self.status.act_date.isChecked() else "")
        line_break = (":" + os.linesep if self.status.act_page.isChecked() or
                      self.status.act_date.isChecked() else "")
        for idx in self.sel_indexes:
            row = idx.row()
            data = self.file_table.item(row, 0).data(Qt.UserRole)
            highlights = []
            for page in data["highlight"]:
                for page_id in data["highlight"][page]:
                    highlights.append(self.analyze_high(data, page, page_id, html))
            if not highlights:  # no highlights
                continue
            title = self.file_table.item(row, 0).data(0)
            if title == _("NO TITLE FOUND"):
                title += str(title_counter)
                title_counter += 1
            authors = self.file_table.item(row, 1).data(0)
            if authors in ["OLD TYPE FILE", "NO AUTHOR FOUND"]:
                authors = ""
            name = title
            if authors:
                name = "{} - {}".format(authors, title)
            if not html:
                ext = ".txt"
                text = ""
            else:
                ext = ".html"
                text = HTML_HEAD + BOOK_BLOCK % {"title": title, "authors": authors}
            filename = join(dir_path, sanitize_filename(name) + ext)
            with io.open(filename, "w+", encoding="utf-8", newline="") as text_file:
                for highlight in sorted(highlights, key=self.sort_high4write):
                    date_text, high_comment, high_text, page_text = highlight
                    if not html:
                        text += (page_text + space + date_text + line_break +
                                 high_text + high_comment)
                        text += 2 * os.linesep
                    else:
                        text += HIGH_BLOCK % {"page": page_text, "date": date_text,
                                              "highlight": high_text,
                                              "comment": high_comment}
                if html:
                    text += "\n</div>\n</body>\n</html>"

                text_file.write(text)
                saved += 1
        return saved

    def save_merged_file(self, filename, html):
        """ Save the selected book's highlights to a single html file

        :type filename: str|unicode
        :param filename: The name of the html file with the highlights
        :type html: bool
        :param html: The output is html
        """
        self.status.animation("start")
        saved = 0
        title_counter = 0
        space = (" " if self.status.act_page.isChecked() and
                 self.status.act_date.isChecked() else "")
        line_break = (":" + os.linesep if self.status.act_page.isChecked() or
                      self.status.act_date.isChecked() else "")
        text = HTML_HEAD if html else ""
        for i in sorted(self.sel_indexes):
            row = i.row()
            data = self.file_table.item(row, 0).data(Qt.UserRole)

            title = self.file_table.item(row, 0).data(0)
            if title == _("NO TITLE FOUND"):
                title += str(title_counter)
                title_counter += 1
            authors = self.file_table.item(row, 1).data(0)
            if authors in ["OLD TYPE FILE", "NO AUTHOR FOUND"]:
                authors = ""

            highlights = []
            for page in data["highlight"]:
                for page_id in data["highlight"][page]:
                    highlights.append(self.analyze_high(data, page, page_id, html=html))
            if not highlights:  # no highlights
                continue

            if html:
                text += BOOK_BLOCK % {"title": title, "authors": authors}
                for high in sorted(highlights, key=self.sort_high4write):
                    date_text, high_comment, high_text, page_text = high
                    text += HIGH_BLOCK % {"page": page_text, "date": date_text,
                                          "highlight": high_text, "comment": high_comment}
                text += "</div>\n"
            else:
                name = title
                if authors:
                    name = "{} - {}".format(authors, title)
                line = "-" * 80
                text += line + os.linesep + name + os.linesep + line + os.linesep
                highlights = [i[3] + space + i[0] + line_break + i[2] + i[1] for i in
                              sorted(highlights, key=self.sort_high4write)]

                text += (os.linesep * 2).join(highlights) + os.linesep * 2
            saved += 1
        text += "\n</body>\n</html>" if html else ""

        with io.open(filename, "w+", encoding="utf-8", newline="") as text_file:
            text_file.write(text)
        return saved

    def save_sel_highlights(self):
        """ Save the selected highlights to a text file (from high_table)
        """
        if not self.sel_high_view:
            return
        # noinspection PyCallByClass
        filename = QFileDialog.getSaveFileName(self, "Save to Text file", self.last_dir,
                                               "text files (*.txt);;"
                                               "all files (*.*)")[0]
        if filename:
            self.last_dir = dirname(filename)
        else:
            return
        text = ""
        for i in sorted(self.sel_high_view):
            row = i.row()
            data = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
            comment = "\n● " + data["comment"] if data["comment"] else ""
            txt = ("{} [{}]\nPage {} [{}]\n{}{}".format(data["title"], data["authors"],
                                                        data["page"], data["date"],
                                                        data["text"], comment))
            text += txt + "\n\n"
        with io.open(filename, "w+", encoding="utf-8", newline="") as text_file:
            text_file.write(text.replace("\n", os.linesep))

    def analyze_high(self, data, page, page_id, html):
        """ Get the highlight's info (text, comment, date and page)

        :type data: dict
        :param data: The highlight's data
        :type page: int
        :param page The page where the highlight starts
        :type page_id: int
        :param page_id The count of this page's highlight
        :type html: bool
        :param html The output is for html
        """
        date = data["highlight"][page][page_id]["datetime"]
        high_text = data["highlight"][page][page_id]["text"]
        pos_0 = data["highlight"][page][page_id]["pos0"]
        pos_1 = data["highlight"][page][page_id]["pos1"]
        comment = ""
        for bookmark_idx in data["bookmarks"]:
            try:
                book_pos0 = data["bookmarks"][bookmark_idx]["pos0"]
            except KeyError:  # no [bookmark_idx]["pos0"] exists (blank highlight)
                continue
            book_pos1 = data["bookmarks"][bookmark_idx]["pos1"]
            if (pos_0 == book_pos0) and (pos_1 == book_pos1):
                book_text = data["bookmarks"][bookmark_idx].get("text", "")
                if not book_text:
                    break
                book_text = re.sub(r"Page \d+ (.+?) @ \d+-\d+-\d+ \d+:\d+:\d+",
                                   r"\1", book_text, 1, re.DOTALL | re.MULTILINE)
                if high_text != book_text:
                    comment = book_text
                break
        page_text = "Page " + str(page) if self.status.act_page.isChecked() else ""
        date_text = "[" + date + "]" if self.status.act_date.isChecked() else ""
        linesep = "<br/>" if html else os.linesep
        high_text = (high_text.replace("\\\n", linesep)
                     if self.status.act_text.isChecked() else "")
        comment = comment.replace("\\\n", linesep)
        line_break2 = (os.linesep if self.status.act_text.isChecked() and comment else "")
        high_comment = (line_break2 + "● " + comment
                        if self.status.act_comment.isChecked() and comment else "")
        return date_text, high_comment, high_text, page_text

    # ___ ___________________ SETTINGS STUFF ________________________

    def settings_load(self):
        """ Loads the jason based configuration settings
        """
        if app_config:
            self.restoreGeometry(self.unpickle("geometry"))
            self.restoreState(self.unpickle("state"))
            self.splitter.restoreState(self.unpickle("splitter"))
            self.about.restoreGeometry(self.unpickle("about_geometry"))
            self.col_sort = app_config.get("col_sort", MODIFIED)
            self.col_sort_asc = app_config.get("col_sort_asc", False)
            self.col_sort_h = app_config.get("col_sort_h", DATE_H)
            self.col_sort_asc_h = app_config.get("col_sort_asc_h", False)
            self.highlight_width = app_config.get("highlight_width", None)
            self.comment_width = app_config.get("comment_width", None)
            self.last_dir = app_config.get("last_dir", os.getcwd())
            self.current_view = app_config.get("current_view", 0)
            self.fold_btn.setChecked(app_config.get("show_info", True))
            self.opened_times = app_config.get("opened_times", 0)
            self.toolbar_size = app_config.get("toolbar_size", 48)
            self.skip_version = app_config.get("skip_version", None)
            self.date_vacuumed = app_config.get("date_vacuumed", self.date_vacuumed)
            self.exit_msg = app_config.get("exit_msg", True)
            self.high_merge_warning = app_config.get("high_merge_warning", True)
            self.edit_lua_file_warning = app_config.get("edit_lua_file_warning", True)

            if len(sys.argv) > 1:  # command arguments exist, open in Book view
                self.current_view = 0
            self.toolbar.view_frame.children()[self.current_view + 1].click()

            checked = app_config.get("show_items", (True, True, True, True))
            # noinspection PyTypeChecker
            checked = checked if len(checked) == 4 else checked + [True]  # 4compatibility
            self.status.act_page.setChecked(checked[0])
            self.status.act_date.setChecked(checked[1])
            self.status.act_text.setChecked(checked[2])
            self.status.act_comment.setChecked(checked[3])
            self.high_by_page = app_config.get("high_by_page", False)
        else:
            self.resize(800, 600)
        if self.highlight_width:
            self.header_high_view.resizeSection(HIGHLIGHT_H, self.highlight_width)
        if self.comment_width:
            self.header_high_view.resizeSection(COMMENT_H, self.comment_width)
        self.toolbar.set_btn_size(self.toolbar_size)

    def settings_save(self):
        """ Saves the jason based configuration settings
        """
        config = {"geometry": self.pickle(self.saveGeometry()),
                  "state": self.pickle(self.saveState()),
                  "splitter": self.pickle(self.splitter.saveState()),
                  "about_geometry": self.pickle(self.about.saveGeometry()),
                  "col_sort_asc": self.col_sort_asc, "col_sort": self.col_sort,
                  "col_sort_asc_h": self.col_sort_asc_h, "col_sort_h": self.col_sort_h,
                  "highlight_width": self.highlight_width,
                  "comment_width": self.comment_width, "toolbar_size": self.toolbar_size,
                  "last_dir": self.last_dir, "exit_msg": self.exit_msg,
                  "current_view": self.current_view,
                  "high_by_page": self.high_by_page, "date_vacuumed": self.date_vacuumed,
                  "show_info": self.fold_btn.isChecked(),
                  "show_items": (self.status.act_page.isChecked(),
                                 self.status.act_date.isChecked(),
                                 self.status.act_text.isChecked(),
                                 self.status.act_comment.isChecked()),
                  "skip_version": self.skip_version, "opened_times": self.opened_times,
                  "edit_lua_file_warning": self.edit_lua_file_warning,
                  "high_merge_warning": self.high_merge_warning,
                  }
        try:
            if not PYTHON2:
                # noinspection PyUnresolvedReferences
                for k, v in config.items():
                    if type(v) == bytes:
                        # noinspection PyArgumentList
                        config[k] = str(v, encoding="utf8")
            config_json = json.dumps(config, sort_keys=True, indent=4)
            with gzip.GzipFile(join(SETTINGS_DIR, "settings.json.gz"), "w+") as gz_file:
                try:
                    gz_file.write(config_json)
                except TypeError:  # Python3
                    gz_file.write(config_json.encode("utf8"))
        except IOError as error:
            print("On saving settings:", error)

    @staticmethod
    def pickle(array):
        """ Serialize some binary settings

        :type array: QByteArray
        :param array: The data
        """
        if PYTHON2:
            return pickle.dumps(array)
        # noinspection PyArgumentList
        return str(pickle.dumps(array.data()), encoding="unicode_escape")  # Python3

    @staticmethod
    def unpickle(key):
        """ Un-serialize some binary settings

        :type key: str|unicode
        :param key: The dict key to be un-pickled
        """
        try:
            if PYTHON2:
                try:
                    value = pickle.loads(str(app_config.get(key)))
                except UnicodeEncodeError:  # settings file from Python3
                    return
            else:
                try:
                    # noinspection PyArgumentList
                    pickled = pickle.loads(bytes(app_config.get(key), encoding="latin"))
                    value = QByteArray(pickled)
                except UnicodeDecodeError:  # settings file from Python2
                    return
        except pickle.UnpicklingError as err:
            print("While unPickling:", err)
            return
        return value

    # ___ ___________________ UTILITY STUFF _________________________

    def thread_cleanup(self):
        """ Deletes the finished threads
        """
        for thread in self.threads:
            if thread.isFinished():
                self.threads.remove(thread)

    def popup(self, title, text, icon=QMessageBox.Warning, buttons=1,
              extra_text="", check_text=""):
        """ Creates and returns a Popup dialog

        :type title: str|unicode
        :parameter title: The Popup's title
        :type text: str|unicode
        :parameter text: The Popup's text
        :type icon: int|unicode|QPixmap
        :parameter icon: The Popup's icon
        :type buttons: int
        :parameter buttons: The number of the Popup's buttons
        :type extra_text: str|unicode
        :parameter extra_text: The extra button's text (button is omitted if "")
        :type check_text: str|unicode
        :parameter check_text: The checkbox's text (checkbox is omitted if "")
        """
        popup = XMessageBox(self)
        popup.setWindowIcon(QIcon(":/stuff/icon.png"))
        if type(icon) == QMessageBox.Icon:
            popup.setIcon(icon)
        elif type(icon) == unicode:
            popup.setIconPixmap(QPixmap(icon))
        elif type(icon) == QPixmap:
            popup.setIconPixmap(icon)
        else:
            raise TypeError("Wrong icon type!")
        popup.setWindowTitle(title)
        popup.setText(text + "\n" if check_text else text)
        if buttons == 1:
            popup.addButton(_("Close"), QMessageBox.RejectRole)
        elif buttons == 2:
            popup.addButton(_("OK"), QMessageBox.AcceptRole)
            popup.addButton(_("Cancel"), QMessageBox.RejectRole)
        elif buttons == 3:
            popup.addButton(_("Yes"), QMessageBox.AcceptRole)
            popup.addButton(_("No"), QMessageBox.RejectRole)
        if extra_text:  # add an extra button
            popup.addButton(extra_text, QMessageBox.ApplyRole)
        if check_text:  # hide check_box if no text for it
            popup.check_box.setText(check_text)
        else:
            popup.check_box.hide()
        popup.checked = popup.exec_()[1]

        return popup

    def passed_files(self):
        """ Command line parameters that are passed to the program.
        """
        # args = QApplication.instance().arguments()
        try:
            if sys.argv[1]:
                self.on_file_table_fileDropped(sys.argv[1:])
        except IndexError:
            pass

    def open_file(self, path):
        """ Opens a file with its associated app

        :type path: str|unicode
        :param path: The path to the file to be opened
        """
        if isfile(path):
            if sys.platform == "win32":
                os.startfile(path)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, path])
        else:
            self.popup(_("Error opening file!"), _('"{}" does not exists!').format(path))

    def copy_text_2clip(self, text):
        """ Copy a text to clipboard

        :type text: str|unicode
        """
        if text:
            data = QMimeData()
            data.setText(text)
            self.clip.setMimeData(data)

    @staticmethod
    def get_time_str(sec):
        """ Takes seconds and returns the formatted time value

        :type sec: int
        :param sec: The seconds
        """
        return "{:02}:{:02}:{:02}".format(int(sec / 3600),
                                          int(sec % 3600 / 60),
                                          int(sec % 60))

    def auto_check4update(self):
        """ Checks online for an updated version
        """
        if self.get_db_book_count():  # db has books
            now = datetime.now()
            vacuumed = datetime.strptime(self.date_vacuumed, DATE_FORMAT)
            delta = now - vacuumed
            if delta.days > 90:  # after three months
                self.vacuum_db(info=False)  # compact db
                self.date_vacuumed = now.strftime(DATE_FORMAT)  # reset vacuumed date

        self.opened_times += 1
        if self.opened_times == 20:
            text = _("Since you are using {} for some time now, perhaps you find it "
                     "useful enough to consider a donation.\nWould you like to visit "
                     "the PayPal donation page?\n\nThis is a one-time message. "
                     "It will never appear again!").format(APP_NAME)
            popup = self.popup(_("A reminder..."), text,
                               icon=":/stuff/paypal76.png", buttons=3)

            if popup.buttonRole(popup.clickedButton()) == QMessageBox.AcceptRole:
                webbrowser.open("https://www.paypal.com/cgi-bin/webscr?"
                                "cmd=_s-xclick%20&hosted_button_id=MYV4WLTD6PEVG")
            return
        # noinspection PyBroadException
        try:
            version_new = self.about.get_online_version()
        # except URLError:  # can not connect
        except Exception:
            return
        if not version_new:
            return
        version = LooseVersion(self.version)
        skip_version = LooseVersion(self.skip_version)
        if version_new > version and version_new != skip_version:
            popup = self.popup(_("Newer version exists!"),
                               _("There is a newer version (v.{}) online.\n"
                                 "Open the site to download it now?")
                               .format(version_new),
                               icon=QMessageBox.Information, buttons=2,
                               check_text=_("Don\"t alert me for this version again"))
            if popup.checked:
                self.skip_version = version_new
            if popup.clickedButton().text() == "OK":
                webbrowser.open("http://www.noembryo.com/apps.php?kohighlights")

    def write_to_log(self, text):
        """ Append text to the QTextEdit.
        """
        # self.about.log_txt.appendPlainText(text)

        cursor = self.about.log_txt.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.about.log_txt.setTextCursor(cursor)
        self.about.log_txt.ensureCursorVisible()

        if self.sender().objectName() == "err":
            text = "\033[91m" + text + "\033[0m"

        # noinspection PyBroadException
        try:
            sys.__stdout__.write(text)
        except Exception:  # a problematic print that WE HAVE to ignore or we LOOP
            pass

    @staticmethod
    def delete_logs():
        """ Keeps the number of log texts steady.
        """
        _, _, files = next(os.walk(SETTINGS_DIR))
        files = sorted(i for i in files if i.startswith("error_log"))
        if len(files) > 3:
            for name in files[:-3]:
                try:
                    os.remove(join(SETTINGS_DIR, name))
                except WindowsError:  # the file is locked
                    pass

    def on_check_btn(self):
        pass


class KoHighlights(QApplication):

    def __init__(self, *args, **kwargs):
        super(KoHighlights, self).__init__(*args, **kwargs)

        # decode app's arguments
        try:
            sys.argv = [i.decode(sys.getfilesystemencoding()) for i in sys.argv]
        except AttributeError:  # i.decode does not exists in Python 3
            pass

        self.parser = argparse.ArgumentParser(prog=APP_NAME,
                                              description="{} v{} - A KoReader's "
                                                          "highlights converter"
                                              .format(APP_NAME, __version__),
                                              epilog="Thanks for using %s!" % APP_NAME)
        self.parser.add_argument("-v", "--version", action="version",
                                 version="%(prog)s v{}".format(__version__))

        if getattr(sys, 'frozen', False):
            if not sys.platform.lower().startswith("win"):
                self.parse_args()
        else:
            self.parse_args()

        # # hide console window, but only under Windows and only if app is frozen
        # on_windows = sys.platform.lower().startswith("win")
        # compiled = getattr(sys, 'frozen', False)
        # if on_windows and compiled:
        #     hide_console()
        #     self.parse_args()
        # else:
        #     self.parse_args()

        self.base = Base()
        self.exec_()

        # show_console() if on_windows and compiled else None

    # ___ ___________________ CLI STUFF _____________________________

    def parse_args(self):
        """ Parse the command line parameters that are passed to the program.
        """
        self.parser.add_argument("paths", nargs="*",
                                 help="The paths to input files or folder")

        self.parser.add_argument("-x", "--use_cli", required="-o" in sys.argv,
                                 help="Use the command line interface only (exit the "
                                      "app after finishing)", action="store_true",
                                 default=False)
        # self.parser.add_argument("-i", "--input", required="-x" in sys.argv,
        #                          help="The path to input files or folder")
        # sort_group = self.parser.add_mutually_exclusive_group()
        self.parser.add_argument("-s", "--sort_page", action="store_true", default=False,
                                 help="Sort highlights by page, otherwise sort by date")
        self.parser.add_argument("-m", "--merge", action="store_true", default=False,
                                 help="Merge the highlights of all input books in a "
                                      "single file, otherwise save every book's "
                                      "highlights to a different file")
        self.parser.add_argument("-f", "--html", action="store_true", default=False,
                                 help="Saves highlights in .html format instead of .txt")

        self.parser.add_argument("-np", "--no_page", action="store_true", default=False,
                                 help="Exclude the page number of the highlight")
        self.parser.add_argument("-nd", "--no_date", action="store_true", default=False,
                                 help="Exclude the date of the highlight")
        self.parser.add_argument("-nh", "--no_highlight",
                                 action="store_true", default=False,
                                 help="Exclude the highlighted text of the highlight")
        self.parser.add_argument("-nc", "--no_comment",
                                 action="store_true", default=False,
                                 help="Exclude the comment of the highlight")

        self.parser.add_argument("-o", "--output", required="-x" in sys.argv,
                                 help="The filename of the file (in merge mode) or "
                                 "the directory for saving the highlight files")

        # args, paths = self.parser.parse_known_args()
        args = self.parser.parse_args()
        if args.use_cli:
            self.cli_save_highlights(args)
            sys.exit(0)  # quit the app if cli execution

        # if args.paths:
        #     self.on_file_table_fileDropped(args.paths)

    def cli_save_highlights(self, args):
        """ Saves highlights using the command line interface

        :type args: argparse.Namespace
        :param args: The parsed cli args
        """
        # pprint(args.__dict__)
        files = self.get_lua_files(args.paths)
        if not files:
            return
        path = abspath(args.output)
        if not args.merge:  # save to different files
            if not isdir(path):
                self.parser.error("The output path (-o/--output) must point "
                                  "to an existing directory!")
            saved = self.cli_save_multi_files(args, files)
        else:  # save combined highlights to one file
            if isdir(path):
                ext = "an .html" if args.html else "a .txt"
                self.parser.error("The output path (-o/--output) must be {} filename "
                                  "not a directory!".format(ext))
                return
            saved = self.cli_save_merged_file(args, files)

        all_files = len(files)
        sys.stdout.write(_("\n{} files were saved from the {} processed.\n"
                           "{} files with no highlights.\n").format(saved, all_files,
                                                                    all_files - saved))

    def cli_save_multi_files(self, args, files):
        """ Save each selected book's highlights to a different file

        :type args: argparse.Namespace
        :param args: The parsed cli args
        :type files: list
        :param files: A list with the metadata files to get converted
        """
        saved = 0
        title_counter = 0
        space = " " if not args.no_page and not args.no_date else ""
        line_break = ":" + os.linesep if not args.no_page or not args.no_date else ""
        path = abspath(args.output)
        for file_ in files:
            data = decode_data(file_)
            highlights = []
            for page in data["highlight"]:
                for page_id in data["highlight"][page]:
                    highlights.append(self.cli_analyze_high(data, page, page_id, args))
            if not highlights:  # no highlights
                continue
            authors = ""
            try:
                title = data["stats"]["title"]
                authors = data["stats"]["authors"]
            except KeyError:  # older type file
                title = splitext(basename(file_))[0]
                try:
                    name = title.split("#] ")[1]
                    title = splitext(name)[0]
                except IndexError:  # no "#] " in filename
                    pass
            if not title:
                try:
                    name = file_.split("#] ")[1]
                    title = splitext(name)[0]
                except IndexError:  # no "#] " in filename
                    title = _("NO TITLE FOUND") + str(title_counter)
                    title_counter += 1
            name = title
            if authors:
                name = "{} - {}".format(authors, title)
            if not args.html:
                ext = ".txt"
                text = ""
            else:
                ext = ".html"
                text = HTML_HEAD + BOOK_BLOCK % {"title": title, "authors": authors}
            filename = join(path, sanitize_filename(name) + ext)
            with io.open(filename, "w+", encoding="utf-8", newline="") as text_file:
                # noinspection PyTypeChecker
                for highlight in sorted(highlights, key=partial(self.cli_sort, args)):
                    date_text, high_comment, high_text, page_text = highlight
                    if not args.html:
                        text += (page_text + space + date_text +
                                 line_break + high_text + high_comment)
                        text += 2 * os.linesep
                    else:
                        text += HIGH_BLOCK % {"page": page_text, "date": date_text,
                                              "highlight": high_text,
                                              "comment": high_comment}
                if args.html:
                    text += "\n</div>\n</body>\n</html>"

                text_file.write(text)
                sys.stdout.write("Created {}\n".format(basename(filename)))
                saved += 1
        return saved

    def cli_save_merged_file(self, args, files):
        """ Save the selected book's highlights to a single html file

        :type args: argparse.Namespace
        :param args: The parsed cli args
        :type files: list
        :param files: A list with the metadata files to get converted
        """
        saved = 0
        title_counter = 0
        space = " " if not args.no_page and not args.no_date else ""
        line_break = ":" + os.linesep if not args.no_page or not args.no_date else ""
        text = HTML_HEAD if args.html else ""
        for file_ in files:
            data = decode_data(file_)
            authors = ""
            try:
                title = data["stats"]["title"]
                authors = data["stats"]["authors"]
            except KeyError:  # older type file
                title = splitext(basename(file_))[0]
                try:
                    name = title.split("#] ")[1]
                    title = splitext(name)[0]
                except IndexError:  # no "#] " in filename
                    pass
            if not title:
                try:
                    name = file_.split("#] ")[1]
                    title = splitext(name)[0]
                except IndexError:  # no "#] " in filename
                    title = _("NO TITLE FOUND") + str(title_counter)
                    title_counter += 1
            highlights = []
            for page in data["highlight"]:
                for page_id in data["highlight"][page]:
                    highlights.append(self.cli_analyze_high(data, page, page_id, args))
            if not highlights:  # no highlights
                continue
            if args.html:
                text += BOOK_BLOCK % {"title": title, "authors": authors}
                # noinspection PyTypeChecker
                for high in sorted(highlights, key=partial(self.cli_sort, args)):
                    date_text, high_comment, high_text, page_text = high
                    text += HIGH_BLOCK % {"page": page_text, "date": date_text,
                                          "highlight": high_text, "comment": high_comment}
                text += "</div>\n"
            else:
                name = title
                if authors:
                    name = "{} - {}".format(authors, title)
                line = "-" * 80
                text += line + os.linesep + name + os.linesep + line + os.linesep
                # noinspection PyTypeChecker
                highlights = [i[3] + space + i[0] + line_break + i[2] + i[1] for i in
                              sorted(highlights, key=partial(self.cli_sort, args))]

                text += (os.linesep * 2).join(highlights) + os.linesep * 2
            saved += 1
        text += "\n</body>\n</html>" if args.html else ""
        path = abspath(args.output)
        name, ext = splitext(path)
        new_ext = ".html" if args.html else ".txt"
        if ext.lower() != new_ext:
            path = name + new_ext
        with io.open(path, "w+", encoding="utf-8", newline="") as text_file:
            text_file.write(text)
            sys.stdout.write("Created {}\n\n".format(path))
        return saved

    @staticmethod
    def get_lua_files(dropped):
        """ Return the paths to the .lua metadata files

        :type dropped: list
        :param dropped: The input paths
        """
        paths = []
        fount_txt = "Found: {}\n"
        for path in dropped:
            if isfile(path) and splitext(path)[1] == ".lua":
                paths.append(abspath(path))
                sys.stdout.write(fount_txt.format(path))
        folders = [i for i in dropped if isdir(i)]
        for folder in folders:
            try:
                for dir_tuple in os.walk(folder):
                    dir_path = dir_tuple[0]
                    if dir_path.lower().endswith(".sdr"):  # a book's metadata folder
                        if dir_path.lower().endswith("evernote.sdr"):
                            continue
                        for file_ in dir_tuple[2]:  # get the .lua file not the .old
                            if splitext(file_)[1].lower() == ".lua":
                                path = abspath(join(dir_path, file_))
                                paths.append(path)
                                sys.stdout.write(fount_txt.format(path))
                                break
                    # older metadata storage or android history folder
                    elif (dir_path.lower().endswith(join("koreader", "history"))
                          or basename(dir_path).lower() == "history"):
                        for file_ in dir_tuple[2]:
                            if splitext(file_)[1].lower() == ".lua":
                                path = abspath(join(dir_path, file_))
                                paths.append(path)
                                sys.stdout.write(fount_txt.format(path))
                        continue
            except UnicodeDecodeError:  # os.walk error
                pass
        return paths

    @staticmethod
    def cli_sort(args, data):
        """ Sets the sorting method of written highlights

        :type args: argparse.Namespace
        :param args: The parsed cli args
        :type data: tuple
        param: data: The highlight's data
        """
        return int(data[3][5:]) if args.sort_page else data[0]

    @staticmethod
    def cli_analyze_high(data, page, page_id, args):
        """ Get the highlight's info (text, comment, date and page)

        :type data: dict
        :param data: The highlight's data
        :type page: int
        :param page The page where the highlight starts
        :type page_id: int
        :param page_id The count of this page's highlight
        :type args: argparse.Namespace
        :param args: The parsed cli args
        """
        date = data["highlight"][page][page_id]["datetime"]
        text = data["highlight"][page][page_id]["text"]
        pos_0 = data["highlight"][page][page_id]["pos0"]
        pos_1 = data["highlight"][page][page_id]["pos1"]
        comment = ""
        for bookmark_idx in data["bookmarks"]:
            try:
                book_pos0 = data["bookmarks"][bookmark_idx]["pos0"]
            except KeyError:  # no [bookmark_idx]["pos0"] exists (blank highlight)
                continue
            book_pos1 = data["bookmarks"][bookmark_idx]["pos1"]
            if (pos_0 == book_pos0) and (pos_1 == book_pos1):
                book_text = data["bookmarks"][bookmark_idx].get("text", "")
                if not book_text:
                    break
                book_text = re.sub(r"Page \d+ (.+?) @ \d+-\d+-\d+ \d+:\d+:\d+",
                                   r"\1", book_text, 1, re.DOTALL | re.MULTILINE)
                if text != book_text:
                    comment = book_text
                break
        page_text = "Page " + str(page) if not args.no_page else ""
        date_text = "[" + date + "]" if not args.no_date else ""

        linesep = "<br/>" if args.html else os.linesep
        high_text = text.replace("\\\n", linesep) if not args.no_highlight else ""
        comment = comment.replace("\\\n", linesep)
        line_break2 = os.linesep if not args.no_highlight and comment else ""
        high_comment = (line_break2 + "● " + comment
                        if not args.no_comment and comment else "")
        return date_text, high_comment, high_text, page_text

    @staticmethod
    def get_name(data, meta_path, title_counter):
        """ Return the name of the book entry

        :type data: dict
        :param data: The book's metadata
        :type meta_path: str|unicode
        :param meta_path: The book's metadata path
        :type title_counter: list
        :param title_counter: A list with the current NO TITLE counter
        """
        authors = ""
        try:
            title = data["stats"]["title"]
            authors = data["stats"]["authors"]
        except KeyError:  # older type file
            title = splitext(basename(meta_path))[0]
            try:
                name = title.split("#] ")[1]
                title = splitext(name)[0]
            except IndexError:  # no "#] " in filename
                pass
        if not title:
            try:
                name = meta_path.split("#] ")[1]
                title = splitext(name)[0]
            except IndexError:  # no "#] " in filename
                title = _("NO TITLE FOUND") + str(title_counter[0])
                title_counter[0] += 1
        name = title
        if authors:
            name = "{} - {}".format(authors, title)
        return name


if __name__ == '__main__':
    app = KoHighlights(sys.argv)
