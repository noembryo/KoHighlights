# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
from boot_config import *
import os, sys, re
import codecs
import gzip
import json
import shutil
import webbrowser
import subprocess
from datetime import datetime
from functools import partial
from collections import defaultdict
from distutils.version import LooseVersion
from os.path import (isdir, isfile, join, basename, splitext, dirname, split, exists,
                     getmtime)
from pprint import pprint

import mechanize  # ___ _______________ DEPENDENCIES ________________
from slppu import slppu as lua  # https://github.com/noembryo/slppu
from bs4 import BeautifulSoup
from PySide.QtCore import (Qt, QTimer, Slot, QObject, Signal, QThread, QMimeData,
                           QModelIndex)
from PySide.QtGui import (QMainWindow, QApplication, QMessageBox, QIcon, QFileDialog,
                          QTableWidgetItem, QTextCursor, QDialog, QWidget, QMovie, QFont,
                          QMenu, QAction, QTableWidget, QCheckBox, QHeaderView, QCursor,
                          QListWidgetItem, QPixmap, QToolButton, QActionGroup)

from gui_main import Ui_Base  # ___ ______ GUI STUFF ________________
from gui_about import Ui_About
from gui_auto_info import Ui_AutoInfo
from gui_toolbar import Ui_ToolBar
from gui_status import Ui_Status
from gui_edit import Ui_TextDialog

try:  # ___ _______ PYTHON 2/3 COMPATIBILITY ________________________
    import cPickle as pickle
except ImportError:  # python 3.x
    import pickle
from future.moves.urllib.request import Request, URLError


__author__ = "noEmbryo"
__version__ = "0.7.0.0"


def _(text):
    return text


# noinspection PyCallByClass
class Base(QMainWindow, Ui_Base):
    def __init__(self, parent=None):
        super(Base, self).__init__(parent)
        self.scan_thread = QThread()
        self.highlight_scan_thread = QThread()
        self.setupUi(self)
        self.version = __version__
        self.file_selection = None
        self.sel_idx = None
        self.sel_indexes = []
        self.highlights_selection = None
        self.sel_highlights = []
        self.sel_book_data = {}
        self.high_view_selection = None
        self.sel_high_view = []
        self.col_sort = MODIFIED
        self.col_sort_asc = False
        self.col_sort_h = DATE_H
        self.col_sort_asc_h = False
        self.highlight_width = None
        self.comment_width = None
        self.loaded_paths = set()

        self.skip_version = "0.0.0.0"
        self.opened_times = 0
        self.last_dir = os.getcwd()
        self.edit_lua_file_warning = True
        self.high_merge_warning = True
        self.current_view = 0
        self.high_by_page = False
        self.exit_msg = True

        self.file_table.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.header_main = self.file_table.horizontalHeader()
        self.header_main.setMovable(True)
        self.header_main.setDefaultAlignment(Qt.AlignLeft)

        self.highlight_table.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.header_high_view = self.highlight_table.horizontalHeader()
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
        self.ico_empty = QIcon(":/stuff/trans32.png")

        self.about = About(self)
        self.auto_info = AutoInfo(self)

        self.toolbar = ToolBar(self)
        self.tool_bar.addWidget(self.toolbar)
        self.toolbar.merge_btn.setEnabled(False)

        self.status = Status(self)
        self.statusbar.addPermanentWidget(self.status)

        self.edit_high = TextDialog(self)
        self.edit_high.on_ok = self.edit_highlight_ok
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

        # noinspection PyTypeChecker
        QTimer.singleShot(0, self.on_load)

        # noinspection PyTypeChecker
        QTimer.singleShot(30000, self.auto_check4update)  # check for updates

        # self.threads4process = []
        # thread_cleanup_timer = QTimer(self)  # cleanup threads for ever
        # thread_cleanup_timer.timeout.connect(self.thread_cleanup)
        # thread_cleanup_timer.start(2000)

    def on_load(self):
        """ Things that must be done after the initialization
        """
        self.settings_load()
        if FIRST_RUN:  # on first run
            self.splitter.setSizes((500, 250))
        self.toolbar.save_btn.setMenu(self.save_menu())  # assign/create menu
        self.toolbar.merge_btn.setMenu(self.merge_menu())  # assign/create menu
        self.toolbar.delete_btn.setMenu(self.delete_menu())  # assign/create menu
        self.connect_gui()
        self.show()
        self.passed_files()

    # ___ ___________________ EVENTS STUFF __________________________

    # noinspection PyUnresolvedReferences
    def connect_gui(self):
        """ Make all the signal/slots connections
        """
        self.file_selection = self.file_table.selectionModel()
        self.file_selection.selectionChanged.connect(self.file_selection_update)
        self.header_main.sectionClicked.connect(self.on_column_clicked)
        self.file_table.customContextMenuRequested.connect(self.on_item_right_clicked)
        self.highlights_selection = self.highlights_list.selectionModel()
        self.highlights_selection.selectionChanged.connect(
            self.highlights_selection_update)
        self.highlights_list.customContextMenuRequested.connect(
            self.on_highlight_right_clicked)

        self.high_view_selection = self.highlight_table.selectionModel()
        self.high_view_selection.selectionChanged.connect(self.high_view_selection_update)
        self.header_high_view.sectionClicked.connect(self.on_highlight_column_clicked)
        self.header_high_view.sectionResized.connect(self.on_highlight_column_resized)
        self.highlight_table.customContextMenuRequested.connect(
            self.on_high_view_right_clicked)

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
            if key == Qt.Key_D:
                print("control + D")
                return True
            if key == Qt.Key_Backspace:  # ctrl+Backspace
                self.toolbar.on_clear_btn_clicked()
                return True
            if key == Qt.Key_L:  # ctrl+L
                self.toolbar.on_select_btn_clicked()
                return True
            if key == Qt.Key_S:  # ctrl+S
                self.save_actions(0)
                return True
            if key == Qt.Key_O:  # ctrl+O
                self.toolbar.on_info_btn_clicked()
                return True
            if key == Qt.Key_Q:  # ctrl+Q
                self.close()

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

    # ___ ___________________ FILE TABLE STUFF ______________________

    @Slot(list)
    def on_file_table_fileDropped(self, dropped):
        """ When some items are dropped to the TableWidget

        :type dropped: list
        :param dropped: The items dropped
        """
        for i in dropped:
            if splitext(i)[1] == ".lua":
                self.create_row(i)
        folders = [j for j in dropped if isdir(j)]
        for folder in folders:
            self.scan_files_thread(folder)

    # @Slot(QTableWidgetItem)  # its called indirectly from self.file_selection_update
    def on_file_table_itemClicked(self, item, reset=True):
        """ When an item of the FileTable is clicked

        :type item: QTableWidgetItem
        :param item: The item (cell) that is clicked
        :type reset: bool
        :param reset: Select the first highlight in the list
        """
        row = item.row()
        data = self.file_table.item(row, TITLE).data(Qt.UserRole)
        self.sel_book_data = data

        if self.file_table.item(row, TYPE).data(Qt.UserRole)[1]:
            self.toolbar.open_btn.setEnabled(True)
        else:
            self.toolbar.open_btn.setEnabled(False)

        self.highlights_list.clear()

        extra = (" " if self.status.act_page.isChecked() and
                 self.status.act_date.isChecked() else "")
        line_break = (":\n" if self.status.act_page.isChecked() or
                      self.status.act_date.isChecked() else "")
        highlights = []
        for page in data["highlight"]:
            for page_id in data["highlight"][page]:
                try:
                    date = data["highlight"][page][page_id]["datetime"]
                    text = data["highlight"][page][page_id]["text"].replace("\\\n", "\n")
                    comment = ""
                    for idx in data["bookmarks"]:
                        if text == data["bookmarks"][idx]["notes"]:
                            book_text = data["bookmarks"][idx].get("text", "")
                            if not book_text:
                                break
                            book_text = re.sub(r"Page \d+ "
                                               r"(.+?) @ \d+-\d+-\d+ \d+:\d+:\d+", r"\1",
                                               book_text, 1, re.DOTALL | re.MULTILINE)
                            if text != book_text:
                                comment = book_text.replace("\\\n", "\n")
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
            high_comment = (line_break2 + "● " + comment
                            if self.status.act_comment.isChecked() and comment else "")
            highlight = (page_text + extra + date_text + line_break +
                         high_text + high_comment + "\n")

            highlight_item = QListWidgetItem(highlight, self.highlights_list)
            highlight_item.setData(Qt.UserRole, item)

        description_state = False
        if "doc_props" in self.sel_book_data and "description" in data["doc_props"]:
            description_state = bool(data["doc_props"]["description"])
        self.description_btn.setEnabled(description_state)

        self.populate_book_info(data, row)
        # self.highlights_list.sortItems()  # using XListWidgetItem for custom sorting
        self.highlights_list.setCurrentRow(0) if reset else None

    def populate_book_info(self, data, row):
        """ Fill in the `Book Info` fields

        :type data: dict
        :param data: The items data
        :type row: int
        :param row: The items row number
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
        description = self.sel_book_data["doc_props"]["description"]
        self.description.high_edit_txt.setHtml(description)
        self.description.show()

    # noinspection PyUnusedLocal
    def on_item_right_clicked(self, point):
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
            save_menu.setTitle(_("Save selected"))
            menu.addMenu(save_menu)
        else:  # only one item selected
            action = QAction(_("Save to text file"), menu)
            action.triggered.connect(self.on_save_actions)
            action.setData(0)
            action.setIcon(self.ico_file_save)
            menu.addAction(action)

        delete_menu = self.delete_menu()
        delete_menu.setIcon(self.ico_files_delete)
        delete_menu.setTitle(_("Delete\tDel"))
        menu.addMenu(delete_menu)

        # noinspection PyArgumentList
        menu.exec_(QCursor.pos())

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
            data = self.highlight_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
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
            pass
        # if self.file_selection.selectedRows():
        #     idx = selected.indexes()[0]
        if self.sel_indexes:
            item = self.file_table.item(self.sel_idx.row(), self.sel_idx.column())
            self.on_file_table_itemClicked(item)
        else:
            self.highlights_list.clear()
            self.description_btn.setEnabled(False)
            for field in self.info_fields:
                field.setText("")
        self.toolbar.merge_btn.setEnabled(self.check4merge())

    def on_column_clicked(self, column):
        """ Sets the current sorting column

        :type column: int
        :parameter column: The column where the filtering is applied
        """
        if column == self.col_sort:
            self.col_sort_asc = not self.col_sort_asc
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

    def scan_files_thread(self, path):
        """ Gets all the history files that are inside
        this path and its sub-directories

        :type path: str|unicode
        :param path: The root path
        """
        self.file_table.setSortingEnabled(False)  # need this before populating table

        scanner = Scanner(path)
        scanner.moveToThread(self.scan_thread)
        scanner.found.connect(self.create_row)
        scanner.finished.connect(self.scan_finished)
        scanner.finished.connect(self.scan_thread.quit)
        self.scan_thread.downer = scanner
        self.scan_thread.started.connect(scanner.process)
        self.scan_thread.start(QThread.IdlePriority)

        self.status.animation("start")

        self.auto_info.set_text(_("Scanning for KoReader metadata files.\n"
                                  "Please Wait..."))
        self.auto_info.show()

    def scan_finished(self):
        """ What will happen after the scanning for history files ends
        """
        self.status.animation("stop")
        self.auto_info.hide()
        self.file_table.resizeColumnsToContents()

        self.file_table.setSortingEnabled(True)  # re-enable it after populating table
        order = Qt.AscendingOrder if self.col_sort_asc else Qt.DescendingOrder
        self.file_table.sortByColumn(self.col_sort, order)

        if self.current_view == 1:  # highlights view
            self.scan_highlights_thread()

    def create_row(self, filename):
        """ Creates a table row from the given file

        :type filename: str|unicode
        :param filename: The file to be read
        """
        if exists(filename) and splitext(filename)[1].lower() == '.lua':
            if filename in self.loaded_paths:
                return  # already loaded file
            self.loaded_paths.add(filename)
            self.file_table.setSortingEnabled(False)
            self.file_table.insertRow(0)
            data = self.decode_data(filename)
            if not data:
                print("No data here!", filename)
                return
            icon, title, authors, percent = self.get_item_stats(filename, data)

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

            date = str(datetime.fromtimestamp(getmtime(filename)))
            date_item = QTableWidgetItem(date)
            date_item.setToolTip(date)
            self.file_table.setItem(0, MODIFIED, date_item)

            path_item = QTableWidgetItem(filename)
            path_item.setToolTip(filename)
            self.file_table.setItem(0, PATH, path_item)

            self.file_table.setSortingEnabled(True)

    def get_item_stats(self, filename, data):
        """ Returns the title and authors of a history file

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

    # ___ ___________________ HIGHLIGHT TABLE STUFF _________________

    @Slot(QTableWidgetItem)
    def on_highlight_table_itemClicked(self, item):
        """ When an item of the highlight_table is clicked

        :type item: QTableWidgetItem
        :param item: The item (cell) that is clicked
        """
        row = item.row()
        data = self.highlight_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)

        if isfile(data["path"]):
            self.toolbar.open_btn.setEnabled(True)
        else:
            self.toolbar.open_btn.setEnabled(False)

        # needed for edit "Comments" or "Find in Books" in Highlight View
        for row in range(self.file_table.rowCount()):  # 2check: need to optimize?
            if data["path"] == self.file_table.item(row, TYPE).data(Qt.UserRole)[0]:
                self.sel_book_data = self.file_table.item(row, TITLE).data(Qt.UserRole)
                break

    @Slot(QModelIndex)
    def on_highlight_table_doubleClicked(self, index):
        """ When an item of the highlight_table is double-clicked

        :type index: QTableWidgetItem
        :param index: The item (cell) that is clicked
        """
        column = index.column()
        if column == COMMENT_H:
            self.on_edit_highlight()

    # noinspection PyUnusedLocal
    def on_high_view_right_clicked(self, point):
        """ When an item of the highlight_table is right-clicked

        :type point: QPoint
        :param point: The point where the right-click happened
        """
        if not len(self.sel_high_view):  # no items selected
            return

        menu = QMenu(self.highlight_table)

        row = self.highlight_table.itemAt(point).row()
        self.act_view_book.setData(row)
        self.act_view_book.setEnabled(self.toolbar.open_btn.isEnabled())
        menu.addAction(self.act_view_book)

        highlights = ""
        comments = ""
        for idx in self.sel_high_view:
            item_row = idx.row()
            data = self.highlight_table.item(item_row, HIGHLIGHT_H).data(Qt.UserRole)
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

            action = QAction(_("Find in Books"), menu)
            action.triggered.connect(partial(self.find_in_books, highlights))
            action.setIcon(self.ico_view_books)
            menu.addAction(action)

            action = QAction(_("Comments"), menu)
            action.triggered.connect(self.on_edit_highlight)
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

        # delete_menu = self.delete_menu()
        # delete_menu.setIcon(self.ico_files_delete)
        # delete_menu.setTitle(_('Delete\tDel'))
        # menu.addMenu(delete_menu)

        # noinspection PyArgumentList
        menu.exec_(QCursor.pos())

    def scan_highlights_thread(self):
        """ Gets all the loaded highlights
        """
        self.highlight_table.model().removeRows(0, self.highlight_table.rowCount())
        self.highlight_table.setSortingEnabled(False)  # need this before populating table

        scanner = HighlightScanner()
        scanner.moveToThread(self.highlight_scan_thread)
        scanner.found.connect(self.create_highlight_row)
        scanner.finished.connect(self.scan_highlights_finished)
        scanner.finished.connect(self.highlight_scan_thread.quit)
        self.highlight_scan_thread.scanner = scanner
        self.highlight_scan_thread.started.connect(scanner.process)
        self.highlight_scan_thread.start(QThread.IdlePriority)

    def create_highlight_row(self, data):
        """ Creates a highlight table row from the given data

        :type data: dict
        :param data: The highlight data
        """
        self.highlight_table.setSortingEnabled(False)
        self.highlight_table.insertRow(0)

        item = QTableWidgetItem(data["text"])
        item.setToolTip("<p>{}</p>".format(data["text"]))
        item.setData(Qt.UserRole, data)
        self.highlight_table.setItem(0, HIGHLIGHT_H, item)

        comment = data["comment"]
        item = QTableWidgetItem(comment)
        if comment:
            item.setToolTip("<p>{}</p>".format(comment))
        self.highlight_table.setItem(0, COMMENT_H, item)

        item = QTableWidgetItem(data["date"])
        item.setToolTip(data["date"])
        item.setTextAlignment(Qt.AlignRight)
        self.highlight_table.setItem(0, DATE_H, item)

        item = QTableWidgetItem(data["title"])
        item.setToolTip(data["title"])
        self.highlight_table.setItem(0, TITLE_H, item)

        page = data["page"]
        item = XTableWidgetItem(page)
        item.setToolTip(page)
        item.setTextAlignment(Qt.AlignRight)
        item.setData(Qt.UserRole, int(page))
        self.highlight_table.setItem(0, PAGE_H, item)

        item = QTableWidgetItem(data["authors"])
        item.setToolTip(data["authors"])
        self.highlight_table.setItem(0, PATH, item)

        self.highlight_table.setSortingEnabled(True)

    def scan_highlights_finished(self):
        """ What will happen after the scanning for history files ends
        """
        for col in [PAGE_H, DATE_H, AUTHOR_H, TITLE_H]:
            self.highlight_table.resizeColumnToContents(col)

        self.highlight_table.setSortingEnabled(True)  # re-enable, after populating table
        order = Qt.AscendingOrder if self.col_sort_asc_h else Qt.DescendingOrder
        self.highlight_table.sortByColumn(self.col_sort_h, order)

    # noinspection PyUnusedLocal
    def high_view_selection_update(self, selected, deselected):
        """ When a row in highlight_table gets selected

        :type selected: QModelIndex
        :parameter selected: The selected row
        :type deselected: QModelIndex
        :parameter deselected: The deselected row
        """
        try:
            self.sel_high_view = self.high_view_selection.selectedRows()
        except IndexError:  # empty table
            pass

    def on_highlight_column_clicked(self, column):
        """ Sets the current sorting column

        :type column: int
        :parameter column: The column where the filtering is applied
        """
        if column == self.col_sort_h:
            self.col_sort_asc_h = not self.col_sort_asc_h
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
        data = self.sel_book_data
        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, TITLE)
            row_data = item.data(Qt.UserRole)
            if data["stats"]["title"] == row_data["stats"]["title"]:  # find the book row
                self.on_file_table_itemClicked(item)
                self.toolbar.books_btn.click()
                self.file_table.selectRow(row)
                for hi_row in range(self.highlights_list.count()):  # find the highlight
                    if (self.highlights_list.item(hi_row)
                            .data(Qt.UserRole)[HIGHLIGHT_TEXT] == highlight):
                        self.highlights_list.setCurrentRow(hi_row)
                        break
                break

    # ___ ___________________ HIGHLIGHTS LIST STUFF _________________

    # noinspection PyUnusedLocal
    def on_highlight_right_clicked(self, point):
        """ When a highlight is right-clicked

        :type point: QPoint
        :param point: The point where the right-click happened
        """
        if self.sel_highlights:
            menu = QMenu(self.highlights_list)

            action = QAction(_("Comments"), menu)
            action.triggered.connect(self.on_edit_highlight)
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

            # noinspection PyArgumentList
            menu.exec_(QCursor.pos())

    @Slot()
    def on_highlights_list_itemDoubleClicked(self):
        """ An item on the Highlight List is double-clicked
        """
        self.on_edit_highlight()

    def on_edit_highlight(self):
        """ Opens a window to edit the selected highlight's comment
        """
        if self.file_table.isVisible():  # edit comments from Book View
            row = self.sel_highlights[-1].row()
            comment = self.highlights_list.item(row).data(Qt.UserRole)[COMMENT]
        elif self.highlight_table.isVisible():  # edit comments from Highlights View
            row = self.sel_high_view[-1].row()
            high_data = self.highlight_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
            comment = high_data["comment"]
        else:
            return
        self.edit_high.high_edit_txt.setText(comment)
        # self.edit_high.high_edit_txt.setFocus()
        self.edit_high.exec_()

    def edit_highlight_ok(self):
        """ Change the selected highlight's comment
        """
        text = self.edit_high.high_edit_txt.toPlainText()
        if self.file_table.isVisible():
            high_index = self.sel_highlights[-1]
            high_row = high_index.row()
            high_data = self.highlights_list.item(high_row).data(Qt.UserRole)
            high_text = high_data[HIGHLIGHT_TEXT]

            row = self.sel_idx.row()
            data = self.file_table.item(row, TITLE).data(Qt.UserRole)

            for bookmark in data["bookmarks"].keys():
                if high_text == data["bookmarks"][bookmark]["notes"]:
                    data["bookmarks"][bookmark]["text"] = text.replace("\n", "\\\n")
                    break
            self.file_table.item(row, TITLE).setData(Qt.UserRole, data)
            path = self.file_table.item(row, PATH).text()
        elif self.highlight_table.isVisible():
            data = self.sel_book_data
            row = self.sel_high_view[-1].row()
            high_data = self.highlight_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
            high_text = high_data["text"]

            for bookmark in data["bookmarks"].keys():
                if high_text == data["bookmarks"][bookmark]["notes"]:
                    data["bookmarks"][bookmark]["text"] = text.replace("\n", "\\\n")
                    break
            self.highlight_table.item(row, HIGHLIGHT_H).setData(Qt.UserRole, high_data)
            self.highlight_table.item(row, COMMENT_H).setText(text)
            book_path, ext = splitext(high_data["path"])
            path = join(book_path + ".sdr", "metadata{}.lua".format(ext))
        else:
            return
        self.save_book_data(path, data)

    def on_copy_highlights(self):
        """ Copy the selected highlights to clipboard
        """
        clipboard_text = ""
        for highlight in sorted(self.sel_highlights):
            row = highlight.row()
            text = self.highlights_list.item(row).text()
            clipboard_text += text + "\n"

        data = QMimeData()
        data.setText(clipboard_text)
        self.clip.setMimeData(data)

    def on_delete_highlights(self):
        """ The delete highlights action was invoked
        """
        if self.edit_lua_file_warning:
            text = _("This is an one-time warning!\n\nIn order to delete highlights "
                     "from a book, its \"metadata\" file must be edited. This contains "
                     "a small risk of corrupting that file and lose all the settings "
                     "and info of that book.\n\nDo you still want to do it?")
            popup = self.popup(_("Warning!"), text, buttons=3)
            if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
                return
            else:
                self.edit_lua_file_warning = False
        text = _("This will delete the selected highlights!\nAre you sure?")
        popup = self.popup(_("Warning!"), text, buttons=3)
        if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
            return
        self.delete_highlights()

    def delete_highlights(self):
        """ Delete the selected highlights
        """
        row = self.sel_idx.row()
        data = self.file_table.item(row, TITLE).data(Qt.UserRole)
        for highlight in self.sel_highlights:
            high_row = highlight.row()
            page = self.highlights_list.item(high_row).data(Qt.UserRole)[PAGE]
            page_id = self.highlights_list.item(high_row).data(Qt.UserRole)[PAGE_ID]
            del data["highlight"][page][page_id]  # delete the highlight

            # delete the associated bookmark
            text = self.highlights_list.item(high_row).data(Qt.UserRole)[HIGHLIGHT_TEXT]
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
            item = self.file_table.item(0, 0)
            item.setIcon(self.ico_empty)
        path = self.file_table.item(row, PATH).text()
        self.save_book_data(path, data)

    def save_book_data(self, path, data):
        """ Saves the data of a book to its lua file

        :type path: str|unicode
        :param path: The path to the book's data file
        :type data: dict
        :param data: The book's data
        """
        times = os.stat(path)  # read the file's created/modified times
        self.encode_data(path, data)
        os.utime(path, (times.st_ctime, times.st_mtime))  # reapply original times
        if self.file_table.isVisible():
            self.on_file_table_itemClicked(self.file_table.item(self.sel_idx.row(), 0),
                                           reset=False)

    # noinspection PyUnusedLocal
    def highlights_selection_update(self, selected, deselected):
        """ When a highlight in gets selected

        :type selected: QModelIndex
        :parameter selected: The selected highlight
        :type deselected: QModelIndex
        :parameter deselected: The deselected highlight
        """
        self.sel_highlights = self.highlights_selection.selectedRows()

    def set_highlight_sort(self):
        """ Sets the sorting method of displayed highlights
        """
        self.high_by_page = bool(self.sender().data())
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

    # ___ ___________________ DELETING STUFF ________________________

    def delete_menu(self):
        """ Creates the `Delete` button menu
        """
        menu = QMenu(self)
        for idx, title in enumerate([_("selected books' info"),
                                     _("selected books"),
                                     _("all missing books' info")]):
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
        if not self.sel_indexes and idx in [0, 1]:
            return

        if idx == 0:
            text = _("This will delete the selected books' information\n"
                     "but will keep the equivalent books.")
        elif idx == 1:
            text = _("This will delete the selected books and their information.")
        elif idx == 2:
            text = _("This will delete all the books' information "
                     "that refers to missing books.")
        else:
            text = ""
        popup = self.popup(_("Warning!"), text, buttons=2)
        if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
            return

        if idx == 0:  # selected books' info
            for index in sorted(self.sel_indexes)[::-1]:
                row = index.row()
                path = self.get_sdr_folder(row)
                shutil.rmtree(path) if isdir(path) else os.remove(path)
                self.remove_book_row(row)
        elif idx == 1:  # selected books
            for index in sorted(self.sel_indexes)[::-1]:
                row = index.row()
                path = self.get_sdr_folder(row)
                shutil.rmtree(path) if isdir(path) else os.remove(path)
                try:
                    book_path = self.file_table.item(row, TYPE).data(Qt.UserRole)[0]
                    os.remove(book_path) if isfile(book_path) else None
                    self.remove_book_row(row)
                except AttributeError:  # empty entry
                    self.remove_book_row(row)
                    continue
        elif idx == 2:  # all missing books info
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
        for idx, item in enumerate([_("to individual text files"),
                                    _("combined to one text file")]):
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

    def save_actions(self, idx):
        """ Execute the selected `Save action`

        :type idx: int
        :param idx: The action type
        """
        # save from the highlight_table
        if idx == 2:
            if not self.sel_high_view:
                return
            filename = QFileDialog.getSaveFileName(self, "Save to Text file",
                                                   self.last_dir, "text files (*.txt);;"
                                                                  "all files (*.*)")[0]
            if filename:
                self.last_dir = dirname(filename)
            else:
                return
            text = ""
            for i in sorted(self.sel_high_view):
                row = i.row()
                data = self.highlight_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
                comment = "\n● " + data["comment"] if data["comment"] else ""
                txt = ("{} [{}]\nPage {} [{}]\n{}{}"
                       .format(data["title"], data["authors"], data["page"],
                               data["date"], data["text"], comment))
                text += txt + "\n\n"
            with codecs.open(filename, "w+", encoding="utf-8") as text_file:
                    text_file.write(text.replace("\n", os.linesep))
            return

        # save from the file_table
        title_counter = 0
        saved = 0
        if not self.sel_indexes:
            return
        extra = (" " if self.status.act_page.isChecked() and
                 self.status.act_date.isChecked() else "")
        line_break = (":" + os.linesep if self.status.act_page.isChecked() or
                      self.status.act_date.isChecked() else "")

        if idx == 0:  # save to different text files
            path = QFileDialog.getExistingDirectory(self,
                                                    _("Select destination folder for the "
                                                      "saved file(s)"), self.last_dir,
                                                    QFileDialog.ShowDirsOnly)
            if path:
                self.last_dir = path
                self.status.animation("start")
            else:
                return
            for i in self.sel_indexes:
                row = i.row()
                data = self.file_table.item(row, 0).data(Qt.UserRole)
                highlights = []
                for page in data["highlight"]:
                    for page_id in data["highlight"][page]:
                        highlights.append(self.analyze_high(data, page, page_id))
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
                filename = join(path, self.sanitize_filename(name) + ".txt")
                with codecs.open(filename, "w+", encoding="utf-8") as text_file:
                    for highlight in sorted(highlights, key=self.sort_high4write):
                        date_text, high_comment, high_text, page_text = highlight
                        highlight = (page_text + extra + date_text + line_break +
                                     high_text + high_comment)
                        highlight = highlight + 2 * os.linesep
                        text_file.write(highlight)
                    saved += 1

        elif idx == 1:  # save combined text to one file
            filename = QFileDialog.getSaveFileName(self, "Save to Text file",
                                                   self.last_dir, "text files (*.txt);;"
                                                                  "all files (*.*)")[0]
            if filename:
                filename = filename
                self.last_dir = dirname(filename)
            else:
                return
            blocks = []
            for i in self.sel_indexes:
                row = i.row()
                data = self.file_table.item(row, 0).data(Qt.UserRole)
                highlights = []
                for page in data["highlight"]:
                    for page_id in data["highlight"][page]:
                        highlights.append(self.analyze_high(data, page, page_id))
                highlights = [i[3] + extra + i[0] + line_break + i[2] + i[1]
                              for i in sorted(highlights, key=self.sort_high4write)]
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
                # noinspection PyUnresolvedReferences
                blocks.append((name, (2 * os.linesep).join(highlights)))
                saved += 1
            line = "-" * 80
            with codecs.open(filename, "w+", encoding="utf-8") as text_file:
                for block in blocks:
                    text_file.write("{0}{3}{1}{3}{0}{3}{2}{3}{3}"
                                    .format(line, block[0], block[1], os.linesep))

        self.status.animation("stop")
        all_files = len(self.file_table.selectionModel().selectedRows())
        self.popup(_("Finished!"), _("{} texts were saved from the {} processed.\n"
                                     "{} files with no highlights.")
                   .format(saved, all_files, all_files - saved),
                   icon=QMessageBox.Information)

    def analyze_high(self, data, page, page_id):
        """ Get the highlight's info (text, comment, date and page)

        :type data: dict
        :param data: The highlight's data
        :type page: int
        :param page The page where the highlight starts
        :type page_id: int
        :param page_id The count of this page's highlight
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
        page_text = "Page " + str(page) if self.status.act_page.isChecked() else ""
        date_text = "[" + date + "]" if self.status.act_date.isChecked() else ""
        high_text = (text.replace("\n", os.linesep)
                     if self.status.act_text.isChecked() else "")
        comment = comment.replace("\n", os.linesep)
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
            self.skip_version = app_config.get("skip_version", None)
            self.exit_msg = app_config.get("exit_msg", True)
            self.high_merge_warning = app_config.get("high_merge_warning", True)
            self.edit_lua_file_warning = app_config.get("edit_lua_file_warning", True)

            checked = app_config.get("show_items", (True, True, True, True))
            # noinspection PyTypeChecker
            checked = checked if len(checked) == 4 else checked + [True]  # 4compatibility
            self.toolbar.view_frame.children()[self.current_view + 1].click()
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

    def settings_save(self):
        """ Saves the jason based configuration settings
        """
        config = {"geometry": pickle.dumps(self.saveGeometry()),
                  "state": pickle.dumps(self.saveState()),
                  "splitter": pickle.dumps(self.splitter.saveState()),
                  "about_geometry": pickle.dumps(self.about.saveGeometry()),
                  "col_sort_asc": self.col_sort_asc, "col_sort": self.col_sort,
                  "col_sort_asc_h": self.col_sort_asc_h, "col_sort_h": self.col_sort_h,
                  "highlight_width": self.highlight_width,
                  "comment_width": self.comment_width,
                  "last_dir": self.last_dir, "exit_msg": self.exit_msg,
                  "current_view": self.current_view, "high_by_page": self.high_by_page,
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
            with gzip.GzipFile(join(SETTINGS_DIR, "settings.json.gz"), "w+") as gz_file:
                gz_file.write(json.dumps(config, sort_keys=True, indent=4))
        except IOError as error:
            print("On saving settings:", error)

    @staticmethod
    def unpickle(key):
        """ Un-serialize some binary settings

        :type key: str|unicode
        :param key: The dict key to be un-pickled
        """
        try:
            value = pickle.loads(str(app_config.get(key)))
        except pickle.UnpicklingError:
            return
        return value

    # ___ ___________________ UTILITY STUFF _________________________

    def passed_files(self):
        """ Command line parameters that are passed to the program.
        """
        # args = QApplication.instance().arguments()
        try:
            if sys.argv[1]:
                dropped = [i.decode("mbcs") for i in sys.argv[1:]]
                self.on_file_table_fileDropped(dropped)
        except IndexError:
            pass

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

    @staticmethod
    def decode_data(path):
        """ Converts a lua table to a Python dict

        :type path: str|unicode
        :param path: The path to the lua file
        """
        with codecs.open(path, "r", encoding="utf8") as txt_file:
            txt = txt_file.read()[39:]  # offset the first words of the file
            data = lua.decode(txt.replace("--", "—"))
            if type(data) == dict:
                return data

    @staticmethod
    def encode_data(path, dict_data):
        """ Converts a Python dict to a lua table

        :type path: str|unicode
        :param path: The path to the lua file
        :type dict_data: dict
        :param dict_data: The dictionary to be encoded as lua table
        """
        with codecs.open(path, "w+", encoding="utf8") as txt_file:
            lua_text = "-- we can read Lua syntax here!\nreturn "
            lua_text += lua.encode(dict_data)
            txt_file.write(lua_text)

    @staticmethod
    def sanitize_filename(filename):
        """ Creates a safe filename

        :type filename: str|unicode
        :param filename: The filename to be sanitized
        """
        filename = re.sub(r'[/:*?"<>|\\]', "_", filename)
        return filename

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
        try:
            version_new = self.about.get_online_version()
        except URLError:  # can not connect
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
        _, _, files = os.walk(SETTINGS_DIR).next()
        files = sorted(i for i in files if i.startswith("error_log"))
        if len(files) > 3:
            for name in files[:-3]:
                try:
                    os.remove(join(SETTINGS_DIR, name))
                except WindowsError:  # the file is locked
                    pass

    def on_check_btn(self):
        QMessageBox.information(self, _("Info"), _("Tool button is pressed"))


# ___ _______________________ EXTRA CLASSES _________________________


class About(QDialog, Ui_About):

    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        self.setupUi(self)
        # Remove the question mark widget from dialog
        self.setWindowFlags(self.windowFlags() ^
                            Qt.WindowContextHelpButtonHint)
        self.base = parent

    @Slot()
    def on_about_qt_btn_clicked(self):
        """ The `About Qt` button is pressed
        """
        # noinspection PyCallByClass
        QMessageBox.aboutQt(self, title=_("About Qt"))

    @Slot()
    def on_updates_btn_clicked(self):
        """ The `Check for Updates` button is pressed
        """
        self.check_for_updates()

    def check_for_updates(self):
        """ Checks the web site for the current version
        """
        version_new = self.get_online_version()
        if not version_new:
            self.base.popup(_("No response!"), _("Version info is unreachable!\n"
                                                 "Please, try again later..."), buttons=1)
            return
        version = LooseVersion(self.base.version)
        if version_new > version:
            popup = self.base.popup(_("Newer version exists!"),
                                    _("There is a newer version (v.{}) online.\n"
                                      "Open the site to download it now?")
                                    .format(version_new),
                                    icon=QMessageBox.Information, buttons=2)
            if popup.clickedButton().text() == "OK":
                webbrowser.open("http://www.noembryo.com/apps.php?katalib")
                self.close()
        elif version_new == version:
            self.base.popup(_("No newer version exists!"),
                            _("{} is up to date (v.{})").format(APP_NAME, version),
                            icon=QMessageBox.Information, buttons=1)
        elif version_new < version:
            self.base.popup(_("No newer version exists!"),
                            _("It seems that you are using a newer version ({0})\n"
                              "than the one online ({1})!").format(version, version_new),
                            icon=QMessageBox.Question, buttons=1)

    @staticmethod
    def get_online_version():
        browser = mechanize.Browser()
        browser.set_handle_robots(False)

        header = {"User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:14.0) "
                                "Gecko/20100101 Firefox/24.0.1",
                  "Referer": "http://whateveritis.com"}
        url = "http://www.noembryo.com/apps.php?kohighlights"

        request = Request(url, None, header)
        html_text = browser.open(request)
        soup_text = BeautifulSoup(html_text, "html5lib")
        results = soup_text.findAll(name="p")
        results = "".join([str(i) for i in results])
        match = re.search(r"\d+\.\d+\.\d+\.\d+", results, re.DOTALL)
        try:
            version_new = match.group(0)
        except AttributeError:  # no match found
            return
        return LooseVersion(version_new)

    def create_text(self):
        # color = self.palette().color(QPalette.WindowText).name()  # for links
        splash = ":/stuff/logo.png"
        paypal = ":/stuff/paypal.png"
        info = _("""<body style="font-size:10pt; font-weight:400; font-style:normal">
        <center>
          <table width="100%" border="0">
            <tr>
                <p align="center"><img src="{0}" width="256" height ="212"></p>
                <p align="center"><b>KoHighlights</b> is a utility for viewing
                    <a href="https://github.com/koreader/koreader">Koreader</a>'s
                    highlights<br/>and/or export them to simple text</p>
                <p align="center">Version {1}</p>
                <p align="center">Visit
                    <a href="https://github.com/noEmbryo/KoHighlights">
                    KoHighlights page at GitHub</a>, or</p>
                <p align="center"><a href="http://www.noEmbryo.com"> noEmbryo's page</a>
                    with more Apps and stuff...</p>
                <p align="center">Use it and if you like it, consider to
                <p align="center"><a href="https://www.paypal.com/cgi-bin/webscr?
                    cmd=_s-xclick &hosted_button_id=RBYLVRYG9RU2S">
                <img src="{2}" alt="PayPal Button"
                    width="142" height="27" border="0"></a></p>
                <p align="center">&nbsp;</p></td>
            </tr>
          </table>
        </center>
        </body>""").format(splash, self.base.version, paypal)
        self.text_lbl.setText(info)


class AutoInfo(QDialog, Ui_AutoInfo):
    def __init__(self, parent=None):
        super(AutoInfo, self).__init__(parent)
        self.setupUi(self)
        # Remove the question mark widget from dialog
        # self.setWindowFlags(self.windowFlags() ^
        #                     Qt.WindowContextHelpButtonHint)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.hide()

        font = QFont()
        font.setBold(True)
        font.setPointSize(QFont.pointSize(QFont()) + 3)
        self.label.setFont(font)

    def set_text(self, text):
        self.label.setText(text)


class ToolBar(QWidget, Ui_ToolBar):

    def __init__(self, parent=None):
        super(ToolBar, self).__init__(parent)
        self.setupUi(self)
        self.base = parent

        # buttons = (self.add_folder_btn, self.manage_folders_btn, self.del_files_btn)
        # for button in buttons:
        #     button.installEventFilter(TextSizer(button))

        self.books_btn.clicked.connect(partial(self.change_view, 0))
        self.highlights_btn.clicked.connect(partial(self.change_view, 1))

        self.check_btn.clicked.connect(parent.on_check_btn)
        self.check_btn.hide()

    @Slot()
    def on_select_btn_clicked(self):
        """ The `Scan Directory` button is pressed
        """
        path = QFileDialog.getExistingDirectory(self.base,
                                                _("Select a directory with books or "
                                                  "your eReader's drive"),
                                                self.base.last_dir,
                                                QFileDialog.ShowDirsOnly)
        if path:
            self.base.last_dir = path
            # self.base.file_table.model().removeRows(0, self.base.file_table.rowCount())
            self.base.highlights_list.clear()
            self.base.scan_files_thread(path)

    @Slot()
    def on_save_btn_clicked(self):
        """ The `Save Selected` button is pressed
        """
        if self.base.current_view == 0:  # books view
            self.base.save_actions(0)
        elif self.base.current_view == 1:  # highlights view
            self.base.save_actions(2)

    @Slot()
    def on_open_btn_clicked(self):
        """ The `Open Book` button is pressed
        """
        if self.base.current_view == 0:  # books view
            try:
                idx = self.base.sel_indexes[-1]
            except IndexError:  # nothing selected
                return
            item = self.base.file_table.item(idx.row(), 0)
            self.base.on_file_table_itemDoubleClicked(item)
        if self.base.current_view == 1:  # highlights view
            try:
                idx = self.base.sel_high_view[-1]
            except IndexError:  # nothing selected
                return
            data = self.base.highlight_table.item(idx.row(),
                                                  HIGHLIGHT_H).data(Qt.UserRole)
            self.base.open_file(data["path"])

    @Slot()
    def on_merge_btn_clicked(self):
        """ The `Merge` button is pressed
        """
        data = [self.base.file_table.item(idx.row(), idx.column()).data(Qt.UserRole)
                for idx in self.base.sel_indexes]
        if data[0]["cre_dom_version"] == data[1]["cre_dom_version"]:
            if self.base.high_merge_warning:
                text = _("Merging highlights from different devices is experimental so, "
                         "always do backups ;o)\n"
                         "Because of the different page formats and sizes, some page "
                         "numbers in KoHighlights might be inaccurate. "
                         "Do you want to continue?")
                popup = self.base.popup(_("Warning!"), text, buttons=3,
                                        check_text=_("Don't show this again"))
                self.base.high_merge_warning = not popup.checked
                if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
                    return

            popup = self.base.popup(_("Warning!"),
                                    _("The highlights of the selected entries will be "
                                      "merged.\nThis can not be undone! Continue?"),
                                    buttons=3,
                                    check_text=_("Try to sync the reading position too"))
            if popup.buttonRole(popup.clickedButton()) == QMessageBox.AcceptRole:
                self.base.merge_highlights(popup.checked)
        else:
            text = _("Can not merge these highlights, because they are produced with a "
                     "different version of the reader engine!\n\n"
                     "The reader engine and the way it renders the text is responsible "
                     "for the positioning of highlights. Some times, code changes are "
                     "made that change its behavior. Its version is written in the "
                     "metadata of a book the first time is opened and can only change "
                     "if the metadata are cleared (loosing all highlights) and open the "
                     "book again as new.\n"
                     "The reader's engine version is independent of the KoReader version "
                     "and does not change that often.")
            self.base.popup(_("Version mismatch!"), text, icon=QMessageBox.Critical)

    @Slot()
    def on_delete_btn_clicked(self):
        """ The `Delete` button is pressed
        """
        self.base.delete_actions(0)

    @Slot()
    def on_clear_btn_clicked(self):
        """ The `Clear List` button is pressed
        """
        # self.base.file_table.setRowCount(0)
        if self.base.current_view == 0:  # books view
            self.base.file_table.model().removeRows(0, self.base.file_table.rowCount())
        elif self.base.current_view == 1:  # highlights view
            (self.base.highlight_table.model()
             .removeRows(0, self.base.highlight_table.rowCount()))

    def change_view(self, idx):
        if idx == 0:  # books view
            self.base.status.show()
            self.base.toolbar.save_btn.setStyleSheet("")
            self.base.toolbar.save_btn.setPopupMode(QToolButton.MenuButtonPopup)
            self.base.toolbar.merge_btn.show()
            self.base.toolbar.delete_btn.show()
            sel_idx = self.base.sel_idx
            if sel_idx:
                item = self.base.file_table.item(sel_idx.row(), sel_idx.column())
                self.base.on_file_table_itemClicked(item, reset=False)
        elif idx == 1:  # highlights view
            self.base.status.hide()
            no_arrow = "QToolButton::menu-indicator{width:0px;}"
            self.base.toolbar.save_btn.setStyleSheet(no_arrow)
            self.base.toolbar.save_btn.setPopupMode(QToolButton.DelayedPopup)
            self.base.toolbar.merge_btn.hide()
            self.base.toolbar.delete_btn.hide()
            self.base.scan_highlights_thread()
        self.base.current_view = idx
        self.base.views.setCurrentIndex(idx)

    @Slot()
    def on_about_btn_clicked(self):
        """ The `About` button is pressed
        """
        self.base.about.create_text()
        self.base.about.show()


class TextDialog(QDialog, Ui_TextDialog):

    def __init__(self, parent=None):
        super(TextDialog, self).__init__(parent)
        # Remove the question mark widget from dialog
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setupUi(self)

        self.base = parent
        self.on_ok = None

    @Slot()
    def on_ok_btn_clicked(self):
        """ The OK button is pressed
        """
        self.on_ok()


class Status(QWidget, Ui_Status):

    def __init__(self, parent=None):
        super(Status, self).__init__(parent)
        self.setupUi(self)
        self.base = parent

        self.wait_anim = QMovie(":/stuff/wait.gif")
        self.anim_lbl.setMovie(self.wait_anim)
        self.anim_lbl.hide()

        self.show_menu = QMenu(self)
        for i in [self.act_page, self.act_date, self.act_text, self.act_comment]:
            self.show_menu.addAction(i)
            # noinspection PyUnresolvedReferences
            i.triggered.connect(self.on_show_items)
            i.setChecked(True)

        sort_menu = QMenu(self)
        ico_sort = QIcon(":/stuff/sort.png")
        group = QActionGroup(self)

        action = QAction(_("Date"), sort_menu)
        action.setCheckable(True)
        action.setChecked(not self.base.high_by_page)
        action.triggered.connect(self.base.set_highlight_sort)
        action.setData(0)
        group.addAction(action)
        sort_menu.addAction(action)

        action = QAction(_("Page"), sort_menu)
        action.setCheckable(True)
        action.setChecked(self.base.high_by_page)
        action.triggered.connect(self.base.set_highlight_sort)
        action.setData(1)
        group.addAction(action)
        sort_menu.addAction(action)

        sort_menu.setIcon(ico_sort)
        sort_menu.setTitle(_("Sort by"))
        self.show_menu.addMenu(sort_menu)

        self.show_items_btn.setMenu(self.show_menu)

    def on_show_items(self):
        """ Show/Hide elements of the highlight info
        """
        try:
            idx = self.base.file_table.selectionModel().selectedRows()[-1]
        except IndexError:  # nothing selected
            return
        item = self.base.file_table.item(idx.row(), 0)
        self.base.on_file_table_itemClicked(item)

    def animation(self, action):
        """ Creates or deletes temporary files and folders

        :type action: str|unicode
        :param action: The action that must be done
        """
        if action == "start":
            self.anim_lbl.show()
            self.wait_anim.start()
        elif action == "stop":
            self.anim_lbl.hide()
            self.wait_anim.stop()


class XTableWidgetItem(QTableWidgetItem):
    def __lt__(self, value):
        return self.data(Qt.UserRole) < value.data(Qt.UserRole)


class LogStream(QObject):
    append_to_log = Signal(str)

    # def __init__(self):
    #     super(LogStream, self).__init__()
    #     # noinspection PyArgumentList
    #     self.base = QtGui.QApplication.instance().base

    def write(self, text):
        self.append_to_log.emit(text)


class Scanner(QObject):
    found = Signal(unicode)
    finished = Signal()

    def __init__(self, path):
        super(Scanner, self).__init__()
        self.path = path

    def process(self):
        self.start_scan()
        self.finished.emit()

    def start_scan(self):
        try:
            for dir_tuple in os.walk(self.path):
                dir_path = dir_tuple[0]
                if dir_path.lower().endswith(".sdr"):  # a book's metadata folder
                    if dir_path.lower().endswith("evernote.sdr"):
                        continue
                    for file_ in dir_tuple[2]:  # get the .lua file not the .old (backup)
                        if splitext(file_)[1].lower() == ".lua":
                            self.found.emit(join(dir_path, file_))
                            break
                # older metadata storage or android history folder
                elif (dir_path.lower().endswith(join("koreader", "history"))
                      or basename(dir_path).lower() == "history"):
                    for file_ in dir_tuple[2]:
                        if splitext(file_)[1].lower() == ".lua":
                            self.found.emit(join(dir_path, file_))
                    continue
        except UnicodeDecodeError:  # os.walk error
            pass


class HighlightScanner(QObject):
    found = Signal(dict)
    finished = Signal()

    def __init__(self):
        super(HighlightScanner, self).__init__()
        # noinspection PyArgumentList
        self.base = QApplication.instance().base

    def process(self):
        for row in range(self.base.file_table.rowCount()):
            data = self.base.file_table.item(row, TITLE).data(Qt.UserRole)
            path = self.base.file_table.item(row, TYPE).data(Qt.UserRole)[0]
            self.get_book_highlights(data, path)
        self.finished.emit()

    def get_book_highlights(self, data, path):
        """ Finds all the highlights from a book

        :type data: dict
        :param data: The book data (converted from the lua file)
        :type path: str|unicode
        :param path: The book path
        """
        try:
            authors = data["stats"]["authors"]
        except KeyError:  # older type file
            authors = ""
        authors = authors if authors else _("NO AUTHOR FOUND")
        try:
            title = data["stats"]["title"]
        except KeyError:  # older type file
            title = ""
        title = title if title else _("NO TITLE FOUND")

        for page in sorted(data["highlight"]):
            for page_id in data["highlight"][page]:
                highlight = {"authors": authors, "title": title, "path": path}
                try:
                    highlight["date"] = data["highlight"][page][page_id]["datetime"]
                    text = data["highlight"][page][page_id]["text"].replace("\\\n", "\n")
                    comment = ""
                    for idx in data["bookmarks"]:  # check for comment text
                        if text == data["bookmarks"][idx]["notes"]:
                            book_text = data["bookmarks"][idx].get("text", "")
                            if not book_text:
                                break
                            book_text = re.sub(r"Page \d+ "
                                               r"(.+?) @ \d+-\d+-\d+ \d+:\d+:\d+", r"\1",
                                               book_text, 1, re.DOTALL | re.MULTILINE)
                            if text != book_text:  # there is a comment
                                comment = book_text.replace("\\\n", "\n")
                            break
                    highlight["text"] = text
                    highlight["comment"] = comment
                    highlight["page"] = str(page)
                except KeyError:  # blank highlight
                    continue
                self.found.emit(highlight)


class DropTableWidget(QTableWidget):
    fileDropped = Signal(list)

    def __init__(self, parent=None):
        super(DropTableWidget, self).__init__(parent)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
            return True
        else:
            event.ignore()
            return False

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
            return True
        else:
            event.ignore()
            return False

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            links = []
            for url in event.mimeData().urls():
                links.append(url.toLocalFile())
            self.fileDropped.emit(links)
            event.accept()
            return True
        else:
            event.ignore()
            return False


class XMessageBox(QMessageBox):
    """ A QMessageBox with a QCheckBox
    """
    def __init__(self, parent=None):
        super(XMessageBox, self).__init__(parent)

        self.check_box = QCheckBox()
        self.checked = False

        # Access the Layout of the MessageBox to add a Checkbox
        layout = self.layout()
        layout.addWidget(self.check_box, 1, 1)

    def exec_(self, *args, **kwargs):
        """ Override the exec_ method so
        you can return the value of the checkbox
        """
        return (QMessageBox.exec_(self, *args, **kwargs),
                self.check_box.isChecked())


class KoHighlights(QApplication):
    def __init__(self, *args, **kwargs):
        super(KoHighlights, self).__init__(*args, **kwargs)
        self.base = Base()
        self.exec_()


if __name__ == '__main__':
    app = KoHighlights(sys.argv)
