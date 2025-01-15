# coding=utf-8
from boot_config import *
from boot_config import _
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
from copy import deepcopy
from collections import defaultdict
from ntpath import normpath
from os.path import (isdir, isfile, join, basename, splitext, dirname, split, getmtime,
                     abspath, splitdrive)
from pprint import pprint

if QT5:
    from PySide2.QtWidgets import (QMainWindow, QHeaderView, QApplication, QMessageBox,
                                   QAction, QMenu, QTableWidgetItem, QListWidgetItem,
                                   QFileDialog, QComboBox)
    from PySide2.QtCore import (Qt, QTimer, QThread, QModelIndex, Slot, QPoint, QMimeData,
                                QByteArray)
    from PySide2.QtSql import QSqlDatabase, QSqlQuery
    from PySide2.QtGui import QIcon, QPixmap, QTextCursor, QBrush, QColor, QFontDatabase
else:  # Qt6
    from PySide6.QtWidgets import (QMainWindow, QHeaderView, QApplication, QMessageBox,
                                   QFileDialog, QTableWidgetItem, QMenu, QListWidgetItem,
                                   QComboBox)
    from PySide6.QtCore import Qt, QTimer, Slot, QPoint, QThread, QModelIndex, QMimeData
    from PySide6.QtGui import (QIcon, QAction, QBrush, QColor, QPixmap, QTextCursor,
                               QFontDatabase)
    from PySide6.QtSql import QSqlDatabase, QSqlQuery

from secondary import *
from gui_main import Ui_Base


from packaging.version import parse as version_parse
import pickle


__author__ = "noEmbryo"
__version__ = "2.3.1.0"


class Base(QMainWindow, Ui_Base):

    def __init__(self, parent=None):
        super(Base, self).__init__(parent)
        # noinspection PyArgumentList
        self.app = QApplication.instance()

        self.scan_thread = None
        self.setupUi(self)
        self.version = __version__
        self.setWindowTitle(APP_NAME + " portable" if PORTABLE else APP_NAME)

        # ___ ________ PREFS SETTINGS ___________
        self.theme = THEME_NONE_OLD
        self.alt_title_sort = False
        self.show_items = [True, True, True, True, True]
        self.show_ref_pg = True

        self.custom_template = False
        self.templ_head = MD_HEAD
        self.templ_body = MD_HIGH
        self.split_chapters = False
        self.head_min = 2
        self.head_max = 6

        self.high_by_page = True
        self.date_format = DATE_FORMAT

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
        self.high_merge_warning = True
        self.archive_warning = True
        self.exit_msg = True
        self.db_path = join(SETTINGS_DIR, "data.db")
        self.date_vacuumed = datetime.now().strftime(DATE_FORMAT)
        # ___ ___________________________________

        self.file_selection = None
        self.sel_idx = None
        self.sel_indexes = []
        self.high_list_selection = None
        self.sel_high_list = []
        self.high_view_selection = None
        self.sel_high_view = []
        self.sync_view_selection = None
        self.sel_sync_view = []

        self.loaded_paths = set()
        self.books2reload = set()
        self.parent_book_data = {}
        self.custom_book_data = {}
        self.reload_highlights = True
        self.reload_from_sync = False
        self.threads = []

        self.query = None
        self.db = None
        self.books = []
        self.sync_groups = []

        tooltip = _("Right click to ignore english articles")
        self.file_table.horizontalHeaderItem(TITLE).setToolTip(tooltip)
        self.file_table.horizontalHeaderItem(TITLE).setStatusTip(tooltip)
        self.header_main = self.file_table.horizontalHeader()
        self.header_main.setDefaultAlignment(Qt.AlignLeft)
        self.header_main.setContextMenuPolicy(Qt.CustomContextMenu)
        self.resize_columns = False
        self.header_high_view = self.high_table.horizontalHeader()
        self.header_high_view.setDefaultAlignment(Qt.AlignLeft)

        self.file_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.header_main.setSectionsMovable(True)
        self.high_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.header_high_view.setSectionsMovable(True)

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        self.info_fields = [self.title_txt, self.author_txt, self.series_txt,
                            self.lang_txt, self.pages_txt, self.tags_txt]
        self.info_keys = ["title", "authors", "series", "language", "pages", "keywords"]
        self.kor_text = _("Scanning for KOReader metadata files.")

        self.ico_file_save = QIcon(":/stuff/file_save.png")
        self.ico_files_merge = QIcon(":/stuff/files_merge.png")
        self.ico_files_delete = QIcon(":/stuff/files_delete.png")
        self.ico_db_add = QIcon(":/stuff/db_add.png")
        self.ico_db_open = QIcon(":/stuff/db_open.png")
        self.ico_db_compact = QIcon(":/stuff/db_compact.png")
        self.ico_refresh = QIcon(":/stuff/refresh16.png")
        self.ico_folder_open = QIcon(":/stuff/folder_open.png")
        self.ico_sort = QIcon(":/stuff/sort.png")
        self.ico_view_books = QIcon(":/stuff/view_books.png")
        self.ico_files_view = QIcon(":/stuff/files_view.png")
        self.ico_file_edit = QIcon(":/stuff/file_edit.png")
        self.ico_copy = QIcon(":/stuff/copy.png")
        self.ico_delete = QIcon(":/stuff/delete.png")
        self.def_icons = [self.ico_file_save,
                          self.ico_files_merge,
                          self.ico_files_delete,
                          self.ico_db_add,
                          self.ico_db_open,
                          self.ico_refresh,
                          self.ico_folder_open,
                          self.ico_sort,
                          self.ico_view_books,
                          self.ico_files_view,
                          self.ico_file_edit,
                          self.ico_copy,
                          self.ico_delete,
                          self.ico_db_compact,
                          ]
        self.ico_file_exists = QIcon(":/stuff/file_exists.png")
        self.ico_file_missing = QIcon(":/stuff/file_missing.png")
        self.ico_label_green = QIcon(":/stuff/label_green.png")
        self.ico_app = QIcon(":/stuff/logo64.png")
        self.ico_empty = QIcon(":/stuff/trans32.png")

        # noinspection PyArgumentList
        self.clip = QApplication.clipboard()

        self.about = About(self)
        self.auto_info = AutoInfo(self)
        self.filter = Filter(self)
        self.prefs = Prefs(self)

        self.toolbar = ToolBar(self)
        self.tool_bar.addWidget(self.toolbar)
        self.toolbar.open_btn.setEnabled(False)
        self.toolbar.merge_btn.setEnabled(False)
        self.toolbar.delete_btn.setEnabled(False)

        self.export_menu = QMenu(self)
        self.export_menu.setTitle(_("Export"))
        self.export_menu.setIcon(self.ico_file_save)
        self.export_menu.aboutToShow.connect(self.create_export_menu)  # assign menu
        if QT6:  # QT6 requires exec() instead of exec_()
            self.export_menu.exec_ = getattr(self.export_menu, "exec")
        self.toolbar.export_btn.setMenu(self.export_menu)

        self.status = Status(self)
        self.statusbar.addPermanentWidget(self.status)

        self.edit_high = TextDialog(self)
        self.edit_high.setWindowTitle(_("Comment"))

        self.description = TextDialog(self)
        self.description.setWindowTitle(_("Description"))
        self.description.high_edit_txt.setReadOnly(True)
        self.description.btn_box.hide()
        self.description_btn.setEnabled(False)

        self.review_lbl.setVisible(False)
        self.review_txt.setVisible(False)

        tbar = self.toolbar
        self.def_btn_icos = []
        self.buttons = [(tbar.scan_btn, "A"),
                        (tbar.export_btn, "B"),
                        (tbar.open_btn, "C"),
                        (tbar.filter_btn, "D"),
                        (tbar.merge_btn, "E"),
                        (tbar.add_btn, "X"),
                        (tbar.delete_btn, "O"),
                        (tbar.clear_btn, "G"),
                        (tbar.prefs_btn, "F"),
                        (tbar.books_view_btn, "H"),
                        (tbar.high_view_btn, "I"),
                        (tbar.sync_view_btn, "W"),
                        (tbar.loaded_btn, "H"),
                        (tbar.db_btn, "K"),
                        (self.custom_btn, "Q"),
                        (self.filter.filter_btn, "D"),
                        (self.description_btn, "V"),
                        (self.filter.clear_filter_btn, "G"),
                        (self.prefs.custom_date_btn, "T"),
                        (self.prefs.custom_template_btn, "Q"),
                        ]

        QTimer.singleShot(10000, self.auto_check4update)  # check for updates

        main_timer = QTimer(self)  # cleanup threads forever
        main_timer.timeout.connect(self.thread_cleanup)
        main_timer.start(2000)

        QTimer.singleShot(0, self.on_load)

    def on_load(self):
        """ Things that must be done after the initialization
        """
        QFontDatabase.addApplicationFont(":/stuff/font.ttf")
        # QFontDatabase.removeApplicationFont(0)

        self.setup_buttons()
        self.settings_load()
        self.init_db()
        if FIRST_RUN:  # on first run
            self.toolbar.loaded_btn.click()
            self.splitter.setSizes((500, 250))
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
                QTimer.singleShot(0, self.load_db_rows)
        self.read_books_from_db()  # always load db on start
        if self.current_view == BOOKS_VIEW:
            self.toolbar.books_view_btn.click()  # open in Books view
        elif self.current_view == SYNC_VIEW:
            self.toolbar.sync_view_btn.click()  # open in Sync view
        else:
            self.toolbar.high_view_btn.click()  # open in Highlights view

        if app_config:
            QTimer.singleShot(0, self.restore_windows)
        else:
            self.resize(800, 600)

        QTimer.singleShot(0, self.show)
        QTimer.singleShot(250, self.load_sync_groups)

    def load_db_rows(self):
        """ Load the rows from the database
        """
        self.loading_thread(DBLoader, self.books,
                            _("Loading {} database.").format(APP_NAME))

    def setup_buttons(self):
        for btn, char in self.buttons:
            self.def_btn_icos.append(btn.icon())
            size = btn.iconSize().toTuple()
            btn.xig = XIconGlyph(self, {"family": "XFont", "size": size, "char": char})
            # btn.glyph = btn.xig.get_icon()

    def set_new_icons(self, menus=True):
        """ Create the new icons

        :type menus: bool
        :param menus: Create the new menu icons too
        """
        QTimer.singleShot(0, partial(self.delayed_set_new_icons, menus))

    def delayed_set_new_icons(self, menus=True):
        """ Delay the creation of the icons to allow for the new palette to be set

        :type menus: bool
        :param menus: Create the menu icons too
        """
        for btn, _ in self.buttons:
            size = btn.iconSize().toTuple()
            btn.setIcon(btn.xig.get_icon({"size": size}))

        if menus:  # recreate the menu icons
            xig = XIconGlyph(self, {"family": "XFont", "size": (16, 16)})

            self.ico_file_save = xig.get_icon({"char": "B"})
            self.ico_files_merge = xig.get_icon({"char": "E"})
            self.ico_files_delete = xig.get_icon({"char": "O"})
            self.ico_db_add = xig.get_icon({"char": "L"})
            self.ico_db_open = xig.get_icon({"char": "M"})
            self.ico_refresh = xig.get_icon({"char": "N"})
            self.ico_folder_open = xig.get_icon({"char": "P"})
            self.ico_sort = xig.get_icon({"char": "S"})
            self.ico_view_books = xig.get_icon({"char": "H"})
            self.act_view_book.setIcon(xig.get_icon({"char": "C"}))
            self.ico_file_edit = xig.get_icon({"char": "Q"})
            self.ico_copy = xig.get_icon({"char": "R"})
            self.ico_delete = xig.get_icon({"char": "O"})
            self.ico_db_compact = xig.get_icon({"char": "J"})

            self.export_menu.setIcon(self.ico_file_save)

    def set_old_icons(self):
        """ Reload the old icons
        """
        for idx, item in enumerate(self.buttons):
            btn = item[0]
            btn.setIcon(self.def_btn_icos[idx])

        self.ico_file_save = self.def_icons[0]
        self.ico_files_merge = self.def_icons[1]
        self.ico_files_delete = self.def_icons[2]
        self.ico_db_add = self.def_icons[3]
        self.ico_db_open = self.def_icons[4]
        self.ico_refresh = self.def_icons[5]
        self.ico_folder_open = self.def_icons[6]
        self.ico_sort = self.def_icons[7]
        self.ico_view_books = self.def_icons[8]
        self.act_view_book.setIcon(self.def_icons[9])
        self.ico_file_edit = self.def_icons[10]
        self.ico_copy = self.def_icons[11]
        self.ico_delete = self.def_icons[12]
        self.ico_db_compact = self.def_icons[13]

        self.export_menu.setIcon(self.ico_file_save)

    def reset_theme_colors(self):
        """ Resets the widget colors after a theme change
        """
        color = self.app.palette().base().color().name()
        self.review_txt.setStyleSheet(f'background-color: "{color}";')

        color = self.app.palette().button().color().name()
        for row in range(self.sync_table.rowCount()):
            wdg = self.sync_table.cellWidget(row, 0)
            wdg.setStyleSheet('QFrame#items_frm {background-color: "%s";}' % color)
            wdg.setup_icons()

        self.setup_buttons()
        self.reload_table(_("Reloading books..."))

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

        self.sync_table.base = self
        self.sync_view_selection = self.sync_table.selectionModel()
        self.sync_view_selection.selectionChanged.connect(self.sync_view_selection_update)

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
        # if mod == Qt.ControlModifier | Qt.AltModifier:  # if control + alt is pressed
        if mod == Qt.ControlModifier:  # if control is pressed
            if key == Qt.Key_Backspace:
                self.toolbar.on_clear_btn_clicked()
            elif key == Qt.Key_L:
                self.toolbar.on_scan_btn_clicked()
            elif key == Qt.Key_S:
                self.on_export()
            elif key == Qt.Key_P:
                self.toolbar.on_prefs_btn_clicked()
            elif key == Qt.Key_I:
                self.toolbar.on_about_btn_clicked()
            elif key == Qt.Key_F:
                self.toolbar.filter_btn.click()
            elif key == Qt.Key_Q:
                self.close()
            elif self.current_view == HIGHLIGHTS_VIEW and self.sel_high_view:
                if key == Qt.Key_C:
                    self.copy_text_2clip(self.get_highlights()[0])

        if mod == Qt.AltModifier:  # if alt is pressed
            if key == Qt.Key_A:
                self.on_archive()
                return True
            elif self.current_view == HIGHLIGHTS_VIEW and self.sel_high_view:
                if key == Qt.Key_C:
                    self.copy_text_2clip(self.get_highlights()[1])
                    return True

        if key == Qt.Key_Escape:
            self.close()
        elif key == Qt.Key_Delete:
            if self.current_view == BOOKS_VIEW:
                self.remove_book_items()
            else:
                self.toolbar.on_delete_btn_clicked()

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
                           check_text=DO_NOT_SHOW)
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
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.db_path)
        if not self.db.open():
            print("Could not open database!")
            return
        self.query = QSqlQuery()
        if QT6:  # QT6 requires exec() instead of exec_()
            self.query.exec_ = getattr(self.query, "exec")
        if app_config:
            pass
            # self.query.exec_("""PRAGMA user_version""")  # 2check: enable if db changes
            # while self.query.next():
            #     self.check_db_version(self.query.value(0))  # check the db version
        self.set_db_version() if not isfile(self.db_path) else None
        self.create_books_table()

    def check_db_version(self, db_version):
        """ Updates the db to the last version

        :type db_version: int
        :param db_version: The db file version
        """
        if db_version == DB_VERSION or not isfile(self.db_path):
            return  # the db is up-to-date or does not exist yet
        self.update_db(db_version)

    def update_db(self, db_version):
        """ Updates the db to the last version"""
        pass

    def set_db_version(self):
        """ Set the current database version
        """
        self.query.exec_(f"""PRAGMA user_version = {DB_VERSION}""")

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
        # print("Reading data from db")
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
        :param ids: The MD5s of the books to be deleted
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
            self.popup(_("Information"), _("The database has been compacted!"),
                       QMessageBox.Information)

    # ___ ___________________ FILE TABLE STUFF ______________________

    @Slot(list)
    def on_file_table_fileDropped(self, dropped):
        """ When some items are dropped to the TableWidget

        :type dropped: list
        :param dropped: The items dropped
        """
        if len(dropped) == 1:
            if splitext(dropped[0])[1] == ".db":
                self.db_path = normpath(dropped[0])
                self.change_db(RELOAD_DB)
                if (self.about.isVisible() and  # update db path on System tab text
                        self.about.about_tabs.currentWidget()
                            .objectName() == "system_tab"):
                    self.about.system_txt.setPlainText(self.about.get_system_info())
                self.popup(_("Information"), _("Database loaded!"),
                           QMessageBox.Information)
                return
        # self.file_table.setSortingEnabled(False)
        for i in dropped:
            if splitext(i)[1] == ".lua" and basename(i).lower() != "custom_metadata.lua":
                self.create_row(normpath(i))  # no highlights in custom_metadata.lua
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

        self.custom_book_data = {}
        self.custom_btn.setChecked(False)
        if not self.db_mode:
            sdr_path = dirname(self.file_table.item(row, PATH).data(0))
            custom_path = join(sdr_path, "custom_metadata.lua")
            if isfile(custom_path):
                custom = decode_data(custom_path)
                self.custom_book_data = deepcopy(data)
                self.custom_book_data.get("doc_props", {}).update(custom["custom_props"])

        self.high_list.clear()
        self.populate_high_list(data, path)
        self.populate_book_info(data, row)

        self.high_list.setCurrentRow(0) if reset else None

    # noinspection PyTestUnpassedFixture
    def populate_book_info(self, data, row):
        """ Fill in the `Book Info` fields

        :type data: dict
        :param data: The item's data
        :type row: int
        :param row: The item's row number
        """
        self.description_btn.setEnabled(bool(data.get("doc_props",
                                                      {}).get("description")))
        self.custom_btn.setEnabled(bool(self.custom_book_data))

        stats = "doc_props" if "doc_props" in data else "stats" if "stats" in data else ""
        for key, field in zip(self.info_keys, self.info_fields):
            try:
                if key == "title" and not data[stats][key]:
                    path = self.file_table.item(row, PATH).data(0)
                    try:
                        name = path.split("#] ")[1]
                        value = splitext(name)[0]
                    except IndexError:  # no "#] " in filename
                        value = ""
                elif key == "pages":
                    if "doc_pages" in data:
                        value = data["doc_pages"]
                    else:  # older type file
                        value = data[stats][key]

                    # no total pages if reference pages are used
                    annotations = data.get("annotations")  # new type metadata
                    if self.show_ref_pg and annotations is not None and len(annotations):
                        annot = annotations[1]  # first annotation
                        ref_page = annot.get("pageref")
                        if ref_page and ref_page.isdigit():  # there is a ref page number
                            value = _("|Ref|")
                elif key == "keywords":
                    keywords = data["doc_props"][key].split("\n")
                    value = "; ".join([i.rstrip("\\") for i in keywords])
                else:
                    value = data.get(stats, {}).get(key)
                try:
                    field.setText(value)
                except TypeError:  # Needs string only
                    field.setText(str(value) if value else "")  # "" if 0
            except KeyError:  # older type file or other problems
                path = self.file_table.item(row, PATH).data(0)
                stats_ = self.get_item_stats(data, path)
                if key == "title":
                    field.setText(stats_["title"])
                elif key == "authors":
                    field.setText(stats_["authors"])
                else:
                    field.setText("")

        review = data.get("summary", {}).get("note", "")
        self.review_lbl.setVisible(bool(review))
        color = self.app.palette().base().color().name()
        self.review_txt.setStyleSheet(f'background-color: "{color}";')
        self.review_txt.setVisible(bool(review))
        self.review_txt.setText(review)

    @Slot(QPoint)
    def on_file_table_customContextMenuRequested(self, point):
        """ When an item of the FileTable is right-clicked

        :type point: QPoint
        :param point: The point where the right-click happened
        """
        if not len(self.file_selection.selectedRows()):  # no items selected
            return

        menu = QMenu(self.file_table)
        if QT6:  # QT6 requires exec() instead of exec_()
            menu.exec_ = getattr(menu, "exec")

        row = self.file_table.itemAt(point).row()
        self.act_view_book.setEnabled(self.toolbar.open_btn.isEnabled())
        self.act_view_book.setData(row)
        menu.addAction(self.act_view_book)
        menu.addMenu(self.export_menu)
        if not self.db_mode:
            action = QAction(_("Archive") + "\tAlt+A", menu)
            action.setIcon(self.ico_db_add)
            action.triggered.connect(self.on_archive)
            menu.addAction(action)

            if len(self.sel_indexes) == 1:
                sync_group = QMenu(self)
                sync_group.setTitle(_("Sync"))
                sync_group.setIcon(self.ico_files_merge)

                action = QAction(_("Create a sync group"), sync_group)
                action.setIcon(self.ico_files_merge)
                path = self.file_table.item(row, PATH).data(0)
                title = self.file_table.item(row, TITLE).data(0)
                data = self.file_table.item(row, TITLE).data(Qt.UserRole)
                book_data = {"path": path, "data": data}
                info = {"title": title,
                        "sync_pos": False,
                        "merge": False,
                        "sync_db": True,
                        "items": [book_data],
                        "enabled": True}
                action.triggered.connect(partial(self.create_sync_row, info))
                sync_group.addAction(action)

                if self.check4archive_merge(book_data) is not False:
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

            elif len(self.sel_indexes) == 2:
                if self.toolbar.merge_btn.isEnabled():
                    action = QAction(_("Sync books"), menu)
                    action.setIcon(self.ico_files_merge)
                    action.triggered.connect(self.toolbar.on_merge_btn_clicked)
                    menu.addAction(action)

            menu.addSeparator()
            delete_menu = self.delete_menu()
            delete_menu.setIcon(self.ico_files_delete)
            delete_menu.setTitle(_("Delete") + "\tDel")
            menu.addMenu(delete_menu)
        else:
            menu.addSeparator()
            action = QAction(_("Delete") + "\tDel", menu)
            action.setIcon(self.ico_files_delete)
            action.triggered.connect(partial(self.delete_actions, DEL_META))
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
        book_path = self.get_book_path(meta_path, data)[0]
        self.open_file(book_path)

    @staticmethod
    def get_book_path(meta_path, data):
        """ Returns the filename of the book that the metadata refers to

        :type meta_path: str|unicode
        :param meta_path: The path of the metadata file
        :type data: dict
        :param data: The book's metadata
        """
        meta_path = splitext(meta_path)[0]  # use the metadata file path
        ext = splitext(meta_path)[1]
        book_path = splitext(split(meta_path)[0])[0] + ext
        book_exists = isfile(book_path)
        if not book_exists:  # use the recorded file path (newer metadata only)
            doc_path = data.get("doc_path")
            if doc_path:
                drive = splitdrive(meta_path)[0]
                # noinspection PyTestUnpassedFixture
                doc_path = join(drive, os.sep, *(doc_path.split("/")[3:]))
                if isfile(doc_path):
                    book_path = doc_path
        return book_path, book_exists

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
            self.review_txt.hide()
            self.review_lbl.hide()
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
            if QT6:  # QT6 requires exec() instead of exec_()
                menu.exec_ = getattr(menu, "exec")

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
        self.blocked_change(self.prefs.alt_title_sort_chk, self.alt_title_sort)
        self.reload_table(_("ReSorting books..."))

    def reload_table(self, text):
        """ Reloads the table depending on the current View mode
        """
        if not self.db_mode:
            self.loading_thread(ReLoader, self.loaded_paths.copy(), text)
        else:
            self.loading_thread(DBLoader, self.books, text)

    @Slot(bool)
    def on_fold_btn_toggled(self, pressed):
        """ Open/closes the Book info panel

        :type pressed: bool
        :param pressed: The arrow button's status
        """
        if pressed:  # Closed
            self.fold_btn.setText(_("Show Book Info"))
            self.fold_btn.setArrowType(Qt.RightArrow)
        else:  # Opened
            self.fold_btn.setText(_("Hide Book Info"))
            self.fold_btn.setArrowType(Qt.DownArrow)
        self.book_info.setHidden(pressed)

    @Slot(bool)
    def on_custom_btn_toggled(self, pressed):
        """ The book's `Custom metadata` button is pressed
        """
        row = self.sel_idx.row()
        if pressed:
            self.populate_book_info(self.custom_book_data, row)
        else:
            data = self.file_table.item(row, TITLE).data(Qt.UserRole)
            self.populate_book_info(data, row)

    @Slot()
    def on_description_btn_clicked(self):
        """ The book's `Description` button is pressed
        """
        data = self.file_table.item(self.sel_idx.row(), TITLE).data(Qt.UserRole)
        description = data["doc_props"]["description"]
        self.description.high_edit_txt.setHtml(description)
        self.description.show()

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
                               check_text=DO_NOT_SHOW)
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
            annotations = data.get("annotations")
            if annotations is not None:  # new format metadata
                for high_idx in annotations:
                    if annotations[high_idx].get("pos0"):
                        break  # there is at least one highlight in the book
                else:  # no highlights don't add
                    empty += 1
                    continue
            else:  # old format metadata
                if not data.get("highlight"):  # no highlights, don't add
                    empty += 1
                    continue
            try:
                md5 = data["partial_md5_checksum"]
            except KeyError:  # older metadata, don't add
                older += 1
                continue
            try:
                data["stats"]["performance_in_pages"] = {}
            except KeyError:  # statistics not available
                pass
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
                   _("{} books were added/updated to the Archive from the "
                     "{} processed.".format(added, len(self.sel_indexes))),
                   icon=QMessageBox.Information)

    def loading_thread(self, worker, args, text, clear=True):
        """ Populates the file_table with different contents
        """
        if clear and (self.current_view != SYNC_VIEW or self.reload_from_sync):
            self.toolbar.on_clear_btn_clicked()
            self.reload_from_sync = False
        self.file_table.setSortingEnabled(False)  # re-enable it after populating table

        self.status.animation(True)
        self.auto_info.set_text(text + _("\nPlease Wait..."))
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
        if not app_config or self.resize_columns:
            self.resize_columns = False
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
            try:
                data = decode_data(meta_path)
            except PermissionError:
                self.error(_("Could not access the book's metadata file\n{}")
                           .format(meta_path))
                return
            except FileNotFoundError:
                self.error(_("Missing book's metadata file: {}".format(meta_path)))
                return
            if not data:
                print("No data here!", meta_path)
                return
            date = str(datetime.fromtimestamp(getmtime(meta_path))).split(".")[0]
            stats = self.get_item_stats(data, meta_path)
        else:  # for db entries
            stats = self.get_item_stats(data)
        title = stats["title"]
        authors = stats["authors"]
        percent = stats["percent"]
        rating = stats["rating"]
        status = stats["status"]
        high_count = stats["high_count"]
        icon = self.ico_label_green if high_count else self.ico_empty

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

        book_path, book_exists = self.get_book_path(meta_path, data)
        ext = splitext(book_path)[1]
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
            if status == "abandoned":
                if self.theme in (THEME_DARK_NEW, THEME_DARK_OLD):
                    color = "#DD0000"
                else:
                    color = "#660000"
                item.setForeground(QBrush(QColor(color)))
        self.file_table.setSortingEnabled(True)

    @staticmethod
    def get_item_stats(data, filename=None):
        """ Returns the title and authors of a metadata file

        :type data: dict
        :param data: The dict converted lua file
        :type filename: str|unicode
        :param filename: The filename to get the stats for
        """
        if filename:  # stats from a file
            title, authors = Base.get_title_authors(data, filename)
        else:  # stats from a db entry
            stats = ("doc_props" if "doc_props" in data
                     else "stats" if "stats" in data else "")
            title = data[stats]["title"]
            authors = data[stats]["authors"]

        annotations = data.get("annotations")
        if annotations is not None:  # new format metadata
            high_count = len([i for i in annotations.values() if i.get("pos0")])
        else:  # old format metadata
            high_count = 0
            try:
                for page in data["highlight"]:
                    high_count += len(data["highlight"][page])
            except KeyError:  # no highlights
                pass
        high_count = str(high_count) if high_count else ""

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
        return {"title": title, "authors": authors, "percent": percent,
                "rating": rating, "status": status, "high_count": high_count}

    @staticmethod
    def get_title_authors(data, filename):
        """ Returns the title and authors of a metadata file

        :type data: dict
        :param data: The dict converted lua file
        :type filename: str|unicode
        :param filename: The filename to get the stats for
        """
        stats = "doc_props" if "doc_props" in data else "stats" if "stats" in data else ""
        try:
            title = data[stats]["title"]
            authors = data[stats]["authors"]
        except KeyError:  # much older type file
            title = splitext(basename(filename))[0]
            try:
                name = title.split("#] ")[1]
                title = splitext(name)[0]
            except IndexError:  # no "#] " in filename
                if splitext(dirname(filename))[1] == ".sdr":
                    title = splitext(basename(dirname(filename)))[0]
            authors = OLD_TYPE
        if not title:
            try:
                name = filename.split("#] ")[1]
                title = splitext(name)[0]
            except IndexError:  # no "#] " in filename
                title = NO_TITLE
        authors = authors if authors else NO_AUTHOR
        return title, authors.replace("\\\n", ", ")

    # ___ ___________________ HIGHLIGHTS LIST STUFF _________________

    def populate_high_list(self, data, path=""):
        """ Populates the Highlights list of `Book` view

        :type data: dict
        :param data: The item/book's data
        :type path: str|unicode
        :param path: The item/book's path
        """
        space = (" " if self.prefs.show_page_chk.isChecked() and
                 self.prefs.show_date_chk.isChecked() else "")
        line_break = (":\n" if self.prefs.show_page_chk.isChecked() or
                      self.prefs.show_date_chk.isChecked() else "")
        def_date_format = self.date_format == DATE_FORMAT
        highlights = self.get_highlights_from_data(data, path)
        new = data.get("annotations") is not None
        for i in sorted(highlights, key=self.sort_high4view):
            chapter_text = (f"[{i['chapter']}]\n"
                            if (i["chapter"] and self.prefs.show_chap_chk.isChecked())
                            else "")
            page = i["page"]
            if new and self.show_ref_pg and i.get("ref_page"):
                page = i["ref_page"]
            page_text = (_("Page {}").format(page)
                         if self.prefs.show_page_chk.isChecked() else "")
            date = i["date"] if def_date_format else self.get_date_text(i["date"])
            date_text = "[" + date + "]" if self.prefs.show_date_chk.isChecked() else ""
            high_text = i["text"] if self.prefs.show_high_chk.isChecked() else ""
            line_break2 = ("\n" if self.prefs.show_comm_chk.isChecked() and i["comment"]
                           else "")
            high_comment = line_break2 + "● " + i["comment"] if line_break2 else ""
            highlight = (page_text + space + date_text + line_break + chapter_text +
                         high_text + high_comment + "\n")

            highlight_item = QListWidgetItem(highlight, self.high_list)
            highlight_item.setData(Qt.UserRole, i)

    def get_highlights_from_data(self, data, path="", meta_path=""):
        """ Get the HighLights from the .sdr data

        :type data: dict
        :param data: The lua converted book data
        :type path: str|unicode
        :param path: The book's path
        :type meta_path: str|unicode
        :param meta_path: The book metadata file's path
        """
        stats = "doc_props" if "doc_props" in data else "stats" if "stats" in data else ""
        authors = data.get(stats, {}).get("authors", NO_AUTHOR)
        title = data.get(stats, {}).get("title", NO_TITLE)
        common = {"authors": authors, "title": title,
                  "path": path, "meta_path": meta_path}

        highlights = []
        annotations = data.get("annotations")
        if annotations is not None:  # new format metadata
            for idx in annotations:
                highlight = self.get_new_highlight_info(data, idx)
                if highlight:
                    # noinspection PyTypeChecker
                    highlight.update(common)
                    highlights.append(highlight)
        else:
            try:
                for page in data["highlight"]:
                    for page_id in data["highlight"][page]:
                        highlight = self.get_old_highlight_info(data, page, page_id)
                        if highlight:
                            # noinspection PyTypeChecker
                            highlight.update(common)
                            highlights.append(highlight)
            except KeyError:  # no highlights
                pass
        return highlights

    @staticmethod
    def get_new_highlight_info(data, idx):
        """ Get the highlight's info (text, comment, date and page) [new format]

        :type data: dict
        :param data: The book's metadata
        :type idx: int
        :param idx: The highlight's idx
        """
        high_data = data["annotations"][idx]
        if not high_data.get("pos0"):
            return  # this is a bookmark not a highlight
        pages = data["doc_pages"]
        page = high_data.get("pageno", 0)
        ref_page = high_data.get("pageref")
        if ref_page and ref_page.isdigit():
            ref_page = int(ref_page)
        else:
            ref_page = None
        highlight = {"text": high_data.get("text", "").replace("\\\n", "\n"),
                     "chapter": high_data.get("chapter", ""),
                     "comment": high_data.get("note", "").replace("\\\n", "\n"),
                     "date": high_data.get("datetime", ""), "idx": idx,
                     "page": page, "ref_page": ref_page, "pages": pages, "new": True}
        return highlight

    @staticmethod
    def get_old_highlight_info(data, page, page_id):
        """ Get the highlight's info (text, comment, date and page)

        :type data: dict
        :param data: The highlight's data
        :type page: int
        :param page The page where the highlight starts
        :type page_id: int
        :param page_id The count of this page's highlight
        """
        pages = data.get("doc_pages", data.get("stats", {}).get("pages", 0))
        highlight = {"page": str(page), "page_id": page_id, "pages": pages, "new": False}
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
            if QT6:  # QT6 requires exec() instead of exec_()
                menu.exec_ = getattr(menu, "exec")

            action = QAction(_("Comment"), menu)
            action.triggered.connect(self.on_edit_comment)
            action.setIcon(self.ico_file_edit)
            menu.addAction(action)

            action = QAction(_("Copy"), menu)
            action.triggered.connect(self.on_copy_highlights)
            action.setIcon(self.ico_copy)
            menu.addAction(action)

            menu.addSeparator()

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
        if QT6:  # QT6 requires exec() instead of exec_()
            self.edit_high.exec_ = getattr(self.edit_high, "exec")
        self.edit_high.exec_()

    def edit_comment_ok(self):
        """ Change the selected highlight's comment
        """
        note = self.edit_high.high_edit_txt.toPlainText()
        if self.file_table.isVisible():  # update comment from Book table
            high_row = self.sel_high_list[-1].row()
            high_data = self.high_list.item(high_row).data(Qt.UserRole)
            item = self.file_table.item
            row = self.sel_idx.row()
            data = item(row, TITLE).data(Qt.UserRole)
            self.update_comment(data, high_data, note)

            if not self.db_mode:  # Loaded mode
                path = item(row, PATH).text()
                self.save_book_data(path, data)
            else:  # Archived mode
                self.update_book2db(data)
                self.on_file_table_itemClicked(item(row, 0), reset=False)

        elif self.high_table.isVisible():  # update comment from Highlights table
            row = self.sel_high_view[-1].row()
            high_data = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
            meta_path = high_data["meta_path"]
            data = self.get_parent_book_data(row)[0]

            self.update_comment(data, high_data, note)
            self.high_table.item(row, HIGHLIGHT_H).setData(Qt.UserRole, high_data)
            self.high_table.item(row, COMMENT_H).setText(note)

            if not self.db_mode:  # Loaded mode
                self.save_book_data(meta_path, data)
            else:  # Archived mode
                self.update_book2db(data)

        self.reload_highlights = True

    @staticmethod
    def update_comment(data, high_data, note):
        """ Update the comment of the selected highlight
        """
        date = datetime.now().strftime(DATE_FORMAT)
        high_text = high_data["text"].replace("\n", "\\\n")
        annotations = data.get("annotations")
        if annotations is not None:  # new format metadata
            for idx in annotations:
                if high_text == annotations[idx]["text"]:
                    annotations[idx]["note"] = note.replace("\n", "\\\n")
                    annotations[idx]["datetime_updated"] = date  # update last edit date
                    high_data["comment"] = note
                    break
        else:  # old format metadata
            for bkm in data["bookmarks"]:
                if high_text == data["bookmarks"][bkm]["notes"]:
                    high_data["comment"] = note
                    data["bookmarks"][bkm]["text"] = note.replace("\n", "\\\n")
                    data["bookmarks"][bkm]["datetime"] = date  # update bkm edit date
                    for pg in data["highlight"]:  # and highlight's too
                        for pg_id in data["highlight"][pg]:
                            if data["highlight"][pg][pg_id]["text"] == high_text:
                                data["highlight"][pg][pg_id]["datetime"] = date
                                break

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
        if self.file_table.isVisible():  # delete comments from Book table
            row = self.sel_idx.row()
            data = self.file_table.item(row, TITLE).data(Qt.UserRole)
            hi_count = int(self.file_table.item(row, HIGH_COUNT).text())
            annotations = data.get("annotations")
            if annotations is not None:  # new format metadata
                for high in self.sel_high_list:
                    high_data = self.high_list.item(high.row()).data(Qt.UserRole)
                    idx = high_data["idx"]
                    del annotations[idx]  # delete the highlight
                    hi_count -= 1
                self.finalize_new_highs(data)
            else:  # old format metadata
                for high in self.sel_high_list:
                    high_data = self.high_list.item(high.row()).data(Qt.UserRole)
                    self.del_old_high(data, high_data)
                    hi_count -= 1
                self.finalize_old_highs(data)
            self.update_and_save_meta(row, data, hi_count)
            self.reload_highlights = True
        elif self.high_table.isVisible():  # delete comments from Highlights table
            hi2del = {}
            idx2del = []
            for hi_idx in self.sel_high_view:  # collect the data from the highlights
                row = hi_idx.row()
                high_data = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
                data = self.get_parent_book_data(row)[0]
                meta_path = high_data["meta_path"]
                idx2del.append(row)
                data_list = hi2del.get(meta_path, [])
                data_list.append((data, high_data, row))
                hi2del[meta_path] = data_list

            for meta_path, data_list in hi2del.items():
                book_row = 0
                for book_row in range(self.file_table.rowCount()):
                    if self.file_table.item(book_row, PATH).text() == meta_path:
                        break
                hi_count = self.file_table.item(book_row, HIGH_COUNT).text()
                hi_count = int(hi_count) if hi_count else 0
                new_format = False
                data = None
                for data, high_data, row in data_list:
                    annotations = data.get("annotations")
                    if annotations is not None:  # new format metadata
                        new_format = True
                        idx = high_data["idx"]
                        del annotations[idx]  # delete the highlight
                        hi_count -= 1
                    else:  # old format metadata
                        self.del_old_high(data, high_data)
                        hi_count -= 1
                if new_format:
                    self.finalize_new_highs(data)
                else:
                    self.finalize_old_highs(data)  # data is same for same meta_path
                self.update_and_save_meta(book_row, data, hi_count)

            idx2del = sorted(idx2del, reverse=True)
            for hi_idx in idx2del:
                self.high_table.removeRow(hi_idx)

    @staticmethod
    def finalize_new_highs(data):
        annotations = data.get("annotations")
        new_annot = {idx + 1: annotations[i]  # renumbering the annotations
                     for idx, i in enumerate(sorted(annotations))}
        if new_annot:
            data["annotations"] = new_annot

    @staticmethod
    def del_old_high(data, hi_data):
        page = int(hi_data["page"])
        page_id = hi_data["page_id"]
        del data["highlight"][page][page_id]  # delete the highlight
        text = hi_data["text"]  # delete the associated bookmark
        for bookmark in list(data["bookmarks"].keys()):
            if text == data["bookmarks"][bookmark]["notes"]:
                del data["bookmarks"][bookmark]

    @staticmethod
    def finalize_old_highs(data):
        for i in list(data["highlight"].keys()):
            if not data["highlight"][i]:  # delete page dicts with no highlights
                del data["highlight"][i]
            else:  # renumbering the highlight keys
                contents = [data["highlight"][i][j] for j in sorted(data["highlight"][i])]
                if contents:
                    for l in list(data["highlight"][i].keys()):
                        del data["highlight"][i][l]  # delete all the items and
                    for k in range(len(contents)):  # rewrite with the new keys
                        data["highlight"][i][k + 1] = contents[k]
        contents = [data["bookmarks"][bookmark] for bookmark in sorted(data["bookmarks"])]
        if contents:  # renumbering the bookmarks keys
            for bookmark in list(data["bookmarks"].keys()):
                del data["bookmarks"][bookmark]  # delete all the items and
            for content in range(len(contents)):  # rewrite them with the new keys
                data["bookmarks"][content + 1] = contents[content]

    def update_and_save_meta(self, row, data, hi_count):
        if not hi_count:  # change icon if no highlights
            self.file_table.item(row, TITLE).setIcon(self.ico_empty)
            hi_count = ""
        self.file_table.item(row, HIGH_COUNT).setText(str(hi_count))
        self.file_table.item(row, HIGH_COUNT).setToolTip(str(hi_count))
        if not self.db_mode:
            path = self.file_table.item(row, PATH).text()
            data["annotations_externally_modified"] = True
            self.save_book_data(path, data)
        else:
            self.update_book2db(data)
            self.on_file_table_itemClicked(self.file_table.item(row, TITLE), reset=False)

    def save_book_data(self, path, data):
        """ Saves the data of a book to its lua file

        :type path: str|unicode
        :param path: The path to the book's data file
        :type data: dict
        :param data: The book's data
        """
        if data.get("annotations") is not None:  # new metadata format
            for annot in data["annotations"].values():
                note = annot.get("note")
                if note is not None and not note:
                    del annot["note"]  # delete key if empty

        times = os.stat(path)  # read the file's created/modified times
        encode_data(path, data)
        if data.get("summary", {}).get("status", "") in ["abandoned", "complete"]:
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

    def set_highlight_sort(self, by_page):
        """ Sets the sorting method of displayed highlights

        :type by_page: bool
        :param by_page: If True, highlights are sorted by page number
        """
        self.high_by_page = by_page
        try:
            row = self.sel_idx.row()
            self.on_file_table_itemClicked(self.file_table.item(row, 0), False)
        except AttributeError:  # no book selected
            pass

    def set_show_ref_pg(self):
        """ Prefer reference page numbers if exists
        """
        self.show_ref_pg = not self.show_ref_pg
        self.reload_highlights = True
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
        if not self.high_by_page:
            return data["date"]
        else:
            if data["new"] and self.show_ref_pg:
                return int(data.get("ref_page", "") or data["page"])
            else:
                return int(data["page"])

    def sort_high4write(self, data):
        """ Sets the sorting method of written highlights

        :type data: tuple
        param: data: The highlight's data
        """
        if self.high_by_page and self.prefs.show_page_chk.isChecked():
            page = data[3]
            if page.startswith("Page"):
                page = page[5:]
            return int(page)
        else:
            return data[0]

    # ___ ___________________ HIGHLIGHT TABLE STUFF _________________

    @Slot(QTableWidgetItem)
    def on_high_table_itemClicked(self, item):
        """ When an item of the high_table is clicked

        :type item: QTableWidgetItem
        :param item: The item (cell) that is clicked
        """
        # row = item.row()
        # self.get_parent_book_data(row)

    def get_parent_book_data(self, row):
        """ Returns the data of the parent book of the given highlight

        :type row: int
        :param row: The row of the highlight
        """
        meta_path = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)["meta_path"]
        for row in range(self.file_table.rowCount()):  # 2check: need to optimize?
            if meta_path == self.file_table.item(row, PATH).data(0):
                parent_book_data = self.file_table.item(row, TITLE).data(Qt.UserRole)
                return parent_book_data, meta_path

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
        if QT6:  # QT6 requires exec() instead of exec_()
            menu.exec_ = getattr(menu, "exec")

        row = self.high_table.itemAt(point).row()
        col = self.high_table.itemAt(point).column()
        self.act_view_book.setData(row)
        self.act_view_book.setEnabled(self.toolbar.open_btn.isEnabled())
        menu.addAction(self.act_view_book)

        highlights, comments, values = self.get_highlights(col)

        single = len(self.sel_high_view) == 1
        if single:  # single selection
            high_text = _("Copy Highlight")
            com_text = _("Copy Comment")
            val_text = _("Copy {} value")

            text = _("Find in Archive") if self.db_mode else _("Find in Books")
            action = QAction(text, menu)
            action.triggered.connect(partial(self.find_in_books, highlights, row))
            action.setIcon(self.ico_view_books)
            menu.addAction(action)

            action = QAction(_("Edit Comment"), menu)
            action.triggered.connect(self.on_edit_comment)
            action.setIcon(self.ico_file_edit)
            menu.addAction(action)
        else:
            high_text = _("Copy Highlights")
            com_text = _("Copy Comments")
            val_text = _("Copy {} values")

        action = QAction(high_text + "\tCtrl+C", menu)
        action.triggered.connect(partial(self.copy_text_2clip, highlights))
        action.setIcon(self.ico_copy)
        menu.addAction(action)

        action = QAction(com_text + "\tAlt+C", menu)
        action.triggered.connect(partial(self.copy_text_2clip, comments))
        action.setIcon(self.ico_copy)
        menu.addAction(action)

        if col not in [HIGHLIGHT_H, COMMENT_H]:
            action = QAction(val_text.format(HIGH_COL_NAMES[col]), menu)
            action.triggered.connect(partial(self.copy_text_2clip, values))
            action.setIcon(self.ico_copy)
            menu.addAction(action)

        action = QAction(_("Export to file"), menu)
        action.triggered.connect(self.on_export)
        action.setData(2)
        action.setIcon(self.ico_file_save)
        menu.addAction(action)

        menu.addSeparator()
        action = QAction(_("Delete") + "\tDel", menu)
        action.setIcon(self.ico_files_delete)
        action.triggered.connect(self.toolbar.on_delete_btn_clicked)
        menu.addAction(action)

        menu.exec_(self.high_table.mapToGlobal(point))

    def get_highlights(self, col=None):
        """ Returns the selected highlights and the comments texts
        """
        col = HIGHLIGHT_H if col is None else col
        highlights = ""
        comments = ""
        values = ""
        for idx in self.sel_high_view:
            item_row = idx.row()
            data = self.high_table.item(item_row, HIGHLIGHT_H).data(Qt.UserRole)
            highlight = data["text"]
            if highlight:
                highlights += highlight + "\n\n"
            comment = data["comment"]
            if comment:
                comments += comment + "\n\n"
            values += self.high_table.item(item_row, col).text() + "\n"
        highlights = highlights.rstrip("\n").replace("\n", os.linesep)
        comments = comments.rstrip("\n").replace("\n", os.linesep)
        values = values.rstrip("\n").replace("\n", os.linesep)
        return highlights, comments, values

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
        item.setToolTip(f"<p>{text}</p>")
        item.setData(Qt.UserRole, data)
        self.high_table.setItem(0, HIGHLIGHT_H, item)

        comment = data["comment"]
        item = QTableWidgetItem(comment)
        item.setToolTip(f"<p>{comment}</p>") if comment else None
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

        if data["new"] and self.show_ref_pg:
            page = str(data.get("ref_page", "") or data["page"])
        else:
            page = str(data["page"])
        item = XTableWidgetIntItem(page)
        item.setToolTip(page)
        item.setTextAlignment(Qt.AlignRight)
        self.high_table.setItem(0, PAGE_H, item)

        chapter = data["chapter"]
        item = XTableWidgetIntItem(chapter)
        item.setToolTip(chapter)
        self.high_table.setItem(0, CHAPTER_H, item)

        # path = data["path"]
        path = data.get("meta_path", "")
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

    def find_in_books(self, highlight, hi_row):
        """ Finds the current highlight in the "Books View"

        :type highlight: str|unicode
        :parameter highlight: The highlight we are searching for
        """
        data, meta_path = self.get_parent_book_data(hi_row)

        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, TITLE)
            row_meta_path = self.file_table.item(row, PATH).data(0)
            try:  # find the book row
                if meta_path == row_meta_path:
                    self.toolbar.books_view_btn.click()
                    self.toolbar.setup_buttons()
                    self.toolbar.activate_buttons()
                    self.file_table.selectRow(row)  # select the book
                    self.on_file_table_itemClicked(item)
                    for high_row in range(self.high_list.count()):  # find the highlight
                        if (self.high_list.item(high_row)
                                .data(Qt.UserRole)["text"] == highlight):
                            self.high_list.setCurrentRow(high_row)  # select the highlight
                            return
            except KeyError:  # old metadata with no "stats"
                continue

    # ___ ___________________ SYNC GROUPS TABLE STUFF _______________

    @Slot(QTableWidgetItem)
    def on_sync_table_itemClicked(self, item):
        """ When an item of the sync_table is clicked

        :type item: QTableWidgetItem
        :param item: The item (cell) that is clicked
        """
        # row = item.row()
        # # path = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)["path"]

    # noinspection PyUnusedLocal
    def sync_view_selection_update(self, selected, deselected):
        """ When a row in sync_table gets selected

        :type selected: QModelIndex
        :parameter selected: The selected row
        :type deselected: QModelIndex
        :parameter deselected: The deselected row
        """
        try:
            self.sel_sync_view = self.sync_view_selection.selectedRows()
        except IndexError:  # empty table
            self.sel_sync_view = []
        self.toolbar.activate_buttons()

    def create_sync_row(self, data, quiet=False):
        """ Creates a sync_table row from the given data

        :type data: dict|list
        :param data: The sync_group data
        :type quiet: bool
        :param quiet: Switch to the Sync view
        """
        if self.current_view != SYNC_VIEW and not quiet:
            self.toolbar.sync_view_btn.setChecked(True)
            self.toolbar.change_view()

        self.sync_table.setSortingEnabled(False)
        if isinstance(data, dict):
            count = self.sync_table.rowCount()
            self.sync_table.insertRow(count)
            wdg = self.create_sync_widget(data)
            wdg.idx = count
            self.sync_groups.append(data)
            self.sync_table.setCellWidget(count, 0, wdg)
            self.sync_table.setRowHeight(count, wdg.sizeHint().height())
            wdg.check_data()
        else:
            for idx, data in enumerate(data):
                self.sync_table.insertRow(idx)
                wdg = self.create_sync_widget(data)
                self.sync_table.setCellWidget(idx, 0, wdg)
                self.sync_table.setRowHeight(idx, wdg.sizeHint().height())
                wdg.on_power_btn_clicked(data.get("enabled", True))
                wdg.idx = idx
                self.sync_groups.append(data)
                folded = data.get("folded", False)
                wdg.fold_btn.setChecked(folded)
                wdg.on_fold_btn_toggled(folded)
                wdg.check_data()
        self.sync_table.setSortingEnabled(True)
        QTimer.singleShot(0, self.save_sync_groups)

    def create_sync_widget(self, data):
        wdg = SyncGroup(self)
        wdg.data = data
        wdg.power_btn.setChecked(data.get("enabled", True))
        wdg.title_lbl.setText(data.get("title", ""))
        wdg.sync_pos_chk.setChecked(data.get("sync_pos", True))
        wdg.merge_chk.setChecked(data.get("merge", True))
        wdg.sync_db_chk.setChecked(data.get("sync_db", False))

        items = deepcopy(data.get("items", [{"path": "", "data": {}}]))
        for item in items:
            wdg.add_item(item)
        return wdg

    def synchronize_group(self, group, multi=False):
        """ Start the process of syncing/merging the group

        :type group: SyncGroup
        :param group: The group to be processed
        """
        group.on_refresh_btn_clicked()
        if not group.sync_items[0].ok:
            self.popup(_(f'Error in group "{group.data["title"]}"!'),
                       _("There is a problem with the first metadata file path!\nCheck "
                         "the Tooltip that appears while hovering the mouse over it."),
                       icon=QMessageBox.Critical)
            return
        sync2db = group.sync_db_chk.isChecked()
        group_changed = sync2db
        to_process = []
        for idx, item in enumerate(group.sync_items):
            if not item.ok:
                continue
            info = group.data["items"][idx]
            mod_time = os.stat(info["path"]).st_mtime
            to_process.append((info, mod_time))
        to_process = sorted(to_process, key=lambda x: x[1], reverse=True)
        to_process = [i[0] for i in to_process]

        if sync2db:
            book_data = {"data": group.data["items"][0]["data"],
                         "path": group.data["items"][0]["path"]}
            db_idx = self.check4archive_merge(book_data)
            if db_idx:
                db_data = self.books[db_idx]["data"]
                to_process.append({"data": db_data, "path": ""})

        if len(to_process) > 1:
            if group.sync_pos_chk.isChecked():
                self.sync_pos(to_process)
                group_changed = True
            if group.merge_chk.isChecked():
                items = []
                for book_info in to_process:  # book_info: {"path": str, "data": dict}
                    data = book_info["data"]
                    total = data.get("doc_pages", data.get("stats", {}).get("pages", 0))
                    if group.new_format:
                        items.append((data["annotations"], total))
                    else:
                        items.append((data["highlight"], data["bookmarks"], total,
                                      book_info["path"]))
                if group.new_format:
                    self.merge_new_highs(items)
                else:
                    self.merge_old_highs(items)
                group_changed = True

        if group_changed:
            for item in deepcopy(to_process):
                if item["path"]:  # db version has no path
                    item["data"]["annotations_externally_modified"] = True
                    self.save_book_data(item["path"], item["data"])

            if sync2db:  # add the newest version of the book to db
                new_data = deepcopy(to_process[0])
                path = new_data["path"]
                data = new_data["data"]
                date = str(datetime.fromtimestamp(getmtime(path))).split(".")[0]
                md5 = data["partial_md5_checksum"]
                self.delete_books_from_db([md5])  # remove the existing version if any
                try:  # clean up data that can be cluttered
                    new_data["stats"]["performance_in_pages"] = {}
                    new_data["page_positions"] = {}
                    new_data.pop("annotations_externally_modified", None)
                except KeyError:
                    pass
                self.add_books2db([{"md5": md5, "path": path, "date": date,
                                    "data": json.dumps(data)}])
            self.update_new_values(group)
            text = _("Synchronization process completed")
        else:
            text = _("Nothing to sync")

        if not multi:  # one group Sync
            self.popup(_("Information"), text, QMessageBox.Information)
        else:  # multiple Sync operations
            if group_changed:
                return True  # needed for counting the number of groups changed

    def update_new_values(self, group):
        """ Updates the book table after sync_groups execution
        """
        self.reload_highlights = True
        row_infos = {}
        for idx, item in enumerate(group.data["items"]):
            if not group.sync_items[idx].ok:
                continue
            path = item["path"]
            for row in range(self.file_table.rowCount()):
                if self.file_table.item(row, PATH).text() == path:
                    row_infos[row] = item
                    break
        for row in row_infos:
            data = row_infos[row]["data"]
            self.file_table.item(row, TITLE).setData(Qt.UserRole, data)
            hi_count = self.get_item_stats(data)["high_count"]
            if hi_count and hi_count != "0":
                self.file_table.item(row, TITLE).setIcon(self.ico_label_green)
            self.file_table.item(row, HIGH_COUNT).setText(hi_count)
            self.file_table.item(row, HIGH_COUNT).setToolTip(hi_count)
            if group.sync_pos_chk.isChecked():
                percent = str(int(data.get("percent_finished", 0) * 100)) + "%"
                self.file_table.item(row, PERCENT).setText(percent)
                self.file_table.item(row, PERCENT).setToolTip(percent)

    def update_sync_groups(self):
        """ Update the sync groups in memory and on disk
        """
        del self.sync_groups[:]
        for i in range(self.sync_table.rowCount()):
            wdg = self.sync_table.cellWidget(i, 0)
            wdg.idx = i  # update the index of widget
            wdg.check_data()
            self.sync_groups.append(wdg.data)

        self.save_sync_groups()

    def load_sync_groups(self):
        """ Load the sync groups from a file
        """
        try:
            with open(SYNC_FILE, "r", encoding="utf-8") as f:
                sync_groups = json.load(f)
        except (IOError, ValueError):  # no json file exists or corrupted file
            return
        self.create_sync_row(sync_groups, quiet=True)

    def save_sync_groups(self):
        """ Save the sync groups to a file
        """
        sync_groups = deepcopy(self.sync_groups)
        sync_groups = [i for i in sync_groups if i["items"][0].get("path")]
        with open(SYNC_FILE, "w+", encoding="utf-8") as f:
            items = [i for grp in sync_groups for i in grp["items"] if i.get("path")]
            for item in items:
                item["data"] = {}
                item["path"] = normpath(item["path"])
            json.dump(sync_groups, f, indent=4)

    # ___ ___________________ MERGING - SYNCING STUFF _______________

    def same_book(self, data1, data2, meta_path1="", meta_path2=""):
        """ Check if the supplied metadata comes from the same book

        :type data1: dict
        :param data1: The data of the first book
        :type data2: dict
        :param data2: The data of the second book
        :type meta_path1: str|unicode
        :param meta_path1: The path to the first book
        :type meta_path2: str|unicode
        :param meta_path2: The path to the second book
        """
        if ((meta_path1 and isfile(join(dirname(meta_path1), "ignore_md5")))
                or (meta_path2 and isfile(join(dirname(meta_path2), "ignore_md5")))):
            return True  # hack to totally ignore the MD5 check

        md5_1 = data1.get("partial_md5_checksum", data1["stats"].get("md5", None)
                          if "stats" in data1 else None)
        if not md5_1 and meta_path1:
            md5_1 = self.md5_from_file(meta_path1)
        if md5_1:  # got the first MD5, check for the second
            md5_2 = data2.get("partial_md5_checksum", data2["stats"].get("md5", None)
                              if "stats" in data2 else None)
            if not md5_2 and meta_path2:
                md5_2 = self.md5_from_file(meta_path2)
            if md5_2 and md5_1 == md5_2:  # same MD5 for both books
                return True
        return False

    def wrong_book(self):
        """ Shows an info dialog if the book MD5 of two metadata are different
        """
        text = _("It seems that the selected metadata file belongs to a different file..")
        self.popup(_("Book mismatch!"), text, icon=QMessageBox.Critical)

    @staticmethod
    def same_cre_version(data1, data2):
        """ Check if the supplied metadata have the same CRE version

        :type data1: dict
        :param data1: The data of the first book
        :type data2: dict
        :param data2: The data of the second book
        """
        try:
            if data1["cre_dom_version"] == data2["cre_dom_version"]:
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

    def check4archive_merge(self, book_data):
        """ Check if the selected books' highlights can be merged
            with its archived version

        :type book_data: dict
        :param book_data: The data of the book
        """
        data1 = book_data["data"]
        book_path = book_data["path"]

        for index, book in enumerate(self.books):
            data2 = book["data"]
            if self.same_book(data1, data2, book_path):
                if self.same_cre_version(data1, data2):
                    return index
        return False

    def wrong_meta_format(self):
        """ Shows an info dialog if the format of the two metadata are different
        """
        text = _("Can not merge these highlights, because their metadata format are "
                 "different!\nThere was a re-write of the highlight/bookmark "
                 "structure of KOReader that make them incompatible.\n\nRe-open the "
                 "books with a newer version of KOReader to update them and then merge "
                 "them using KOHighlights.")
        self.popup(_("Metadata format mismatch!"), text, icon=QMessageBox.Critical)

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
        if self.merge_warning_stop():
            return
        popup = self.popup(_("Warning!"),
                           _("The highlights of the selected entries will be merged.\n"
                             "This can not be undone! Continue?"), buttons=2,
                           button_text=(_("Yes"), _("No")),
                           check_text=_("Sync the reading position too"))
        if popup.buttonRole(popup.clickedButton()) == QMessageBox.AcceptRole:
            self.merge_highlights(popup.checked, True, to_archived, filename)

    def merge_warning_stop(self):
        """ Stop if the merge warning is answered "No"
        """
        if self.high_merge_warning:
            text = _("Merging highlights is experimental so, always do backups ;o)\n"
                     "Because of the different page formats and sizes, some page "
                     "numbers in {} might be inaccurate. "
                     "Do you want to continue?").format(APP_NAME)
            popup = self.popup(_("Warning!"), text, buttons=2,
                               button_text=(_("Yes"), _("No")),
                               check_text=DO_NOT_SHOW)
            self.high_merge_warning = not popup.checked
            if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
                return True

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
        item = self.file_table.item
        if to_archived:  # Merge/Sync a book with archive
            idx1, idx2 = self.sel_idx, None
            data1 = item(idx1.row(), TITLE).data(Qt.UserRole)
            path1, path2 = item(idx1.row(), PATH).text(), None
            book_data = {"data": data1, "path": path1}
            db_idx = self.check4archive_merge(book_data)
            if not db_idx:
                return
            data2 = self.books[db_idx]["data"]
        elif filename:  # Merge/Sync a book with a metadata file
            idx1, idx2 = self.sel_idx, None
            data1 = item(idx1.row(), TITLE).data(Qt.UserRole)
            book1 = item(idx1.row(), TYPE).data(Qt.UserRole)[0]
            data2 = decode_data(filename)
            name2 = splitext(dirname(filename))[0]
            book2 = name2 + splitext(book1)[1]
            if not self.same_book(data1, data2, book1, book2):
                self.wrong_book()
                return
            if not self.same_cre_version(data1, data2):
                self.wrong_cre_version()
                return
            path1, path2 = item(idx1.row(), PATH).text(), None
        else:  # Merge/Sync two different book files
            idx1, idx2 = self.sel_indexes
            data1, data2 = [item(idx.row(), TITLE).data(Qt.UserRole)
                            for idx in [idx1, idx2]]
            path1, path2 = [item(idx.row(), PATH).text()
                            for idx in [idx1, idx2]]

        if merge:  # merge highlights
            data1_new = data1.get("annotations") is not None
            data2_new = data2.get("annotations") is not None
            new_type = data1_new and data2_new
            datas = [data1, data2]
            if path2 and (os.stat(path1).st_mtime < os.stat(path2).st_mtime):
                datas = [data2, data1]  # put the newer metadata first
            items = []
            if new_type:  # new format metadata
                for data in datas:
                    total = data.get("doc_pages", data.get("stats", {}).get("pages", 0))
                    items.append([data["annotations"], total])
                self.merge_new_highs(items)
                if data1["annotations"]:  # update row data for books
                    num = str(len([i for i in data1["annotations"].values()
                                   if i.get("pos0")]))
                    for index in [idx1, idx2]:
                        if index:
                            item(index.row(), TITLE).setIcon(self.ico_label_green)
                            item(index.row(), HIGH_COUNT).setText(num)
                            item(index.row(), HIGH_COUNT).setToolTip(num)
            elif (data1_new and not data2_new) or (data2_new and not data1_new):
                self.wrong_meta_format()
                return  # different formats metadata - not supported
            else:  # old format metadata
                for data in datas:
                    total = data.get("doc_pages", data.get("stats", {}).get("pages", 0))
                    items.append([data["highlight"], data["bookmarks"], total])
                self.merge_old_highs(items)
                if data1["highlight"]:  # update row data for books
                    num = str(len(data1["highlight"]))
                    for index in [idx1, idx2]:
                        if index:
                            item(index.row(), TITLE).setIcon(self.ico_label_green)
                            item(index.row(), HIGH_COUNT).setText(num)
                            item(index.row(), HIGH_COUNT).setToolTip(num)

        if sync:  # sync position and percent
            to_process = [{"data": data1, "path": path1}, {"data": data2, "path": path2}]
            percent = self.sync_pos(to_process)
            for index in [idx1, idx2]:
                if index:
                    item(index.row(), PERCENT).setText(percent)
                    item(index.row(), PERCENT).setToolTip(percent)

        data1["annotations_externally_modified"] = True
        self.save_book_data(path1, data1)
        if to_archived:  # update the db item
            self.update_book2db(data2)
        elif filename:  # do nothing with the loaded file
            pass
        else:  # update the second item
            data2["annotations_externally_modified"] = True
            self.save_book_data(path2, data2)

        self.reload_highlights = True

    def merge_new_highs(self, items):
        """ Merge the highlights of multiple books [new format]

        :type items: [[dict, int], ...]
        :param items: [[annotations, total_pg], ...]
        :param items: The list of books to be processed
        """
        uni_check_hi = set()
        uni_highs = []
        uni_check_bkm = set()
        uni_bkms = []
        for book_id, info in enumerate(items):  # find all unique highlights
            source = info[0]                    # that are not in all books
            for target_id, target in enumerate(items):
                if target_id == book_id:
                    continue  # don't check self
                target = target[0]
                for src_hi in source.values():
                    src_pos0 = src_hi.get("pos0")
                    if src_pos0:  # a highlight
                        for trg_hi in target.values():
                            trg_pos0 = trg_hi.get("pos0")
                            if trg_pos0:  # a highlight not a bookmark
                                if src_pos0 == trg_pos0:
                                    if src_hi["pos1"] == trg_hi["pos1"]:  # same highlight
                                        src_dt = (src_hi.get("datetime_updated")
                                                  or src_hi.get("datetime"))
                                        trg_dt = (trg_hi.get("datetime_updated")
                                                  or trg_hi.get("datetime"))
                                        if src_dt == trg_dt:
                                            break  # it's the exact same annotation
                                        if src_dt > trg_dt:  # sync src_hi to trg_hi
                                            self.sync_hi_data(src_hi, trg_hi)
                                            trg_hi["datetime_updated"] = src_dt
                                        else:  # sync trg_hi to src_hi
                                            self.sync_hi_data(trg_hi, src_hi)
                                            src_hi["datetime_updated"] = trg_dt
                                        break  # highlight found in target book
                        else:  # highlight was not found in target book
                            if src_hi["pos0"] + src_hi["pos1"] not in uni_check_hi:
                                uni_check_hi.add(src_hi["pos0"] + src_hi["pos1"])
                                uni_highs.append((src_hi, info[1]))
                    else:  # a bookmark
                        if src_hi["page"] not in uni_check_bkm:
                            uni_check_bkm.add(src_hi["page"])
                            uni_bkms.append((src_hi, info[1]))

        for info in items:  # update the annotations with the unique found ones
            annots = deepcopy([i for i in info[0].values()])
            total = info[1]
            hi_pos_check = {i["pos0"] + i["pos1"] for i in annots if i.get("pos0")}
            bkm_pos_check = {i["page"] for i in annots if i.get("page")}
            for hi_info in uni_highs:
                hi, hi_total = hi_info
                if not hi["pos0"] + hi["pos1"] in hi_pos_check:  # new highlight
                    new_hi = deepcopy(hi)
                    if hi_total != total:  # re-calculate the page numbers
                        percent = int(new_hi["pageno"]) / hi_total
                        new_hi["pageno"] = int(round(percent * total))
                    annots.append(new_hi)
            for bkm_info in uni_bkms:
                bkm, bkm_total = bkm_info
                if not bkm["page"] in bkm_pos_check:  # new bookmark
                    new_bkm = deepcopy(bkm)
                    if bkm_total != total:  # re-calculate the page numbers
                        percent = new_bkm["pageno"] / bkm_total
                        new_bkm["pageno"] = int(round(percent * total))
            info[0].clear()  # repopulate the annotations
            annots_upd = {}
            for i, hi in enumerate(sorted(annots, key=lambda x: int(x["pageno"]))):
                annots_upd[i + 1] = hi
            info[0].update(annots_upd)

    @staticmethod
    def sync_hi_data(hi1, hi2):
        """ Sync the highlight data from hi1 to hi2

        :type hi1: dict
        :type hi2: dict
        :param hi1: 1st highlight data
        :param hi2: 2nd highlight data
        """
        for key in ["note", "color", "drawer"]:
            hi2[key] = hi1.get(key)
            if hi2[key] is None:    # if no hi1 value
                hi2.pop(key, None)  # remove hi2 value too

    @staticmethod
    def merge_old_highs(items):
        """ Merge the highlights of multiple books

        :type items: [[dict, dict, int], ...]
        :param items: [[highlights, bookmarks, total_pg], ...]
        :param items: The list of books to be processed
        """
        uni_check = set()
        all_uni_highs = {}
        all_uni_bkms = {}
        # Collect the highlights that are missing even from one book
        for book_id, s_info in enumerate(items):
            source = s_info[0]
            uni_highs = defaultdict(dict)
            uni_bkms = defaultdict(dict)
            for target_id, t_info in enumerate(items):
                if target_id == book_id:
                    continue  # don't check self
                target = t_info[0]
                for src_pg in source:
                    for src_pg_id in source[src_pg]:
                        high = source[src_pg][src_pg_id]
                        src_text = high["text"]
                        for target_pg in target:
                            for target_pg_id in target[target_pg]:
                                targ = target[target_pg][target_pg_id]
                                if src_text == targ["text"]:  # same annotation
                                    if high["datetime"] == targ["datetime"]:
                                        break
                                    src_comm = ""  # if one comment is newer then the
                                    trg_comm = ""  # other, we keep the newer for both
                                    src_bkm = {}
                                    trg_bkm = {}
                                    for bk_idx in s_info[1]:
                                        src_bkm = s_info[1][bk_idx]
                                        if src_bkm["notes"] == src_text:
                                            src_comm = src_bkm.get("text", "")
                                            break
                                    for bk_idx in t_info[1]:
                                        trg_bkm = t_info[1][bk_idx]
                                        if trg_bkm["notes"] == targ["text"]:
                                            trg_comm = trg_bkm.get("text", "")
                                            break
                                    if src_bkm["datetime"] > trg_bkm["datetime"]:
                                        if src_comm:  # this is the newer comment
                                            trg_bkm["text"] = src_comm
                                        elif trg_comm:  # the comment was erased lately
                                            trg_bkm.pop("text", None)
                                        trg_bkm["datetime"] = src_bkm["datetime"]
                                        targ["datetime"] = high["datetime"]
                                    else:
                                        if trg_comm:  # this is the newer comment
                                            src_bkm["text"] = trg_comm
                                        elif src_comm:  # the comment was erased lately
                                            src_bkm.pop("text", None)
                                        src_bkm["datetime"] = trg_bkm["datetime"]
                                        high["datetime"] = targ["datetime"]
                                    break  # highlight found in target book
                            else:  # highlight was not found yet in target book
                                continue  # no break in the inner loop, keep checking
                            break  # highlight exists in target (there was a break)
                        else:  # text not in the target book highlights, add to unique
                            # but not if already added
                            if high["pos0"] + high["pos1"] not in uni_check:
                                uni_check.add(high["pos0"] + high["pos1"])
                                uni_highs[src_pg][src_pg_id] = high
            for pg in uni_highs:
                for pg_id in uni_highs[pg]:
                    text = uni_highs[pg][pg_id]["text"]
                    for bkm_idx in s_info[1]:  # get the associated bookmarks
                        if text == s_info[1][bkm_idx]["notes"]:
                            uni_bkms[pg][pg_id] = s_info[1][bkm_idx]
                            break
            if uni_highs:
                all_uni_highs[book_id] = dict(uni_highs)
                all_uni_bkms[book_id] = dict(uni_bkms)

        # Merge the highlights that are not on all books
        for book_id in all_uni_highs:
            uni_highs = all_uni_highs[book_id]
            uni_bkms = all_uni_bkms[book_id]
            source_total = items[book_id][2]
            for item_id, target_item in enumerate(items):
                target_total = target_item[2]
                recalculate = source_total != target_total
                all_highs = [target_item[0][pg][pg_id]
                             for pg in target_item[0] for pg_id in target_item[0][pg]]
                all_bkms = [i for i in target_item[1].values()]
                renumber = False  # no change made to the highlights/bookmarks
                for pg in uni_highs:
                    new_pg = pg
                    for pg_id in uni_highs[pg]:
                        if uni_highs[pg][pg_id] not in all_highs:  # add this highlight
                            renumber = True  # mark for renumbering the bookmarks
                            if recalculate:  # diff total pages, recalculate page number
                                percent = int(pg) / target_total
                                new_pg = int(round(percent * source_total))

                            if new_pg in target_item[0]:  # sort same page highlights
                                contents = target_item[0][new_pg]
                                contents = [contents[i] for i in contents]
                                extras = uni_highs[pg]
                                extras = [extras[i] for i in extras
                                          if extras[i] not in contents]
                                highs = sorted(contents + extras, key=lambda x: x["pos0"])
                                target_item[0][new_pg] = {i + 1: h
                                                          for i, h in enumerate(highs)}
                            else:  # single highlight in page, just add it
                                target_item[0][new_pg] = uni_highs[pg]
                            all_bkms.append(uni_bkms[pg][pg_id])
                if renumber:  # bookmarks added, so we must merge all and renumber them
                    bkm_list = target_item[1].copy()
                    bkm_list = [bkm_list[i] for i in bkm_list]
                    bkm_check = {i["pos0"] + i["pos1"] for i in bkm_list}
                    for bkm in all_bkms:
                        if bkm["pos0"] + bkm["pos1"] not in bkm_check:
                            bkm_list.append(bkm)
                    bkm_list = sorted(bkm_list, key=lambda x: x["page"])
                    target_item[1].clear()
                    offset = 1
                    for bkm in bkm_list:
                        target_item[1][offset] = bkm
                        offset += 1

    @staticmethod
    def sync_pos(to_process):
        """ Sync the reading position of multiple books

        :type to_process: list
        :param to_process: The list of books to be processed
        """
        percents = [i["data"]["percent_finished"] for i in to_process
                    if i and i.get("data", {}).get("percent_finished", 0) > 0]
        max_idx = percents.index(max(percents))
        max_percent = percents[max_idx]
        max_pointer = to_process[max_idx]["data"]["last_xpointer"]

        for item in to_process:
            item["data"]["percent_finished"] = max_percent
            item["data"]["last_xpointer"] = max_pointer

        return str(int(max_percent * 100)) + "%"

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
        for idx, title in [(DEL_META, _("Selected books' info")),
                           (DEL_BOOKS, _("Selected books")),
                           (DEL_MISSING, _("All missing books' info"))]:
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

    def delete_actions(self, idx=DEL_META):
        """ Execute the selected `Delete action`

        :type idx: int
        :param idx: The action type
        """
        if not self.db_mode:  # Loaded mode
            if not self.sel_indexes and idx in [DEL_META, DEL_BOOKS]:
                return
            text = ""
            if idx == DEL_META:
                text = _("This will delete the selected books' information\n"
                         "but will keep the equivalent books.")
            elif idx == DEL_BOOKS:
                text = _("This will delete the selected books and their information.")
            elif idx == DEL_MISSING:
                text = _("This will delete all the books' information "
                         "that refers to missing books.")
            popup = self.popup(_("Warning!"), text, buttons=2)
            if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
                return

            if idx == DEL_META:  # delete selected books' info
                self.remove_sel_books()
            elif idx == DEL_BOOKS:  # delete selected books
                self.remove_sel_books(delete=True)
            elif idx == DEL_MISSING:  # delete all missing books info
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
        """ Remove the selected book entries

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

    def remove_book_items(self):
        """ Remove the selected book entries from the file_table
        """
        if self.db_mode:
            self.delete_actions()
        else:
            for index in sorted(self.sel_indexes)[::-1]:
                self.remove_book_row(index.row())  # remove file_table entry

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

    def create_export_menu(self):
        """ Creates the `Export Files` button menu
        """
        self.export_menu.clear()
        single = len(self.sel_indexes) == 1
        if single:
            for idx, item in enumerate([(_("To text file"), MANY_TEXT),
                                        (_("To html file"), MANY_HTML),
                                        (_("To csv file"), MANY_CSV),
                                        (_("To md file"), MANY_MD)]):
                action = QAction(item[0], self.export_menu)
                action.triggered.connect(self.export_actions)
                action.setData(item[1])
                action.setIcon(self.ico_file_save)
                self.export_menu.addAction(action)
        else:
            for idx, item in enumerate([(_("To individual text files"), MANY_TEXT),
                                        (_("Combined to one text file"), ONE_TEXT),
                                        (_("To individual html files"), MANY_HTML),
                                        (_("Combined to one html file"), ONE_HTML),
                                        (_("To individual csv files"), MANY_CSV),
                                        (_("Combined to one csv file"), ONE_CSV),
                                        (_("To individual md files"), MANY_MD),
                                        (_("Combined to one md file"), ONE_MD)]):
                action = QAction(item[0], self.export_menu)
                action.triggered.connect(self.export_actions)
                action.setData(item[1])
                action.setIcon(self.ico_file_save)
                if idx and (idx % 2 == 0):
                    self.export_menu.addSeparator()
                self.export_menu.addAction(action)

    # noinspection PyCallByClass
    def on_export(self):
        """ Export the selected highlights to file(s)
        """
        if self.current_view == BOOKS_VIEW:
            if not self.sel_indexes:
                return
            self.toolbar.export_btn.showMenu()
        elif self.current_view == HIGHLIGHTS_VIEW:  # Save from high_table,
            if self.save_sel_highlights():          # combine to one file
                self.popup(_("Finished!"),
                           _("The Highlights were exported successfully!"),
                           icon=QMessageBox.Information)

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
        space = (" " if self.prefs.show_page_chk.isChecked() and
                 self.prefs.show_date_chk.isChecked() else "")
        if idx not in [MANY_MD, ONE_MD]:
            line_break = (":" + os.linesep if self.prefs.show_page_chk.isChecked() or
                          self.prefs.show_date_chk.isChecked() else "")
        else:
            line_break = (":*  " + os.linesep if self.prefs.show_page_chk.isChecked() or
                          self.prefs.show_date_chk.isChecked() else " ")
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
                                                   self.last_dir, f"*.{ext}")[0]
            if not filename:
                return
            self.last_dir = dirname(filename)
            saved = self.save_merged_file(filename, idx, line_break, space)

        self.status.animation(False)
        all_files = len(self.sel_indexes)
        self.popup(_("Finished!"),
                   _("{} texts were exported from {} processed.\n{} files with no "
                     "highlights.").format(saved, all_files, all_files - saved),
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
        count = 0
        for idx in self.sel_indexes:
            authors, title, highlights = self.get_item_data(idx, format_)
            if not highlights:  # no highlights in book
                continue
            highlights = sorted(highlights, key=self.sort_high4write)
            template = {"active": self.custom_template, "templ_head": self.templ_head,
                        "templ_body": self.templ_body,
                        "split_chapters": self.split_chapters,
                        "head_min": self.head_min, "head_max": self.head_max}
            try:
                args = {"title": title, "authors": authors, "highlights": highlights,
                        "dir_path": dir_path, "format_": format_, "space": space,
                        "line_break": line_break, "custom_template": template}
                save_file(args)
                count += 1
            except IOError as err:  # any problem when writing (like long filename, etc.)
                self.popup(_("Warning!"),
                           _("Could not save the file to disk!\n{}").format(err))
        return count

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
        count = 0
        text = (HTML_HEAD if format_ == ONE_HTML
                else CSV_HEAD if format_ == ONE_CSV else "")
        encoding = "utf-8-sig" if ONE_CSV else "utf-8"

        for idx in sorted(self.sel_indexes):
            authors, title, highlights = self.get_item_data(idx, format_)
            if not highlights:  # no highlights
                continue
            highlights = sorted(highlights, key=self.sort_high4write)
            template = {"active": self.custom_template, "templ_head": self.templ_head,
                        "templ_body": self.templ_body,
                        "split_chapters": self.split_chapters,
                        "head_min": self.head_min, "head_max": self.head_max}
            args = {"title": title, "authors": authors, "highlights": highlights,
                    "format_": format_, "line_break": line_break, "space": space,
                    "text": text, "custom_template": template}
            text = get_book_text(args)
            count += 1
        if format_ == ONE_HTML:
            text += "\n</body>\n</html>"

        with open(filename, "w+", encoding=encoding, newline="") as text_file:
            text_file.write(text)
        return count

    def get_item_data(self, index, format_):
        """ Get the highlight data for an item

        :type index: QModelIndex
        :param index: The item's index
        :type format_: int
        :param format_: The output format idx
        """
        row = index.row()
        data = self.file_table.item(row, 0).data(Qt.UserRole)
        args = {"page": self.prefs.show_page_chk.isChecked(),
                "date": self.prefs.show_date_chk.isChecked(),
                "text": self.prefs.show_high_chk.isChecked(),
                "chapter": self.prefs.show_chap_chk.isChecked(),
                "comment": self.prefs.show_comm_chk.isChecked(),
                "ref_pg": self.show_ref_pg,
                "html": format_ in [ONE_HTML, MANY_HTML],
                "csv": format_ in [ONE_CSV, MANY_CSV],
                "custom_md": self.custom_template,
                }
        highlights = self.get_formatted_highlights(data, args)
        title = self.file_table.item(row, TITLE).data(0)
        authors = self.file_table.item(row, AUTHOR).data(0)
        if authors in [OLD_TYPE, NO_AUTHOR]:
            authors = ""
        authors.replace("\\\n", ", ")
        return authors, title, highlights

    def get_formatted_highlights(self, data, args):
        """ Get the highlight texts for an item

        :type data: dict
        :param data: The item's data
        :type args: dict
        :param args: The arguments for the highlight texts
        """
        if not data:  # no highlights
            return []
        highlights = []
        annotations = data.get("annotations")
        if annotations:  # new format metadata
            for idx in annotations:
                highlight = self.get_new_highlight_info(data, idx)
                if highlight:
                    if not args["ref_pg"]:
                        highlight["page"] = str(highlight["page"])
                    else:
                        highlight["page"] = str(highlight.get("ref_page", "")
                                                or highlight["page"])
                    if self.date_format != DATE_FORMAT:
                        highlight["date"] = self.get_date_text(highlight["date"])
                    formatted_high = self.get_formatted_high(highlight, args)
                    highlights.append(formatted_high)
        else:  # old format metadata
            try:
                for page in data["highlight"]:
                    for page_id in data["highlight"][page]:
                        highlight = self.get_old_highlight_info(data, page, page_id)
                        if highlight:
                            highlights.append(self.get_formatted_high(highlight, args))
            except KeyError:  # no highlights
                pass
        return highlights

    @staticmethod
    def get_formatted_high(highlight, args):
        """ Create the highlight's texts

        :type highlight: dict
        :param highlight: The highlight's data
        :type args: dict
        :param args: The arguments for the highlight texts
        """
        line_break = "<br/>" if args["html"] else os.linesep
        chapter = (highlight["chapter"].replace("\n", line_break)
                   if args["chapter"] else "")
        high_text = highlight["text"].replace("\n", line_break) if args["text"] else ""
        comment = highlight["comment"].replace("\n", line_break)
        date = highlight["date"]
        line_break2 = os.linesep if args["text"] and comment else ""
        if args["csv"]:
            page_text = highlight["page"] if args["page"] else ""
            date_text = date if args["date"] else ""
            high_comment = comment if args["comment"] and comment else ""
        elif args["custom_md"]:
            page_text = str(highlight["page"]) if args["page"] else ""
            date_text = date if args["date"] else ""
            high_comment = (comment if args["comment"] and comment else "")
        else:
            page_text = "Page " + str(highlight["page"]) if args["page"] else ""
            date_text = "[" + date + "]" if args["date"] else ""
            high_comment = (line_break2 + "● " + comment
                            if args["comment"] and comment else "")
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
        if not filename[0]:
            return
        filename, extra = filename
        self.last_dir = dirname(filename)

        text_out = extra.startswith("text")
        html_out = extra.startswith("html")
        csv_out = extra.startswith("csv")
        md_out = extra.startswith("markdown")
        text = HTML_HEAD if html_out else CSV_HEAD if csv_out else ""
        encoding = "utf-8-sig" if csv_out else "utf-8"
        def_date_format = self.date_format == DATE_FORMAT

        for i in sorted(self.sel_high_view):
            row = i.row()
            data = self.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)

            if not def_date_format:
                data["date"] = self.get_date_text(data["date"])

            comment = "\n● " + data["comment"] if data["comment"] else ""
            authors = data["authors"].replace("\\\n", ", ")

            if data["new"] and self.show_ref_pg and data.get("ref_page"):
                page = data["ref_page"]
            else:
                page = data["page"]

            if text_out:
                hi_txt = (f"{data['title']} [{authors}]\nPage {page} [{data['date']}]\n"
                          f"[{data['chapter']}]\n{data['text']}{comment}")
                text += hi_txt + "\n\n"
            elif html_out:
                left = f"{data['title']} [{authors}]"
                right = f"Page {page} [{data['date']}]"
                text += HIGH_BLOCK % {"page": left, "date": right, "comment": comment,
                                      "highlight": data["text"],
                                      "chapter": data["chapter"]}
                text += "</div>\n"
            elif csv_out:
                csv_data = data.copy()
                csv_data["page"] = str(page)
                csv_data["authors"] = authors
                text += get_csv_row(csv_data) + "\n"
            elif md_out:
                hi_txt = data["text"].replace("\n", "  \n")
                chapter = data["chapter"]
                date_txt = data["date"].replace("-", "\\-")
                if not self.custom_template:
                    comment = comment.replace("\n", "  \n")
                    if chapter:
                        chapter = f"***{chapter}***\n\n".replace("\n", "  \n")
                    text += (f'\n---\n### {data["title"]} [{authors}]  \n'
                             f'*Page {page} [{date_txt}]*  \n'
                             f'{chapter}{hi_txt}{comment}\n')
                else:
                    comment = data["comment"].replace("\n", "  \n")
                    text += MD_HEAD.format(data["title"], authors)
                    text += MD_HIGH.format(date_txt, comment, hi_txt, page, chapter)
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
        """ Loads the json based configuration settings
        """
        if app_config:
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

            self.custom_template = app_config.get("custom_template", False)
            self.templ_head = app_config.get("templ_head", MD_HEAD)
            self.templ_body = app_config.get("templ_body", MD_HIGH)
            self.split_chapters = app_config.get("split_chapters", False)
            self.head_min = app_config.get("head_min", 2)
            self.head_max = app_config.get("head_max", 6)

            self.date_format = app_config.get("date_format", DATE_FORMAT)
            self.theme = app_config.get("theme", THEME_NONE_OLD)
            self.archive_warning = app_config.get("archive_warning", True)
            self.exit_msg = app_config.get("exit_msg", True)
            self.high_merge_warning = app_config.get("high_merge_warning", True)
            self.edit_lua_file_warning = app_config.get("edit_lua_file_warning", True)

            self.show_items = app_config.get("show_items", [True, True, True, True, True])
            if len(self.show_items) != 5:  # settings from older versions
                self.show_items = [True, True, True, True, True]
            for idx, chk in enumerate(self.prefs.show_items):
                self.blocked_change(chk, self.show_items[idx])
            self.high_by_page = app_config.get("high_by_page", False)
            self.show_ref_pg = app_config.get("show_ref_pg", True)
            self.blocked_change(self.prefs.show_ref_pg_chk, self.show_ref_pg)
        if self.highlight_width:
            self.header_high_view.resizeSection(HIGHLIGHT_H, self.highlight_width)
        if self.comment_width:
            self.header_high_view.resizeSection(COMMENT_H, self.comment_width)
        self.prefs.theme_box.setCurrentIndex(self.theme)
        self.blocked_change(self.prefs.alt_title_sort_chk, self.alt_title_sort)
        self.blocked_change(self.prefs.custom_template_chk, self.custom_template)
        self.prefs.edit_template.body_edit_txt.setText(self.templ_body)
        self.prefs.edit_template.head_edit_txt.setText(self.templ_head)
        self.prefs.edit_template.split_chapters_chk.setChecked(self.split_chapters)
        self.prefs.edit_template.head_min_box.setCurrentIndex(self.head_min - 1)
        self.prefs.edit_template.head_max_box.setCurrentIndex(self.head_max - 1)
        self.toolbar.set_btn_size(self.toolbar_size)

    def restore_windows(self):
        """ Restores the windows layout after the main window is build
        """
        self.restoreGeometry(self.unpickle("geometry"))
        # self.restoreState(self.unpickle("state"))  # 2fix makes window wider (if small)
        self.splitter.restoreState(self.unpickle("splitter"))
        self.header_main.restoreState(self.unpickle("header_main"))
        self.header_high_view.restoreState(self.unpickle("header_high_view"))
        self.filter.restoreGeometry(self.unpickle("filter_geometry"))
        self.prefs.restoreGeometry(self.unpickle("prefs_geometry"))
        self.prefs.edit_template.restoreGeometry(self.unpickle("templ_geometry"))
        self.prefs.edit_template.splitter.restoreState(self.unpickle("templ_split"))
        self.prefs.edit_template.head_split.restoreState(
            self.unpickle("templ_head_split"))
        self.prefs.edit_template.body_split.restoreState(
            self.unpickle("templ_body_split"))
        self.about.restoreGeometry(self.unpickle("about_geometry"))
        QTimer.singleShot(200, self.get_header_width)

    def get_header_width(self):
        """ Checks if the header width is smaller than the table
        """
        width = 0
        for i in range(self.header_main.count()):
            width += self.header_main.sectionSize(i)
        self.resize_columns = width < self.file_table.width()

    def settings_save(self):
        """ Saves the json based configuration settings
        """
        config = {"geometry": self.pickle(self.saveGeometry()),
                  "state": self.pickle(self.saveState()),
                  "splitter": self.pickle(self.splitter.saveState()),
                  "header_main": self.pickle(self.header_main.saveState()),
                  "header_high_view": self.pickle(self.header_high_view.saveState()),
                  "filter_geometry": self.pickle(self.filter.saveGeometry()),
                  "about_geometry": self.pickle(self.about.saveGeometry()),

                  "prefs_geometry": self.pickle(self.prefs.saveGeometry()),
                  "templ_geometry": self.pickle(self.prefs.edit_template.saveGeometry()),
                  "templ_split": self.pickle(
                      self.prefs.edit_template.splitter.saveState()),
                  "templ_head_split": self.pickle(
                      self.prefs.edit_template.head_split.saveState()),
                  "templ_body_split": self.pickle(
                      self.prefs.edit_template.body_split.saveState()),
                  "templ_head": self.templ_head, "templ_body": self.templ_body,
                  "custom_template": self.custom_template,
                  "split_chapters": self.split_chapters,
                  "head_min": self.head_min, "head_max": self.head_max,
                  "col_sort_asc": self.col_sort_asc, "col_sort": self.col_sort,
                  "col_sort_asc_h": self.col_sort_asc_h, "col_sort_h": self.col_sort_h,
                  "highlight_width": self.highlight_width, "db_path": self.db_path,
                  "comment_width": self.comment_width, "toolbar_size": self.toolbar_size,
                  "last_dir": self.last_dir, "alt_title_sort": self.alt_title_sort,
                  "archive_warning": self.archive_warning, "exit_msg": self.exit_msg,
                  "current_view": self.current_view, "db_mode": self.db_mode,
                  "high_by_page": self.high_by_page, "show_ref_pg": self.show_ref_pg,
                  "date_vacuumed": self.date_vacuumed,
                  "show_info": self.fold_btn.isChecked(), "date_format": self.date_format,
                  "theme": self.theme, "show_items": self.show_items,
                  "skip_version": self.skip_version, "opened_times": self.opened_times,
                  "edit_lua_file_warning": self.edit_lua_file_warning,
                  "high_merge_warning": self.high_merge_warning,
                  }
        try:
            for k, v in config.items():

                if isinstance(v, bytes):
                    try:
                        config[k] = v.decode("latin1")
                    except UnicodeDecodeError as e:
                        print("Error decoding bytes to string: {}".format(e))
                        config[k] = v.decode("latin1", errors="ignore")
            config_json = json.dumps(config, sort_keys=True, indent=4)
            with gzip.GzipFile(join(SETTINGS_DIR, str("settings.json.gz")),
                               "w+") as gz_file:
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

        :type key: str
        :parameter key: The dict key to be un-pickled
        """
        try:
            value = app_config.get(key)
            if not value:
                return
            value = value.encode("latin1")
            # noinspection PyTypeChecker,PyArgumentList
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
        if isinstance(icon, QMessageBox.Icon):
            popup.setIcon(icon)
        elif isinstance(icon, str):
            popup.setIconPixmap(QPixmap(icon))
        elif isinstance(icon, QPixmap):
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

        if QT6:  # QT6 requires exec() instead of exec_()
            popup.exec_ = getattr(popup, "exec")
        popup.exec_()
        return popup

    def error(self, error_txt):
        self.popup(_("Error!"), error_txt, icon=QMessageBox.Critical)

    def passed_files(self):
        """ Command line parameters that are passed to the program.
        """
        if len(sys.argv) > 1 and sys.argv[1].endswith("Portable.exe"):
            del sys.argv[1]
        if len(sys.argv) > 1:
            self.on_file_table_fileDropped(sys.argv[1:])

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
            self.popup(_("Error opening target!"), _(f'"{path}" does not exists!'))

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

    @staticmethod
    def blocked_change(widget, state):
        """ Check/Uncheck a switch or change index to a combo while blocking its signals

        :type widget: QWidget
        :param widget: The widget to change
        :type state: bool|int
        :param state: The new state we want
        """
        widget.blockSignals(True)
        if type(state) is bool:  # switch
            widget.setChecked(state)
        elif type(state) is int:  # combo
            widget.setCurrentIndex(state)
        widget.blockSignals(False)

    def auto_check4update(self):
        """ Checks online for an updated version
        """
        self.db_maintenance()

        self.opened_times += 1
        if self.opened_times == 20:
            text = _("Since you are using {} for some time now, perhaps you find it "
                     "useful enough to consider a donation.\nWould you like to visit the "
                     "PayPal donation page?\n\nThis is a one-time message. It will never "
                     "appear again!").format(APP_NAME)
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
        # current_version = LooseVersion(self.version)
        # skip_version = LooseVersion(self.skip_version)
        current_version = version_parse(self.version)
        skip_version = version_parse(self.skip_version)
        if version_new > current_version and version_new != skip_version:
            popup = self.popup(_("Newer version exists!"),
                               _("There is a newer version (v.{}) online.\n"
                                 "Open the site to download it now?").format(version_new),
                               icon=QMessageBox.Information, buttons=2,
                               check_text=_("Don't alert me for this version again"))
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
        except Exception:  # a problematic print that WE HAVE to ignore, or we LOOP
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


class KOHighlights(QApplication):

    def __init__(self, *args, **kwargs):
        super(KOHighlights, self).__init__(*args, **kwargs)
        if QT5:
            self.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        on_windows = sys.platform.lower().startswith("win")
        compiled = getattr(sys, 'frozen', False)
        # # hide console window, but only under Windows and only if app is frozen
        # if on_windows and compiled:
        #     self.hide_console()

        argv = self.arguments()
        if argv[0].endswith("python.exe") or argv[0].endswith("python3.exe"):
            argv = argv[1:]
        if len(argv) > 1 and argv[1] == "-p":
            del argv[1]
        sys.argv = argv
        self.parser = argparse.ArgumentParser(prog=APP_NAME,
                                              description=f"{APP_NAME} v{__version__} - "
                                                          f"A KOReader's "
                                                          f"highlights converter",
                                              epilog=f"Thank you for using {APP_NAME}!")
        self.base = Base()
        if compiled:  # the app is compiled
            if not on_windows:  # no cli in windows
                self.parse_args()
        else:
            self.parse_args()
        if QT6:  # QT6 requires exec() instead of exec_()
            self.exec_ = getattr(self, "exec")
        self.exec_()
        self.deleteLater()  # avoids some QThread messages in the shell on exit
        # self.show_console() if on_windows and compiled else None

    # ___ ___________________ GUI + CLI TESTING _____________________

    @staticmethod
    def hide_console():
        """ Hides the console window in GUI mode. Necessary for frozen application,
        because this application support both, command line processing AND GUI mode
        and therefore cannot be run via pythonw.exe.
        """
        import ctypes
        win_handles = ctypes.windll.kernel32.GetConsoleWindow()
        if win_handles != 0:
            ctypes.windll.user32.ShowWindow(win_handles, 0)
            # if you wanted to close the handles...
            # ctypes.windll.kernel32.CloseHandle(win_handles)

    @staticmethod
    def show_console():
        """ UnHides console window
        """
        import ctypes
        win_handles = ctypes.windll.kernel32.GetConsoleWindow()
        if win_handles != 0:
            ctypes.windll.user32.ShowWindow(win_handles, 1)

    @staticmethod
    def get_pid_info():
        """ Return a dictionary with keys the PID of all running processes.
        The values are dictionaries with the following key-value pairs:
            name: <Name of the process PID>
            parent_id: <PID of this process parent>
        """
        import win32pdh
        # get the names and occurrences of all running process names
        items, instances = win32pdh.EnumObjectItems(None, None, "Process",
                                                    win32pdh.PERF_DETAIL_WIZARD)
        instance_dict = {}
        for instance in instances:
            instance_dict[instance] = instance_dict.get(instance, 0) + 1
        counter_items = ["ID Process", "Creating Process ID"]  # define the info to obtain

        pid_dict = {}
        # loop over each program (multiple instances might be running)
        for instance, max_instances in instance_dict.items():
            for i_num in range(max_instances):
                hq = win32pdh.OpenQuery()  # define the counters for the query
                hcs = {}
                for item in counter_items:
                    path = win32pdh.MakeCounterPath((None, "Process", instance,
                                                     None, i_num, item))
                    hcs[item] = win32pdh.AddCounter(hq, path)
                win32pdh.CollectQueryData(hq)

                hc_dict = {}  # store the values in a temporary dict
                for item, hc in hcs.items():
                    type_, val = win32pdh.GetFormattedCounterValue(hc,
                                                                   win32pdh.PDH_FMT_LONG)
                    hc_dict[item] = val
                    win32pdh.RemoveCounter(hc)
                win32pdh.CloseQuery(hq)

                # obtain the pid and ppid of the current instance and store it
                pid, pp_id = (hc_dict[item] for item in counter_items)
                pid_dict[pid] = {"name": instance, "parent_id": pp_id}
        return pid_dict

    def get_parent_info(self, pid):
        """ Returns a PID, Name tuple of the parent process

        :type pid: int
        :param pid: PID of the process to get the parent PID for
        :rtype: tuple(int, str)
        """
        pid_info = self.get_pid_info()
        pp_id = pid_info[pid]["parent_id"]
        pp_name = pid_info[pp_id]["name"]
        return pp_id, pp_name

    # ___ ___________________ CLI STUFF _____________________________

    def parse_args(self):
        """ Parse the command line parameters that are passed to the program.
        """
        self.parser.add_argument("-v", "--version", action="version",
                                 version=f"%(prog)s v{__version__}")

        self.parser.add_argument("paths", nargs="*",
                                 help="The paths to input files or folder")

        self.parser.add_argument("-x", "--use_cli", required="-o" in sys.argv,
                                 help="Use the command line interface only (exit the "
                                      "app after finishing)", action="store_true",
                                 default=False)
        self.parser.add_argument("-s", "--sort_page", action="store_true", default=False,
                                 help="Sort highlights by page, otherwise sort by date")
        self.parser.add_argument("-r", "--ref_page", action="store_true", default=True,
                                 help="Use reference page numbers if they exist")
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

        self.parser.add_argument("-p", "--portable", action="store_true", default=False,
                                 help="Just run the program in portable mode "
                                      "(Windows only)")

        # args, paths = self.parser.parse_known_args()
        args = self.parser.parse_args()
        if args.portable:
            print("Running in portable mode...")
        elif args.use_cli:
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
                self.parser.error(f"The output path (-o/--output) must be {ext} filename "
                                  f"not a directory!")
                return
            saved = self.cli_save_merged_file(args, files, line_break, space)

        all_files = len(files)
        sys.stdout.write(f"\n{saved} files were exported from the {all_files} processed"
                         f".\n{all_files - saved} files with no highlights.\n")

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
        path = abspath(args.output)
        for file_ in files:
            authors, title, highlights = self.cli_get_item_data(file_, args)
            if not highlights:  # no highlights
                continue
            highlights = sorted(highlights, key=partial(self.cli_sort, args))
            try:
                exp_args = {"title": title, "authors": authors, "highlights": highlights,
                            "dir_path": path, "format_": format_,
                            "line_break": line_break, "space": space}
                save_file(exp_args)
                saved += 1
            except IOError as err:  # any problem when writing (like long filename, etc.)
                sys.stdout.write(str(f"Could not save the file to disk!\n{err}"))
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
            exp_args = {"title": title, "authors": authors, "highlights": highlights,
                        "format_": format_, "line_break": line_break, "space": space,
                        "text": text}
            text = get_book_text(exp_args)
            saved += 1
        if args.html:
            text += "\n</body>\n</html>"
        path = abspath(args.output)
        name, ext = splitext(path)
        if ext.lower() != new_ext:
            path = name + new_ext
        with open(path, "w+", encoding=encoding, newline="") as text_file:
            text_file.write(text)
            sys.stdout.write(f"Created {path}\n\n")
        return saved

    def cli_get_item_data(self, file_, args):
        """ Get the highlight data for an item

        :type file_: str|unicode
        :param file_: The item's path
        :type args: argparse.Namespace
        :param args: The item's arguments
        """
        data = decode_data(file_)
        args_ = {"page": not args.no_page,
                 "date": not args.no_date,
                 "text": not args.no_highlight,
                 "chapter": not args.no_chapter,
                 "comment": not args.no_comment,
                 "ref_pg": args.ref_page,
                 "html": args.html,
                 "csv": args.csv,
                 "custom_md": False  # not used from cli
                 }
        highlights = self.base.get_formatted_highlights(data, args_)
        title, authors = self.base.get_title_authors(data, file_)
        return authors, title, highlights

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


if __name__ == "__main__":
    app = KOHighlights(sys.argv)
