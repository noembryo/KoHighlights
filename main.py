# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals


from boot_config import *
import os, sys, re
import gzip
import json
import shutil
import webbrowser
import subprocess
import argparse
import hashlib
from datetime import datetime
from functools import partial
from collections import defaultdict
from distutils.version import LooseVersion
from os.path import (isdir, isfile, join, basename, splitext, dirname, split, getmtime,
                     abspath, splitdrive)
from pprint import pprint


if QT4:  # ___ ______________ DEPENDENCIES __________________________
    from PySide.QtSql import QSqlDatabase, QSqlQuery
    from PySide.QtCore import (Qt, QTimer, Slot, QThread, QMimeData, QModelIndex,
                               QByteArray, QPoint)
    from PySide.QtGui import (QMainWindow, QApplication, QMessageBox, QIcon, QFileDialog,
                              QTableWidgetItem, QTextCursor, QMenu, QAction, QHeaderView,
                              QPixmap, QListWidgetItem, QBrush, QColor)
else:
    from PySide2.QtWidgets import (QMainWindow, QHeaderView, QApplication, QMessageBox,
                                   QAction, QMenu, QTableWidgetItem, QListWidgetItem,
                                   QFileDialog)
    from PySide2.QtCore import (Qt, QTimer, QThread, QModelIndex, Slot, QPoint, QMimeData,
                                QByteArray)
    from PySide2.QtSql import QSqlDatabase, QSqlQuery
    from PySide2.QtGui import QIcon, QPixmap, QTextCursor, QBrush, QColor

from secondary import *
from gui_main import Ui_Base


if PYTHON2:  # ___ __________ PYTHON 2/3 COMPATIBILITY ______________
    import cPickle as pickle
else:
    import pickle


__author__ = "noEmbryo"
__version__ = "1.7.3.0"


# if sys.platform.lower().startswith("win"):
#     import ctypes
#
#     def hide_console():
#         """ Hides the console window in GUI mode. Necessary for frozen application,
#         because this application support both, command line processing AND GUI mode
#         and therefore cannot be run via pythonw.exe.
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
        self.current_view = BOOKS_VIEW
        self.db_mode = False
        self.toolbar_size = 48
        self.alt_title_sort = False
        self.high_by_page = False
        self.high_merge_warning = True
        self.archive_warning = True
        self.exit_msg = True
        self.db_path = join(SETTINGS_DIR, "data.db")
        self.date_vacuumed = datetime.now().strftime(DATE_FORMAT)
        self.date_format = DATE_FORMAT
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
        self.books = []

        self.header_main = self.file_table.horizontalHeader()
        self.header_main.setDefaultAlignment(Qt.AlignLeft)
        self.header_main.setContextMenuPolicy(Qt.CustomContextMenu)
        self.header_high_view = self.high_table.horizontalHeader()
        self.header_high_view.setDefaultAlignment(Qt.AlignLeft)
        # self.header_high_view.setResizeMode(HIGHLIGHT_H, QHeaderView.Stretch)
        if QT4:
            self.file_table.verticalHeader().setResizeMode(QHeaderView.Fixed)
            self.header_main.setMovable(True)
            self.high_table.verticalHeader().setResizeMode(QHeaderView.Fixed)
            self.header_high_view.setMovable(True)
        else:
            self.file_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.header_main.setSectionsMovable(True)
            self.high_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.header_high_view.setSectionsMovable(True)

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        self.info_fields = [self.title_txt, self.author_txt, self.series_txt,
                            self.lang_txt, self.pages_txt, self.tags_txt]
        self.info_keys = ["title", "authors", "series", "language", "pages", "keywords"]
        self.kor_text = _("Scanning for KOReader metadata files")

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
        self.ico_db_open = QIcon(":/stuff/db_open.png")
        self.ico_app = QIcon(":/stuff/logo64.png")
        self.ico_empty = QIcon(":/stuff/trans32.png")
        self.ico_refresh = QIcon(":/stuff/refresh16.png")
        self.ico_folder_open = QIcon(":/stuff/folder_open.png")

        # noinspection PyArgumentList
        self.clip = QApplication.clipboard()

        self.about = About(self)
        self.auto_info = AutoInfo(self)
        self.filter = Filter(self)

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

        self.review_lbl.setVisible(False)
        self.review_txt.setVisible(False)

        # noinspection PyTypeChecker,PyCallByClass
        QTimer.singleShot(10000, self.auto_check4update)  # check for updates

        main_timer = QTimer(self)  # cleanup threads for ever
        main_timer.timeout.connect(self.thread_cleanup)
        main_timer.start(2000)

        # noinspection PyTypeChecker,PyCallByClass
        QTimer.singleShot(0, self.on_load)

    def on_load(self):
        """ Things that must be done after the initialization
        """
        self.settings_load()
        self.init_db()
        if FIRST_RUN:  # on first run
            self.toolbar.loaded_btn.click()
            self.splitter.setSizes((500, 250))
        self.toolbar.export_btn.setMenu(self.get_export_menu())  # assign/create menu
        self.toolbar.merge_btn.setMenu(self.merge_menu())  # assign/create menu
        self.toolbar.delete_btn.setMenu(self.delete_menu())  # assign/create menu
        self.connect_gui()
        self.passed_files()

        if len(sys.argv) > 1:  # command line arguments exist, open in Loaded mode
            self.toolbar.loaded_btn.click()
        else:  # no extra command line arguments
            if not self.db_mode:
                self.toolbar.loaded_btn.setChecked(True)  # open in Loaded mode
            else:
                self.toolbar.db_btn.setChecked(True)  # open in Archived mode
                text = _("Loading {} database").format(APP_NAME)
                self.loading_thread(DBLoader, self.books, text)
        self.read_books_from_db()  # always load db on start
        if self.current_view == BOOKS_VIEW:
            self.toolbar.books_view_btn.click()  # open in Books view
        else:
            self.toolbar.high_view_btn.click()  # open in Highlights view

        self.show()

    # ___ ___________________ EVENTS STUFF __________________________

    def connect_gui(self):
        """ Make all the extra signal/slots connections
        """
        self.file_selection = self.file_table.selectionModel()
        self.file_selection.selectionChanged.connect(self.file_selection_update)
        self.header_main.sectionClicked.connect(self.on_column_clicked)
        self.header_main.customContextMenuRequested.connect(self.on_column_right_clicked)
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
                self.toolbar.on_scan_btn_clicked()
                return True
            if key == Qt.Key_S:
                self.on_export()
                return True
            if key == Qt.Key_I:
                self.toolbar.on_about_btn_clicked()
                return True
            if key == Qt.Key_F:
                self.toolbar.filter_btn.click()
                return True
            if key == Qt.Key_Q:
                self.close()
            if self.current_view == HIGHLIGHTS_VIEW and self.sel_high_view:
                if key == Qt.Key_C:
                    self.copy_text_2clip(self.get_highlights()[0])
                    return True
        if mod == Qt.AltModifier:  # if alt is pressed
            if key == Qt.Key_A:
                self.on_archive()
                return True
            if self.current_view == HIGHLIGHTS_VIEW and self.sel_high_view:
                if key == Qt.Key_C:
                    self.copy_text_2clip(self.get_highlights()[1])
                    return True

        if key == Qt.Key_Escape:
            self.close()
            return True
        if key == Qt.Key_Delete:
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
        popup = self.popup(_("Confirmation"), _("Exit {}?").format(APP_NAME), buttons=2,
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
        # noinspection PyTypeChecker,PyCallByClass
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.db_path)
        if not self.db.open():
            print("Could not open database!")
            return
        self.query = QSqlQuery()
        if app_config:
            pass
            # self.query.exec_("""PRAGMA user_version""")  # 2do: enable if db changes
            # while self.query.next():
            #     self.check_db_version(self.query.value(0))  # check the db version
        self.set_db_version() if not isfile(self.db_path) else None
        self.create_books_table()

    def check_db_version(self, version):
        """ Updates the db to the last version

        :type version: int
        :param version: The db file version
        """
        if version == DB_VERSION or not isfile(self.db_path):
            return  # the db is up to date or does not exists yet
        self.update_db(version)

    def set_db_version(self):
        """ Set the current database version
        """
        self.query.exec_("""PRAGMA user_version = {}""".format(DB_VERSION))

    def change_db(self, mode):
        """ Changes the current db file

        :type mode: int
        :param mode: Change, create new or reload the current db
        """
        if mode == NEW_DB:
            # noinspection PyCallByClass
            filename = QFileDialog.getSaveFileName(self, _("Type the name of the new db"),
                                                   self.db_path,
                                                   (_("database files (*.db)")))[0]
        elif mode == CHANGE_DB:
            # noinspection PyCallByClass
            filename = QFileDialog.getOpenFileName(self, _("Select a database file"),
                                                   self.db_path,
                                                   (_("database files (*.db)")))[0]
        elif mode == RELOAD_DB:
            filename = self.db_path
        else:
            return
        if filename:
            # self.toolbar.loaded_btn.click()
            if self.toolbar.db_btn.isChecked():
                self.toolbar.update_loaded()
            self.delete_data()
            self.db_path = filename
            self.db_mode = False
            self.init_db()
            self.read_books_from_db()
            if self.toolbar.db_btn.isChecked():
                # noinspection PyTypeChecker,PyCallByClass
                QTimer.singleShot(0, self.toolbar.update_archived)

    def delete_data(self):
        """ Deletes the database data
        """
        self.db.close()  # close the db
        self.db = None
        self.query = None
        # print(self.db.connectionNames())
        # self.db.removeDatabase(self.db.connectionName())

    def create_books_table(self):
        """ Create the books table
        """
        self.query.exec_("""CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, 
                         md5 TEXT UNIQUE NOT NULL, date TEXT, path TEXT, data TEXT)""")

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
            data = json.loads(book[DB_DATA], object_hook=self.keys2int)
            self.books.append({"md5": book[DB_MD5], "date": book[DB_DATE],
                               "path": book[DB_PATH], "data": data})

    @staticmethod
    def keys2int(data):
        """ ReConverts the numeric keys of the Highlights in the data dictionary
            that are converted to strings because of json serialization
        :type data: dict
        :param data: The books to add in the db
        """
        if isinstance(data, dict):
            return {int(k) if k.isdigit() else k: v for k, v in data.items()}
        return data

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
        # self.file_table.setSortingEnabled(False)
        for i in dropped:
            if splitext(i)[1] == ".lua":
                self.create_row(i)
        # self.file_table.setSortingEnabled(True)
        folders = [j for j in dropped if isdir(j)]
        for folder in folders:
            self.loading_thread(Scanner, folder, self.kor_text, clear=False)

    # @Slot(QTableWidgetItem)  # called indirectly from self.file_selection_update
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
        path = self.file_table.item(row, TYPE).data(Qt.UserRole)[0]

        self.high_list.clear()
        self.populate_high_list(data, path)
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

        review = data.get("summary", {}).get("note", "")
        self.review_lbl.setVisible(bool(review))
        self.review_txt.setVisible(bool(review))
        self.review_txt.setText(review)

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

        export_menu = self.get_export_menu()
        export_menu.setIcon(self.ico_file_save)
        export_menu.setTitle(_("Export"))
        menu.addMenu(export_menu)

        if not self.db_mode:
            action = QAction(_("Archive") + "\tAlt+A", menu)
            action.setIcon(self.ico_db_add)
            action.triggered.connect(self.on_archive)
            menu.addAction(action)

            if len(self.sel_indexes) == 1:
                sync_group = QMenu(self)
                sync_group.setTitle(_("Sync"))
                sync_group.setIcon(self.ico_files_merge)
                if self.check4archive_merge() is not False:
                    sync_menu = self.create_archive_merge_menu()
                    sync_menu.setTitle(_("Sync with archived"))
                    sync_menu.setIcon(self.ico_files_merge)
                    sync_group.addMenu(sync_menu)
                action = QAction(_("Sync with file"), sync_group)
                action.setIcon(self.ico_files_merge)
                action.triggered.connect(self.use_meta_files)
                sync_group.addAction(action)

                book_path, book_exists = self.file_table.item(row, TYPE).data(Qt.UserRole)
                if book_exists:
                    action = QAction(_("ReCalculate MD5"), sync_group)
                    action.setIcon(self.ico_refresh)
                    action.triggered.connect(partial(self.recalculate_md5, book_path))
                    sync_group.addAction(action)
                menu.addMenu(sync_group)

                action = QAction(_("Open location"), menu)
                action.setIcon(self.ico_folder_open)
                folder_path = dirname(self.file_table.item(row, PATH).text())
                action.triggered.connect(partial(self.open_file, folder_path))
                menu.addAction(action)

            delete_menu = self.delete_menu()
            delete_menu.setIcon(self.ico_files_delete)
            delete_menu.setTitle(_("Delete") + "\tDel")
            menu.addMenu(delete_menu)
        else:
            action = QAction(_("Delete") + "\tDel", menu)
            action.setIcon(self.ico_files_delete)
            action.triggered.connect(partial(self.delete_actions, 0))
            menu.addAction(action)

        menu.exec_(self.file_table.mapToGlobal(point))

    @Slot(QTableWidgetItem)
    def on_file_table_itemDoubleClicked(self, item):
        """ When an item of the FileTable is double-clicked

        :type item: QTableWidgetItem
        :param item: The item (cell) that is double-clicked
        """
        row = item.row()
        meta_path = self.file_table.item(row, PATH).data(0)
        data = self.file_table.item(row, TITLE).data(Qt.UserRole)
        book_path = self.get_book_path(meta_path, data)
        self.open_file(book_path)

    @staticmethod
    def get_book_path(meta_path, data):
        """ Returns the filename of the book that the metadata refers to

        :type meta_path: str|unicode
        :param meta_path: The path of the metadata file
        :type data: dict
        :param data: The book's metadata
        """
        book_path = data.get("doc_path")
        if not book_path:  # use the metadata file path
            ext = splitext(splitext(meta_path)[0])[1]
            meta_path = splitext(meta_path)[0]
            book_path = splitext(split(meta_path)[0])[0] + ext
        else:  # use the recorded file path
            drive = splitdrive(meta_path)[0]
            book_path = join(drive, os.sep, *(book_path.split("/")[3:]))
        return book_path

    @Slot()
    def on_act_view_book_triggered(self):
        """ The View Book menu entry is pressed
        """
        row = self.sender().data()
        if self.current_view == BOOKS_VIEW:
            item = self.file_table.itemAt(row, 0)
            self.on_file_table_itemDoubleClicked(item)
        elif self.current_view == HIGHLIGHTS_VIEW:
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
            if not self.filter.isVisible():
                self.sel_indexes = self.file_selection.selectedRows()
            else:
                self.sel_indexes = [i for i in self.file_selection.selectedRows()
                                    if not self.file_table.isRowHidden(i.row())]
            self.sel_idx = self.sel_indexes[-1]
        except IndexError:  # empty table
            self.sel_indexes = []
            self.sel_idx = None
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
        :parameter column: The column where the sorting is applied
        """
        if column == self.col_sort:
            self.col_sort_asc = not self.col_sort_asc
        else:
            self.col_sort_asc = True
        self.col_sort = column

    def on_column_right_clicked(self, pos):
        """ Creates a sorting menu for the "Title" column

        :type pos: QPoint
        :parameter pos: The position of the right click
        """
        column = self.header_main.logicalIndexAt(pos)
        name = self.file_table.horizontalHeaderItem(column).text()
        if name == _("Title"):
            menu = QMenu(self)

            action = QAction(_("Ignore english articles"), menu)
            action.setCheckable(True)
            action.setChecked(self.alt_title_sort)
            action.triggered.connect(self.toggle_title_sort)
            menu.addAction(action)

            menu.exec_(self.file_table.mapToGlobal(pos))

    def toggle_title_sort(self):
        """ Toggles the way titles are sorted (use or not A/The)
        """
        self.alt_title_sort = not self.alt_title_sort
        text = _("ReSorting books...")
        if not self.db_mode:
            self.loading_thread(ReLoader, self.loaded_paths.copy(), text)
        else:
            self.loading_thread(DBLoader, self.books, text)

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

        if self.archive_warning:  # warn about book replacement in archive
            extra = _("these books") if len(self.sel_indexes) > 1 else _("this book")
            popup = self.popup(_("Question!"),
                               _("Add or replace {} in the archive?").format(extra),
                               buttons=2, icon=QMessageBox.Question,
                               check_text=_("Don't show this again"))
            self.archive_warning = not popup.checked
            if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
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

        self.status.animation(True)
        self.auto_info.set_text(_("{}.\nPlease Wait...").format(text))
        self.auto_info.show()

        scan_thread = QThread()
        loader = worker(args)
        loader.moveToThread(scan_thread)
        loader.found.connect(self.create_row)
        loader.finished.connect(self.loading_finished)
        loader.finished.connect(scan_thread.quit)
        loader.finished.connect(self.thread_cleanup)
        scan_thread.loader = loader
        scan_thread.started.connect(loader.process)
        scan_thread.start(QThread.IdlePriority)
        self.threads.append(scan_thread)

    def loading_finished(self):
        """ What will happen after the populating of the file_table ends
        """
        if self.current_view == HIGHLIGHTS_VIEW:
            self.scan_highlights_thread()
        else:  # Books view
            self.status.animation(False)
            self.auto_info.hide()

        self.file_table.clearSelection()
        self.sel_idx = None
        self.sel_indexes = []
        self.file_table.resizeColumnsToContents()
        self.toolbar.activate_buttons()

        self.file_table.setSortingEnabled(True)
        order = Qt.AscendingOrder if self.col_sort_asc else Qt.DescendingOrder
        self.file_table.sortByColumn(self.col_sort, order)

    def create_row(self, meta_path, data=None, date=None):
        """ Creates a table row from the given file

        :type meta_path: str|unicode
        :param meta_path: The metadata file to be read
        """
        if not self.db_mode:  # for files
            if meta_path in self.loaded_paths:
                return  # already loaded file
            self.loaded_paths.add(meta_path)
            data = decode_data(meta_path)
            if not data:
                print("No data here!", meta_path)
                return
            date = str(datetime.fromtimestamp(getmtime(meta_path))).split(".")[0]
            stats = self.get_item_stats(meta_path, data)
        else:  # for db entries
            stats = self.get_item_db_stats(data)
        icon, title, authors, percent, rating, status, high_count = stats

        # noinspection PyArgumentList
        color = ("#660000" if status == "abandoned" else
                 # "#005500" if status == "complete" else
                 QApplication.palette().text().color())

        self.file_table.setSortingEnabled(False)
        self.file_table.insertRow(0)

        Item = QTableWidgetItem if not self.alt_title_sort else XTableWidgetTitleItem
        title_item = Item(icon, title)
        title_item.setToolTip(title)
        title_item.setData(Qt.UserRole, data)
        self.file_table.setItem(0, TITLE, title_item)

        author_item = QTableWidgetItem(authors)
        author_item.setToolTip(authors)
        self.file_table.setItem(0, AUTHOR, author_item)

        book_path = self.get_book_path(meta_path, data)
        ext = splitext(book_path)[1]
        book_exists = isfile(book_path)
        book_icon = self.ico_file_exists if book_exists else self.ico_file_missing
        type_item = QTableWidgetItem(book_icon, ext)
        type_item.setToolTip(book_path if book_exists else
                             _("The {} file is missing!").format(ext))
        type_item.setData(Qt.UserRole, (book_path, book_exists))
        self.file_table.setItem(0, TYPE, type_item)

        percent_item = XTableWidgetPercentItem(percent)
        percent_item.setToolTip(percent)
        percent_item.setTextAlignment(Qt.AlignRight)
        self.file_table.setItem(0, PERCENT, percent_item)

        rating_item = QTableWidgetItem(rating)
        rating_item.setToolTip(rating)
        self.file_table.setItem(0, RATING, rating_item)

        count_item = XTableWidgetIntItem(high_count)
        count_item.setToolTip(high_count)
        # count_item.setTextAlignment(Qt.AlignRight)
        self.file_table.setItem(0, HIGH_COUNT, count_item)

        date_item = QTableWidgetItem(date)
        date_item.setToolTip(date)
        self.file_table.setItem(0, MODIFIED, date_item)

        path_item = QTableWidgetItem(meta_path)
        path_item.setToolTip(meta_path)
        self.file_table.setItem(0, PATH, path_item)

        for i in range(8):  # colorize row
            item = self.file_table.item(0, i)
            item.setForeground(QBrush(QColor(color)))
        self.file_table.setSortingEnabled(True)

    def get_item_db_stats(self, data):
        """ Returns the title and authors of a history file

        :type data: dict
        :param data: The dict converted lua file
        """
        if data["highlight"]:
            icon = self.ico_label_green
            high_count = str(len(data["highlight"]))
        else:
            icon = self.ico_empty
            high_count = ""
        title = data["stats"]["title"]
        authors = data["stats"]["authors"]
        title = title if title else _("NO TITLE FOUND")
        authors = authors if authors else _("NO AUTHOR FOUND")
        try:
            percent = str(int(data["percent_finished"] * 100)) + "%"
        except KeyError:
            percent = ""
        if "summary" in data:
            rating = data["summary"].get("rating")
            rating = rating * "*" if rating else ""
            status = data["summary"].get("status")
        else:
            rating = ""
            status = None

        return icon, title, authors, percent, rating, status, high_count

    def get_item_stats(self, filename, data):
        """ Returns the title and authors of a metadata file

        :type filename: str|unicode
        :param filename: The filename to get the stats for
        :type data: dict
        :param data: The dict converted lua file
        """
        if data["highlight"]:
            icon = self.ico_label_green
            high_count = str(len(data["highlight"]))
        else:
            icon = self.ico_empty
            high_count = ""
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
            percent = str(int(data["percent_finished"] * 100)) + "%"
        except KeyError:
            percent = None
        if "summary" in data:
            rating = data["summary"].get("rating")
            rating = rating * "*" if rating else ""
            status = data["summary"].get("status")
        else:
            rating = ""
            status = None

        return icon, title, authors, percent, rating, status, high_count

    # ___ ___________________ HIGHLIGHT TABLE STUFF _________________

    @Slot(QTableWidgetItem)
    def on_high_table_itemClicked(self, item):
        """ When an item of the high_table is clicked

        :type item: QTableWidgetItem
        :param item: The item (cell) that is clicked
        """
        row = item.row()
        path = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)["path"]

        # needed for edit "Comments" or "Find in Books" in Highlight View
        for row in range(self.file_table.rowCount()):  # 2check: need to optimize?
            if path == self.file_table.item(row, TYPE).data(Qt.UserRole)[0]:
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

        highlights, comments = self.get_highlights()

        high_text = _("Copy Highlights")
        com_text = _("Copy Comments")
        if len(self.sel_high_view) == 1:  # single selection
            high_text = _("Copy Highlight")
            com_text = _("Copy Comment")

            text = _("Find in Archive") if self.db_mode else _("Find in Books")
            action = QAction(text, menu)
            action.triggered.connect(partial(self.find_in_books, highlights))
            action.setIcon(self.ico_view_books)
            menu.addAction(action)

            action = QAction(_("Comments"), menu)
            action.triggered.connect(self.on_edit_comment)
            action.setIcon(self.ico_file_edit)
            menu.addAction(action)

        action = QAction(high_text + "\tCtrl+C", menu)
        action.triggered.connect(partial(self.copy_text_2clip, highlights))
        action.setIcon(self.ico_copy)
        menu.addAction(action)

        action = QAction(com_text + "\tAlt+C", menu)
        action.triggered.connect(partial(self.copy_text_2clip, comments))
        action.setIcon(self.ico_copy)
        menu.addAction(action)

        action = QAction(_("Export to file"), menu)
        action.triggered.connect(self.on_export)
        action.setData(2)
        action.setIcon(self.ico_file_save)
        menu.addAction(action)

        menu.exec_(self.high_table.mapToGlobal(point))

    def get_highlights(self):
        """ Returns the selected highlights and the comments texts
        """
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
        return highlights, comments

    def scan_highlights_thread(self):
        """ Gets all the loaded highlights
        """
        self.high_table.model().removeRows(0, self.high_table.rowCount())

        self.status.animation(True)
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
        self.status.animation(False)
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
        item.setToolTip("<p>{}</p>".format(comment)) if comment else None
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

        authors = data["authors"]
        item = QTableWidgetItem(authors)
        item.setToolTip(authors)
        self.high_table.setItem(0, AUTHOR_H, item)

        page = data["page"]
        item = XTableWidgetIntItem(page)
        item.setToolTip(page)
        item.setTextAlignment(Qt.AlignRight)
        self.high_table.setItem(0, PAGE_H, item)

        chapter = data["chapter"]
        item = XTableWidgetIntItem(chapter)
        item.setToolTip(chapter)
        self.high_table.setItem(0, CHAPTER_H, item)

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
            if not self.filter.isVisible():
                self.sel_high_view = self.high_view_selection.selectedRows()
            else:
                self.sel_high_view = [i for i in self.high_view_selection.selectedRows()
                                      if not self.high_table.isRowHidden(i.row())]
        except IndexError:  # empty table
            self.sel_high_view = []
        self.toolbar.activate_buttons()

    def on_highlight_column_clicked(self, column):
        """ Sets the current sorting column

        :type column: int
        :parameter column: The column where the sorting is applied
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
                    self.views.setCurrentIndex(BOOKS_VIEW)
                    self.toolbar.books_view_btn.setChecked(True)
                    self.toolbar.setup_buttons()
                    self.toolbar.activate_buttons()

                    self.file_table.selectRow(row)  # select the book
                    self.on_file_table_itemClicked(item)
                    for high_row in range(self.high_list.count()):  # find the highlight
                        if (self.high_list.item(high_row)
                                .data(Qt.UserRole)[HIGHLIGHT_TEXT] == highlight):
                            self.high_list.setCurrentRow(high_row)  # select the highlight
                            return
            except KeyError:  # old metadata with no "stats"
                continue

    # ___ ___________________ HIGHLIGHTS LIST STUFF _________________

    def populate_high_list(self, data, path=""):
        """ Populates the Highlights list of `Book` view

        :type data: dict
        :param data: The item/book's data
        :type path: str|unicode
        :param path: The item/book's path
        """
        space = (" " if self.status.act_page.isChecked() and
                 self.status.act_date.isChecked() else "")
        line_break = (":\n" if self.status.act_page.isChecked() or
                      self.status.act_date.isChecked() else "")
        def_date_format = self.date_format == DATE_FORMAT
        highlights = self.get_highlights_from_data(data, path)
        for i in sorted(highlights, key=self.sort_high4view):
            chapter_text = i["chapter"]
            if chapter_text and self.status.act_chapter.isChecked():
                chapter_text = "[{0}]\n".format(chapter_text)
            page_text = (_("Page ") + i["page"]
                         if self.status.act_page.isChecked() else "")
            date = i["date"] if def_date_format else self.get_date_text(i["date"])
            date_text = "[" + date + "]" if self.status.act_date.isChecked() else ""
            high_text = i["text"] if self.status.act_text.isChecked() else ""
            line_break2 = ("\n" if self.status.act_comment.isChecked() and i["comment"]
                           else "")
            high_comment = line_break2 + "● " + i["comment"] if line_break2 else ""
            highlight = (page_text + space + date_text + line_break + chapter_text +
                         high_text + high_comment + "\n")

            highlight_item = QListWidgetItem(highlight, self.high_list)
            highlight_item.setData(Qt.UserRole, i)

    def get_highlights_from_data(self, data, path=""):
        """ Get the HighLights from the .sdr data

        :type data: dict
        :param data: The lua converted book data
        :type path: str|unicode
        :param path: The book's path
        """
        authors = data.get("stats", {}).get("authors", _("NO AUTHOR FOUND"))
        title = data.get("stats", {}).get("title", _("NO TITLE FOUND"))

        highlights = []
        for page in data["highlight"]:
            for page_id in data["highlight"][page]:
                highlight = self.get_highlight_info(data, page, page_id)
                if highlight:
                    highlight.update({"authors": authors, "title": title,
                                      "path": path})
                    highlights.append(highlight)
        return highlights

    @staticmethod
    def get_highlight_info(data, page, page_id):
        """ Get the highlight's info (text, comment, date and page)

        :type data: dict
        :param data: The highlight's data
        :type page: int
        :param page The page where the highlight starts
        :type page_id: int
        :param page_id The count of this page's highlight
        """
        highlight = {}
        try:
            high_stuf = data["highlight"][page][page_id]
            date = high_stuf["datetime"]
            text4check = high_stuf["text"]
            chapter = high_stuf.get("chapter", "")
            pat = r"Page \d+ (.+?) @ \d+-\d+-\d+ \d+:\d+:\d+"
            text = text4check.replace("\\\n", "\n")
            comment = ""
            for idx in data["bookmarks"]:  # check for comment text
                if text4check == data["bookmarks"][idx]["notes"]:
                    bkm_text = data["bookmarks"][idx].get("text", "")
                    if not bkm_text or (bkm_text == text4check):
                        break
                    bkm_text = re.sub(pat, r"\1", bkm_text, 1, re.DOTALL | re.MULTILINE)
                    if text4check != bkm_text:  # there is a comment
                        comment = bkm_text.replace("\\\n", "\n")
                        break
            highlight["date"] = date
            highlight["text"] = text
            highlight["comment"] = comment
            highlight["chapter"] = chapter
            highlight["page"] = str(page)
            highlight["page_id"] = page_id
        except KeyError:  # blank highlight
            return
        return highlight

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
            comment = self.high_list.item(row).data(Qt.UserRole)["comment"]
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
            high_text = high_data["text"].replace("\n", "\\\n")

            row = self.sel_idx.row()
            item = self.file_table.item
            data = item(row, TITLE).data(Qt.UserRole)

            for bookmark in data["bookmarks"].keys():
                if high_text == data["bookmarks"][bookmark]["notes"]:
                    data["bookmarks"][bookmark]["text"] = text.replace("\n", "\\\n")
                    break
            item(row, TITLE).setData(Qt.UserRole, data)

            if not self.db_mode:  # Loaded mode
                path = item(row, PATH).text()
                self.save_book_data(path, data)
            else:  # Archived mode
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

            if not self.db_mode:  # Loaded mode
                book_path, ext = splitext(high_data["path"])
                path = join(book_path + ".sdr", "metadata{}.lua".format(ext))
                self.save_book_data(path, data)
            else:  # Archived mode
                self.update_book2db(data)
                path = self.high_table.item(row, PATH_H).text()
                for row in range(self.file_table.rowCount()):
                    if path == self.file_table.item(row, TYPE).data(Qt.UserRole)[0]:
                        self.file_table.item(row, TITLE).setData(Qt.UserRole, data)
                        break

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
        if not self.db_mode:
            if self.edit_lua_file_warning:
                text = _("This is an one-time warning!\n\nIn order to delete highlights "
                         "from a book, its \"metadata\" file must be edited. This "
                         "contains a small risk of corrupting that file and lose all the "
                         "settings and info of that book.\n\nDo you still want to do it?")
                popup = self.popup(_("Warning!"), text, buttons=2,
                                   button_text=(_("Yes"), _("No")))
                if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
                    return
                else:
                    self.edit_lua_file_warning = False
            text = _("This will delete the selected highlights!\nAre you sure?")
        else:
            text = _("This will remove the selected highlights from the Archive!\n"
                     "Are you sure?")
        popup = self.popup(_("Warning!"), text, buttons=2,
                           button_text=(_("Yes"), _("No")))
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
            high_data = self.high_list.item(high_row).data(Qt.UserRole)
            pprint(high_data)
            page = high_data["page"]
            page_id = high_data["page_id"]
            del data["highlight"][page][page_id]  # delete the highlight

            # delete the associated bookmark
            text = high_data["text"]
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

        if not self.db_mode:
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
        return int(data["page"]) if self.high_by_page else data["date"]

    def sort_high4write(self, data):
        """ Sets the sorting method of written highlights

        :type data: tuple
        param: data: The highlight's data
        """
        if self.high_by_page and self.status.act_page.isChecked():
            page = data[3]
            if page.startswith("Page"):
                page = page[5:]
            return int(page)
        else:
            return data[0]

    # ___ ___________________ MERGING - SYNCING STUFF _______________

    def same_book(self, data1, data2, book1="", book2=""):
        """ Check if the supplied metadata comes from the same book

        :type data1: dict
        :param data1: The data of the first book
        :type data2: dict
        :param data2: The data of the second book
        :type book1: str|unicode
        :param book1: The path to the first book
        :type book2: str|unicode
        :param book2: The path to the second book
        """
        md5_1 = data1.get("partial_md5_checksum", data1["stats"].get("md5", None)
                          if "stats" in data1 else None)
        if not md5_1 and book1:
            md5_1 = self.md5_from_file(book1)
        if md5_1:  # got the first MD5, check for the second
            md5_2 = data2.get("partial_md5_checksum", data2["stats"].get("md5", None)
                              if "stats" in data2 else None)
            if not md5_2 and book2:
                md5_2 = self.md5_from_file(book2)
            if md5_2 and md5_1 == md5_2:  # same MD5 for both books
                return True
        return False

    def wrong_book(self):
        """ Shows an info dialog if the book MD5 of two metadata are different
        """
        text = _("It seems that the selected metadata file belongs to a different book..")
        self.popup(_("Book mismatch!"), text, icon=QMessageBox.Critical)

    @staticmethod
    def same_cre_version(data):
        """ Check if the supplied metadata have the same CRE version

        :type data: list[dict]
        :param data: The data to get checked
        """
        try:
            if data[0]["cre_dom_version"] == data[1]["cre_dom_version"]:
                return True
        except KeyError:  # no "cre_dom_version" key (older metadata)
            pass
        return False

    def wrong_cre_version(self):
        """ Shows an info dialog if the CRE version of two metadata are different
        """
        text = _("Can not merge these highlights, because they are produced with a "
                 "different version of the reader engine!\n\n"
                 "The reader engine and the way it renders the text is responsible "
                 "for the positioning of highlights. Some times, code changes are "
                 "made that change its behavior. Its version is written in the "
                 "metadata of a book the first time is opened and can only change "
                 "if the metadata are cleared (loosing all highlights) and open the "
                 "book again as new.\n\n"
                 "The reader's engine version is independent of the KOReader version "
                 "and does not change that often.")
        self.popup(_("Version mismatch!"), text, icon=QMessageBox.Critical)

    def check4archive_merge(self):
        """ Check if the selected books' highlights can be merged
            with its archived version
        """
        idx = self.sel_idx
        data1 = self.file_table.item(idx.row(), idx.column()).data(Qt.UserRole)
        book_path = self.file_table.item(idx.row(), TYPE).data(Qt.UserRole)[0]

        for index, book in enumerate(self.books):
            data2 = book["data"]
            if self.same_book(data1, data2, book_path):
                if self.same_cre_version([data1, data2]):
                    return index
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

    def create_archive_merge_menu(self):
        """ Creates the `Sync` sub-menu
        """
        menu = QMenu(self)

        action = QAction(self.ico_files_merge, _("Merge highlights"), menu)
        action.triggered.connect(partial(self.on_merge_highlights, True))
        menu.addAction(action)

        action = QAction(self.ico_files_merge, _("Sync position only"), menu)
        action.triggered.connect(partial(self.merge_highlights, True, False, True))
        menu.addAction(action)

        return menu

    def on_merge_highlights(self, to_archived=False, filename=""):
        """ Tries to merge/sync highlights

        :type to_archived: bool
        :param to_archived: Merge a book with its archived version
        :type filename: str|unicode
        :param filename: The path to the metadata file to merge the book with
        """
        if self.high_merge_warning:
            text = _("Merging highlights is experimental so, always do backups ;o)\n"
                     "Because of the different page formats and sizes, some page "
                     "numbers in {} might be inaccurate. "
                     "Do you want to continue?").format(APP_NAME)
            popup = self.popup(_("Warning!"), text, buttons=2,
                               button_text=(_("Yes"), _("No")),
                               check_text=_("Don't show this again"))
            self.high_merge_warning = not popup.checked
            if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
                return

        popup = self.popup(_("Warning!"),
                           _("The highlights of the selected entries will be merged.\n"
                             "This can not be undone! Continue?"), buttons=2,
                           button_text=(_("Yes"), _("No")),
                           check_text=_("Sync the reading position too"))
        if popup.buttonRole(popup.clickedButton()) == QMessageBox.AcceptRole:
            self.merge_highlights(popup.checked, True, to_archived, filename)

    def merge_highlights(self, sync, merge, to_archived=False, filename=""):
        """ Merge highlights from the same book in two different devices

        :type sync: bool
        :param sync: Sync reading position
        :type merge: bool
        :param merge: Merge the highlights
        :type to_archived: bool
        :param to_archived: Merge a book with its archived version
        :type filename: str|unicode
        :param filename: The path to the metadata file to merge the book with
        """
        if to_archived:  # Merge/Sync a book with archive
            idx1, idx2 = self.sel_idx, None
            data1 = self.file_table.item(idx1.row(), TITLE).data(Qt.UserRole)
            data2 = self.books[self.check4archive_merge()]["data"]
            path1, path2 = self.file_table.item(idx1.row(), PATH).text(), None
        elif filename:  # Merge/Sync a book with a metadata file
            idx1, idx2 = self.sel_idx, None
            data1 = self.file_table.item(idx1.row(), TITLE).data(Qt.UserRole)
            book1 = self.file_table.item(idx1.row(), TYPE).data(Qt.UserRole)[0]
            data2 = decode_data(filename)
            name2 = splitext(dirname(filename))[0]
            book2 = name2 + splitext(book1)[1]
            if not self.same_book(data1, data2, book1, book2):
                self.wrong_book()
                return
            if not self.same_cre_version([data1, data2]):
                self.wrong_cre_version()
                return
            path1, path2 = self.file_table.item(idx1.row(), PATH).text(), None
        else:  # Merge/Sync two different book files
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
            if data1["highlight"] or data2["highlight"]:  # since there are highlights
                for index in [idx1, idx2]:                # set the green icon
                    if index:
                        item = self.file_table.item(idx1.row(), TITLE)
                        item.setIcon(self.ico_label_green)

        if sync:  # sync position and percent
            if data1["percent_finished"] > data2["percent_finished"]:
                data2["percent_finished"] = data1["percent_finished"]
                data2["last_xpointer"] = data1["last_xpointer"]
            else:
                data1["percent_finished"] = data2["percent_finished"]
                data1["last_xpointer"] = data2["last_xpointer"]

            percent = str(int(data1["percent_finished"] * 100)) + "%"
            self.file_table.item(idx1.row(), PERCENT).setText(percent)
            if not to_archived and not filename:
                self.file_table.item(idx2.row(), PERCENT).setToolTip(percent)

        self.file_table.item(idx1.row(), TITLE).setData(Qt.UserRole, data1)
        self.save_book_data(path1, data1)
        if to_archived:  # update the db item
            self.update_book2db(data2)
        elif filename:  # do nothing with the loaded file
            pass
        else:  # update the second item
            self.file_table.item(idx2.row(), TITLE).setData(Qt.UserRole, data2)
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

    def use_meta_files(self):
        """ Selects a metadata files to sync/merge
        """
        # noinspection PyCallByClass
        filenames = QFileDialog.getOpenFileNames(self, _("Select metadata file"),
                                                 self.last_dir,
                                                 (_("metadata files (*.lua *.old)")))[0]
        if filenames:
            self.last_dir = dirname(filenames[0])
            for filename in filenames:
                self.on_merge_highlights(filename=filename)

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
        if not self.db_mode:  # Loaded mode
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
        else:  # Archived mode
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

    def get_export_menu(self):
        """ Creates the `Export Files` button menu
        """
        menu = QMenu(self)
        for idx, item in enumerate([(_("To individual text files"), MANY_TEXT),
                                    (_("Combined to one text file"), ONE_TEXT),
                                    (_("To individual html files"), MANY_HTML),
                                    (_("Combined to one html file"), ONE_HTML),
                                    (_("To individual csv files"), MANY_CSV),
                                    (_("Combined to one csv file"), ONE_CSV),
                                    (_("To individual markdown files"), MANY_MD),
                                    (_("Combined to one markdown file"), ONE_MD)]):
            action = QAction(item[0], menu)
            action.triggered.connect(self.export_actions)
            action.setData(item[1])
            action.setIcon(self.ico_file_save)
            if idx and (idx % 2 == 0):
                menu.addSeparator()
            menu.addAction(action)
        return menu

    # noinspection PyCallByClass
    def on_export(self):
        """ Export the selected highlights to file(s)
        """
        if self.current_view == BOOKS_VIEW:
            if not self.sel_indexes:
                return
        elif self.current_view == HIGHLIGHTS_VIEW:  # Save from high_table,
            if self.save_sel_highlights():          # combine to one file
                self.popup(_("Finished!"),
                           _("The Highlights were exported successfully!"),
                           icon=QMessageBox.Information)
            return
        self.toolbar.export_btn.showMenu()

    def export_actions(self):
        """ An `Export as...` menu item is clicked
        """
        idx = self.sender().data()
        self.export(idx)

    # noinspection PyCallByClass
    def export(self, idx):
        """ Execute the selected `Export action`

        :type idx: int
        :param idx: The action type
        """
        saved = 0
        space = (" " if self.status.act_page.isChecked() and
                 self.status.act_date.isChecked() else "")
        if idx not in [MANY_MD, ONE_MD]:
            line_break = (":" + os.linesep if self.status.act_page.isChecked() or
                          self.status.act_date.isChecked() else "")
        else:
            line_break = (":*  " + os.linesep if self.status.act_page.isChecked() or
                          self.status.act_date.isChecked() else " ")
        # Save from file_table to different files
        if idx in [MANY_TEXT, MANY_HTML, MANY_CSV, MANY_MD]:
            text = _("Select destination folder for the exported file(s)")
            dir_path = QFileDialog.getExistingDirectory(self, text, self.last_dir,
                                                        QFileDialog.ShowDirsOnly)
            if not dir_path:
                return
            self.last_dir = dir_path
            saved = self.save_multi_files(dir_path, idx, line_break, space)
        # Save from file_table, combine to one file
        elif idx in [ONE_TEXT, ONE_HTML, ONE_CSV, ONE_MD]:
            if idx == ONE_TEXT:
                ext = "txt"
            elif idx == ONE_HTML:
                ext = "html"
            elif idx == ONE_CSV:
                ext = "csv"
            elif idx == ONE_MD:
                ext = "md"
            else:
                return
            filename = QFileDialog.getSaveFileName(self,
                                                   _("Export to {} file").format(ext),
                                                   self.last_dir, "*.{}".format(ext))[0]
            if not filename:
                return
            self.last_dir = dirname(filename)
            saved = self.save_merged_file(filename, idx, line_break, space)

        self.status.animation(False)
        all_files = len(self.sel_indexes)
        self.popup(_("Finished!"), _("{} texts were exported from the {} processed.\n"
                                     "{} files with no highlights.")
                   .format(saved, all_files, all_files - saved),
                   icon=QMessageBox.Information)

    def save_multi_files(self, dir_path, format_, line_break, space):
        """ Save each selected book's highlights to a different file

        :type dir_path: str|unicode
        :param dir_path: The directory where the files will be saved
        :type format_: int
        :param format_: The file format to save
        :type line_break: str|unicode
        :param line_break: The line break used, depending on the file format
        :type space: str|unicode
        :param space: The space used at the header, depending on the contents
        """
        self.status.animation(True)
        saved = 0
        sort_by = self.sort_high4write
        for idx in self.sel_indexes:
            authors, title, highlights = self.get_item_data(idx, format_)
            if not highlights:  # no highlights in book
                continue
            try:
                save_file(title, authors, highlights, dir_path,
                          format_, line_break, space, sort_by)
                saved += 1
            except IOError as err:  # any problem when writing (like long filename, etc)
                self.popup(_("Warning!"),
                           _("Could not save the file to disk!\n{}").format(err))
        return saved

    def save_merged_file(self, filename, format_, line_break, space):
        """ Save the selected books' highlights to a single file

        :type filename: str|unicode
        :param filename: The name of the file we export the highlights
        :type format_: int
        :param format_: The filetype to export
        :type line_break: str|unicode
        :param line_break: The line break used, depending on the file format
        :type space: str|unicode
        :param space: The space used at the header, depending on the contents
        """
        self.status.animation(True)
        saved = 0
        text = (HTML_HEAD if format_ == ONE_HTML
                else CSV_HEAD if format_ == ONE_CSV else "")
        encoding = "utf-8-sig" if ONE_CSV else "utf-8"

        for idx in sorted(self.sel_indexes):
            authors, title, highlights = self.get_item_data(idx, format_)
            if not highlights:  # no highlights
                continue
            highlights = sorted(highlights, key=self.sort_high4write)
            text = get_book_text(title, authors, highlights, format_,
                                 line_break, space, text)
            saved += 1
        if format_ == ONE_HTML:
            text += "\n</body>\n</html>"

        with open(filename, "w+", encoding=encoding, newline="") as text_file:
            text_file.write(text)
        return saved

    def get_item_data(self, idx, format_):
        """ Get the highlight data for an item

        :type idx: QModelIndex
        :param idx: The item's index
        :type format_: int
        :param format_: The output format idx
        """
        row = idx.row()
        data = self.file_table.item(row, 0).data(Qt.UserRole)

        highlights = []
        for page in data["highlight"]:
            for page_id in data["highlight"][page]:
                highlights.append(self.get_formatted_high(data, page, page_id, format_))
        title = self.file_table.item(row, TITLE).data(0)
        authors = self.file_table.item(row, AUTHOR).data(0)
        if authors in [_("OLD TYPE FILE"), _("NO AUTHOR FOUND")]:
            authors = ""
        return authors, title, highlights

    def get_formatted_high(self, data, page, page_id, format_):
        """ Create the highlight's texts

        :type data: dict
        :param data: The highlight's data
        :type page: int
        :param page The page where the highlight starts
        :type page_id: int
        :param page_id The idx of this page's highlight
        :type format_: int
        :param format_ The output format idx
        """
        highlight = self.get_highlight_info(data, page, page_id)
        linesep = "<br/>" if format_ in [ONE_HTML, MANY_HTML] else os.linesep
        comment = highlight["comment"].replace("\n", linesep)
        chapter = (highlight["chapter"].replace("\n", linesep)
                   if self.status.act_chapter.isChecked() else "")
        high_text = (highlight["text"].replace("\n", linesep)
                     if self.status.act_text.isChecked() else "")
        date = highlight["date"]
        date = date if self.date_format == DATE_FORMAT else self.get_date_text(date)
        line_break2 = (os.linesep if self.status.act_text.isChecked() and comment else "")
        if format_ in [ONE_CSV, MANY_CSV]:
            page_text = str(page) if self.status.act_page.isChecked() else ""
            date_text = date if self.status.act_date.isChecked() else ""
            high_comment = (comment if self.status.act_comment.isChecked()
                            and comment else "")
        else:
            page_text = "Page " + str(page) if self.status.act_page.isChecked() else ""
            date_text = "[" + date + "]" if self.status.act_date.isChecked() else ""
            high_comment = (line_break2 + "● " + comment
                            if self.status.act_comment.isChecked() and comment else "")
        return date_text, high_comment, high_text, page_text, chapter

    def save_sel_highlights(self):
        """ Save the selected highlights to a text file (from high_table)
        """
        if not self.sel_high_view:
            return
        # noinspection PyCallByClass
        filename = QFileDialog.getSaveFileName(self, _("Export to file"), self.last_dir,
                                               "text file (*.txt);;html file (*.html);;"
                                               "csv file (*.csv);;markdown file (*.md)")
        if filename[0]:
            filename, extra = filename
            encoding = "utf-8"
            text_out = extra.startswith("text")
            html_out = extra.startswith("html")
            csv_out = extra.startswith("csv")
            md_out = extra.startswith("mark")
            if text_out:
                ext = ".txt"
                text = ""
            elif html_out:
                ext = ".html"
                text = HTML_HEAD
            elif csv_out:
                ext = ".csv"
                text = CSV_HEAD
                encoding = "utf-8-sig"
            elif md_out:
                ext = ".md"
                text = ""
            else:
                return
            filename = splitext(filename)[0] + ext
            self.last_dir = dirname(filename)
        else:
            return

        def_date_format = self.date_format == DATE_FORMAT
        for i in sorted(self.sel_high_view):
            row = i.row()
            data = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)

            if not def_date_format:
                data["date"] = self.get_date_text(data["date"])

            comment = "\n● " + data["comment"] if data["comment"] else ""
            if md_out and comment:
                comment = comment.replace("\n", "  \n")

            if text_out:
                txt = ("{} [{}]\nPage {} [{}]\n[{}]\n{}{}"
                       .format(data["title"], data["authors"], data["page"],
                               data["date"], data["chapter"], data["text"], comment))
                text += txt + "\n\n"
            elif html_out:
                left = "{} [{}]".format(data["title"], data["authors"])
                right = "Page {} [{}]".format(data["page"], data["date"])
                text += HIGH_BLOCK % {"page": left, "date": right, "comment": comment,
                                      "highlight": data["text"],
                                      "chapter": data["chapter"]}
                text += "</div>\n"
            elif csv_out:
                text += get_csv_row(data) + "\n"
            elif md_out:
                txt = data["text"].replace("\n", "  \n")
                chapter = data["chapter"]
                if chapter:
                    chapter = "***{0}***\n\n".format(chapter).replace("\n", "  \n")
                text += ("\n---\n### {} [{}]  \n*Page {} [{}]*  \n{}{}{}\n"
                         .format(data["title"], data["authors"], data["page"],
                                 data["date"], chapter, txt, comment))
            else:
                print("Unknown format export!")
                return
        if text_out or csv_out:
            text.replace("\n", os.linesep)
        with open(filename, "w+", encoding=encoding, newline="") as file2save:
            file2save.write(text)
        return True

    def get_date_text(self, date):
        dt_obj = datetime.strptime(date, DATE_FORMAT)
        date = dt_obj.strftime(self.date_format)
        return date

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
            self.current_view = app_config.get("current_view", BOOKS_VIEW)
            self.db_path = app_config.get("db_path", join(SETTINGS_DIR, "data.db"))
            self.db_mode = app_config.get("db_mode", False)
            self.fold_btn.setChecked(app_config.get("show_info", True))
            self.opened_times = app_config.get("opened_times", 0)
            self.alt_title_sort = app_config.get("alt_title_sort", False)
            self.toolbar_size = app_config.get("toolbar_size", 48)
            self.skip_version = app_config.get("skip_version", None)
            self.date_vacuumed = app_config.get("date_vacuumed", self.date_vacuumed)
            self.date_format = app_config.get("date_format", DATE_FORMAT)
            self.archive_warning = app_config.get("archive_warning", True)
            self.exit_msg = app_config.get("exit_msg", True)
            self.high_merge_warning = app_config.get("high_merge_warning", True)
            self.edit_lua_file_warning = app_config.get("edit_lua_file_warning", True)

            checked = app_config.get("show_items", (True, True, True, True, True))
            if len(checked) != 5:  # settings from older versions
                checked = (True, True, True, True, True)
            self.status.act_page.setChecked(checked[0])
            self.status.act_date.setChecked(checked[1])
            self.status.act_chapter.setChecked(checked[2])
            self.status.act_text.setChecked(checked[3])
            self.status.act_comment.setChecked(checked[4])
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
                  "highlight_width": self.highlight_width, "db_path": self.db_path,
                  "comment_width": self.comment_width, "toolbar_size": self.toolbar_size,
                  "last_dir": self.last_dir, "alt_title_sort": self.alt_title_sort,
                  "archive_warning": self.archive_warning, "exit_msg": self.exit_msg,
                  "current_view": self.current_view, "db_mode": self.db_mode,
                  "high_by_page": self.high_by_page, "date_vacuumed": self.date_vacuumed,
                  "show_info": self.fold_btn.isChecked(), "date_format": self.date_format,
                  "show_items": (self.status.act_page.isChecked(),
                                 self.status.act_date.isChecked(),
                                 self.status.act_chapter.isChecked(),
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
                        config[k] = str(v, encoding="latin")
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
        return pickle.dumps(bytes(array), protocol=0)  # type: ignore

    @staticmethod
    def unpickle(key):
        """ Un-serialize some binary settings

        :type key: str|unicode
        :parameter key: The dict key to be un-pickled
        """
        try:
            value = app_config.get(key)
            if not value:
                return
            if PYTHON2:
                try:
                    # noinspection PyTypeChecker
                    value = pickle.loads(str(value))
                except UnicodeEncodeError:  # settings from Python 3.x
                    return
            else:
                # noinspection PyUnresolvedReferences
                value = value.encode("latin1")
                # noinspection PyTypeChecker
                value = pickle.loads(value, encoding="bytes")
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
              extra_text="", button_text=(_("OK"), _("Cancel")),
              check_text=False, input_text=False):
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
        :parameter check_text: The checkbox's text (checkbox is omitted if False)
        :type input_text: str | unicode | bool
        :parameter input_text: The input text's text (input text is omitted if False)
        """
        popup = XMessageBox(self)
        popup.setWindowIcon(self.ico_app)
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
            popup.addButton(button_text[0], QMessageBox.AcceptRole)
            popup.addButton(button_text[1], QMessageBox.RejectRole)

        if extra_text:  # add an extra button
            popup.addButton(extra_text, QMessageBox.ApplyRole)

        if check_text:  # Show check_box
            popup.set_check(check_text)
        elif input_text:  # Show input QLineEdit
            popup.set_input(input_text)

        popup.exec_()
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
        try:
            if sys.platform == "win32":
                os.startfile(path)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, path])
        except OSError:
            self.popup(_("Error opening target!"),
                       _('"{}" does not exists!').format(path))

    def copy_text_2clip(self, text):
        """ Copy a text to clipboard

        :type text: str|unicode
        """
        if text:
            data = QMimeData()
            data.setText(text)
            self.clip.setMimeData(data)

    def recalculate_md5(self, file_path):
        """ Recalculates the MD5 for a book and saves it to the metadata file

        :type file_path: str|unicode
        :param file_path: The path to the book
        """
        popup = self.popup(_("Confirmation"),
                           _("This action can not be undone.\nContinue?"), buttons=2)
        if popup.buttonRole(popup.clickedButton()) == QMessageBox.AcceptRole:
            row = self.sel_idx.row()
            data = self.file_table.item(row, TITLE).data(Qt.UserRole)
            path = self.file_table.item(row, PATH).text()

            old_md5 = ""
            md5 = self.md5_from_file(file_path)
            if "partial_md5_checksum" in data:
                old_md5 = data["partial_md5_checksum"]
                data["partial_md5_checksum"] = md5
            if "stats" in data and "md5" in data["stats"]:
                old_md5 = data["stats"]["md5"]
                data["stats"]["md5"] = md5

            if old_md5:
                text = _("The MD5 was originally\n{}\nA recalculation produces\n{}\n"
                         "The MD5 was replaced and saved!").format(old_md5, md5)
                self.file_table.item(row, TITLE).setData(Qt.UserRole, data)
                self.save_book_data(path, data)
            else:
                text = _("Metadata file has no MD5 information!")
            self.popup(_("Information"), text, QMessageBox.Information)

    @staticmethod
    def md5_from_file(file_path):
        """ Calculates the MD5 for a file

        :type file_path: str|unicode
        :param file_path: The path to the file
        :return: str|unicode|None
        """
        if isfile(file_path):
            with open(file_path, "rb") as file_:
                # noinspection PyDeprecation
                md5 = hashlib.md5()
                sample = file_.read(1024)
                if sample:
                    md5.update(sample)
                for i in range(11):
                    file_.seek((4 ** i) * 1024)
                    sample = file_.read(1024)
                    if sample:
                        md5.update(sample)
                    else:
                        break
                return md5.hexdigest()

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
        self.db_maintenance()

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

    def db_maintenance(self):
        """ Compacts db every three months
        """
        if self.get_db_book_count():  # db has books
            now = datetime.now()
            delta = now - datetime.strptime(self.date_vacuumed, DATE_FORMAT)
            if delta.days > 90:  # after three months
                self.vacuum_db(info=False)  # compact db
                self.date_vacuumed = now.strftime(DATE_FORMAT)  # reset vacuumed date

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


class KOHighlights(QApplication):

    def __init__(self, *args, **kwargs):
        super(KOHighlights, self).__init__(*args, **kwargs)
        if not QT4:
            self.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        # decode app's arguments
        # try:
        #     sys.argv = [i.decode(sys.getfilesystemencoding()) for i in sys.argv]
        # except AttributeError:  # i.decode does not exists in Python 3
        #     pass
        argv = self.arguments()
        if argv[0].endswith("python.exe") or argv[0].endswith("python3.exe"):
            argv = argv[1:]
        if len(argv) > 1 and argv[1] == "-p":
            del argv[1]
        sys.argv = argv
        self.parser = argparse.ArgumentParser(prog=APP_NAME,
                                              description=_("{} v{} - A KOReader's "
                                                            "highlights converter")
                                              .format(APP_NAME, __version__),
                                              epilog=_("Thanks for using %s!") % APP_NAME)
        self.parser.add_argument("-v", "--version", action="version",
                                 version="%(prog)s v{}".format(__version__))

        self.base = Base()
        if getattr(sys, "frozen", False):  # the app is compiled
            if not sys.platform.lower().startswith("win"):  # no cli in windows
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
        self.base.setWindowTitle(APP_NAME + " portable" if PORTABLE else APP_NAME)
        self.exec_()
        self.deleteLater()  # avoids some QThread messages in the shell on exit
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
        self.parser.add_argument("-s", "--sort_page", action="store_true", default=False,
                                 help="Sort highlights by page, otherwise sort by date")
        self.parser.add_argument("-m", "--merge", action="store_true", default=False,
                                 help="Merge the highlights of all input books in a "
                                      "single file, otherwise exports every book's "
                                      "highlights to a different file")
        self.parser.add_argument("-f", "--html", action="store_true", default=False,
                                 help="Exports highlights in .html format "
                                      "instead of .txt")
        self.parser.add_argument("-c", "--csv", action="store_true", default=False,
                                 help="Exports highlights in .csv format "
                                      "instead of .txt")
        self.parser.add_argument("-md", "--markdown", action="store_true", default=False,
                                 help="Exports highlights in markdown .md format "
                                      "instead of .txt")

        self.parser.add_argument("-np", "--no_page", action="store_true", default=False,
                                 help="Exclude the page number of the highlight")
        self.parser.add_argument("-nd", "--no_date", action="store_true", default=False,
                                 help="Exclude the date of the highlight")
        self.parser.add_argument("-nt", "--no_chapter", action="store_true",
                                 default=False,
                                 help="Exclude the chapter of the highlight")
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

    def cli_save_highlights(self, args):
        """ Saves highlights using the command line interface

        :type args: argparse.Namespace
        :param args: The parsed cli args
        """
        files = self.get_lua_files(args.paths)
        if not files:
            return
        space = " " if not args.no_page and not args.no_date else ""
        if not args.markdown:
            line_break = ":" + os.linesep if not args.no_page or not args.no_date else ""
        else:
            line_break = (":*  " + os.linesep
                          if not args.no_page or not args.no_date else " ")
        path = abspath(args.output)
        if not args.merge:  # save to different files
            if not isdir(path):
                self.parser.error("The output path (-o/--output) must point "
                                  "to an existing directory!")
            saved = self.cli_save_multi_files(args, files, line_break, space)
        else:  # save combined highlights to one file
            if isdir(path):
                ext = ("an .html" if args.html else "a .csv" if args.csv
                       else "an .md" if args.markdown else "a .txt")
                self.parser.error("The output path (-o/--output) must be {} filename "
                                  "not a directory!".format(ext))
                return
            saved = self.cli_save_merged_file(args, files, line_break, space)

        all_files = len(files)
        sys.stdout.write(_("\n{} files were exported from the {} processed.\n"
                           "{} files with no highlights.\n").format(saved, all_files,
                                                                    all_files - saved))

    def cli_save_multi_files(self, args, files, line_break, space):
        """ Save each selected book's highlights to a different file

        :type args: argparse.Namespace
        :param args: The parsed cli args
        :type files: list
        :param files: A list with the metadata files to get converted
        :type line_break: str|unicode
        :param line_break: The line break used, depending on the file format
        :type space: str|unicode
        :param space: The space used at the header, depending on the contents
        """
        saved = 0
        if args.html:
            format_ = MANY_HTML
        elif args.csv:
            format_ = MANY_CSV
        elif args.markdown:
            format_ = MANY_MD
        else:
            format_ = MANY_TEXT
        sort_by = self.cli_sort
        path = abspath(args.output)
        for file_ in files:
            authors, title, highlights = self.cli_get_item_data(file_, args)
            if not highlights:  # no highlights
                continue
            try:
                save_file(title, authors, highlights, path,
                          format_, line_break, space, sort_by)
            except IOError as err:  # any problem when writing (like long filename, etc)
                sys.stdout.write(str("Could not save the file to disk!\n{}").format(err))
        return saved

    def cli_save_merged_file(self, args, files, line_break, space):
        """ Save the selected book's highlights to a single html file

        :type args: argparse.Namespace
        :param args: The parsed cli args
        :type files: list
        :param files: A list with the metadata files to get converted
        :type line_break: str|unicode
        :param line_break: The line break used, depending on the file format
        :type space: str|unicode
        :param space: The space used at the header, depending on the contents
        """
        saved = 0
        text = ""
        encoding = "utf-8"
        if args.html:
            format_ = ONE_HTML
            text = HTML_HEAD
            new_ext = ".html"
        elif args.csv:
            format_ = ONE_CSV
            text = CSV_HEAD
            new_ext = ".csv"
            encoding = "utf-8-sig"
        elif args.markdown:
            format_ = ONE_MD
            new_ext = ".md"
        else:
            format_ = ONE_TEXT
            new_ext = ".txt"

        for file_ in files:
            authors, title, highlights = self.cli_get_item_data(file_, args)
            if not highlights:  # no highlights
                continue
            highlights = sorted(highlights, key=partial(self.cli_sort, args))
            text = get_book_text(title, authors, highlights, format_,
                                 line_break, space, text)
            saved += 1
        if args.html:
            text += "\n</body>\n</html>"
        path = abspath(args.output)
        name, ext = splitext(path)
        if ext.lower() != new_ext:
            path = name + new_ext
        with open(path, "w+", encoding=encoding, newline="") as text_file:
            text_file.write(text)
            sys.stdout.write(str("Created {}\n\n").format(path))
        return saved

    def cli_get_item_data(self, file_, args):
        """ Get the highlight data for an item

        :type file_: str|unicode
        :param file_: The item's path
        :type args: argparse.Namespace
        :param args: The item's arguments
        """
        data = decode_data(file_)
        highlights = []
        for page in data["highlight"]:
            for page_id in data["highlight"][page]:
                highlights.append(self.cli_get_formatted_high(data, page, page_id, args))
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
                title = _("NO TITLE FOUND")
        return authors, title, highlights

    def cli_get_formatted_high(self, data, page, page_id, args):
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
        highlight = self.base.get_highlight_info(data, page, page_id)
        nl = "<br/>" if args.html else os.linesep
        chapter = highlight["chapter"].replace("\n", nl) if not args.no_chapter else ""
        high_text = highlight["text"]
        high_text = high_text.replace("\n", nl) if not args.no_highlight else ""
        comment = highlight["comment"].replace("\n", nl)
        date = highlight["date"]
        line_break2 = os.linesep if not args.no_highlight and comment else ""
        if args.csv:
            page_text = str(page) if not args.no_page else ""
            date_text = date if not args.no_date else ""
            high_comment = comment if not args.no_comment and comment else ""
        else:
            page_text = "Page " + str(page) if not args.no_page else ""
            date_text = "[" + date + "]" if not args.no_date else ""
            high_comment = (line_break2 + "● " + comment
                            if not args.no_comment and comment else "")
        return date_text, high_comment, high_text, page_text, chapter

    @staticmethod
    def get_lua_files(dropped):
        """ Return the paths to the .lua metadata files

        :type dropped: list
        :param dropped: The input paths
        """
        paths = []
        fount_txt = str("Found: {}\n")
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
                                try:
                                    sys.stdout.write(fount_txt.format(path))
                                except UnicodeEncodeError:
                                    sys.stdout.write(fount_txt.format(
                                                     path.encode("utf8")))
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
        if args.sort_page and not args.no_page:
            page = data[3]
            if page.startswith("Page"):
                page = page[5:]
            return int(page)
        else:
            return data[0]

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


if __name__ == "__main__":
    app = KOHighlights(sys.argv)
