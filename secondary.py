# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
from boot_config import *
import re
import webbrowser
from functools import partial
from distutils.version import LooseVersion
from os.path import join, basename, splitext, isfile
from pprint import pprint

if QT4:  # ___ ______________ DEPENDENCIES __________________________
    from PySide.QtCore import Qt, Slot, QObject, Signal, QSize, QPoint, QEvent
    from PySide.QtGui import (QApplication, QMessageBox, QIcon, QFileDialog, QLineEdit,
                              QDialog, QWidget, QMovie, QFont, QMenu, QAction, QCursor,
                              QTableWidget, QCheckBox, QToolButton, QActionGroup,
                              QTableWidgetItem)
else:
    from PySide2.QtCore import QObject, Qt, Signal, QPoint, Slot, QSize, QEvent
    from PySide2.QtGui import QFont, QMovie, QIcon, QCursor
    from PySide2.QtWidgets import (QTableWidgetItem, QTableWidget, QMessageBox, QLineEdit,
                                   QApplication, QWidget, QDialog, QFileDialog,
                                   QActionGroup, QMenu, QAction, QToolButton, QCheckBox)
import requests
from bs4 import BeautifulSoup
from slppu import slppu as lua  # https://github.com/noembryo/slppu


def _(text):  # for future gettext support
    return text


def decode_data(path):
    """ Converts a lua table to a Python dict

    :type path: str|unicode
    :param path: The path to the lua file
    """
    with open(path, "r", encoding="utf8", newline=None) as txt_file:
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
    with open(path, "w+", encoding="utf8", newline="") as txt_file:
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


def get_csv_row(data):
    """ Return an RFC 4180 compliant csv row

    :type data: dict
    :param data: The highlight's data
    """
    values = []
    for key in CSV_KEYS:
        value = data[key].replace('"', '""')
        if "\n" in value or '"' in value:
            value = '"' + value.lstrip() + '"'
        values.append(value if value else "")
    return "\t".join(values)


def get_book_text(title, authors, highlights, format_, line_break, space, text):
    """ Create the book's contents to be added to a single merged exported file
    """
    nl = os.linesep
    if format_ == ONE_HTML:
        text += BOOK_BLOCK % {"title": title, "authors": authors}
        for high in highlights:
            date_text, high_comment, high_text, page_text, chapter = high
            text += HIGH_BLOCK % {"page": page_text, "date": date_text,
                                  "highlight": high_text, "comment": high_comment,
                                  "chapter": chapter}
        text += "</div>\n"
    elif format_ == ONE_TEXT:
        name = title
        if authors:
            name = "{} - {}".format(authors, title)
        line = "-" * 80
        text += line + nl + name + nl + line + nl
        highlights = [i[3] + space + i[0] + line_break +
                      ("[{}]{}".format(i[4], nl) if i[4] else "") +
                      i[2] + i[1] for i in highlights]
        text += (nl * 2).join(highlights) + nl * 2
    elif format_ == ONE_CSV:
        for high in highlights:
            date_text, high_comment, high_text, page_text, chapter = high
            data = {"title": title, "authors": authors, "page": page_text,
                    "date": date_text, "text": high_text, "comment": high_comment,
                    "chapter": chapter}
            # data = {k.encode("utf8"): v.encode("utf8") for k, v in data.items()}
            text += get_csv_row(data) + "\n"
    elif format_ == ONE_MD:
        text += "\n---\n## {}  \n##### {}  \n---\n".format(title, authors)
        highs = []
        for i in highlights:
            comment = i[1].replace(nl, "  " + nl)
            if comment:
                comment = "  " + comment
            chapter = i[4]
            if chapter:
                chapter = "***{0}***{1}{1}".format(chapter, nl).replace(nl, "  " + nl)
            high = i[2].replace(nl, "  " + nl)
            h = ("*" + i[3] + space + i[0] + line_break + chapter +
                 high + comment + "  \n&nbsp;  \n")
            h = h.replace("-", "\\-")
            highs.append(h)
        text += nl.join(highs) + "\n---\n"
    return text


def save_file(title, authors, highlights, path, format_, line_break, space, sort_by):
    """ Saves the book's exported file
    """
    nl = os.linesep
    ext = text = ""
    encoding = "utf-8"
    name = title
    if authors:
        name = "{} - {}".format(authors, title)
    if format_ == MANY_TEXT:
        ext = ".txt"
        line = "-" * 80
        text = line + nl + name + nl + line + (2 * nl)
    elif format_ == MANY_HTML:
        ext = ".html"
        text = HTML_HEAD + BOOK_BLOCK % {"title": title, "authors": authors}
    elif format_ == MANY_CSV:
        ext = ".csv"
        text = CSV_HEAD
        encoding = "utf-8-sig"
    elif format_ == MANY_MD:
        ext = ".md"
        text = "\n---\n## {}  \n##### {}  \n---\n".format(title, authors)

    filename = join(path, sanitize_filename(name))
    if _("NO TITLE FOUND") in title:  # don't overwrite unknown title files
        while isfile(filename + ext):
            match = re.match(r"(.+?) \[(\d+?)]$", filename)
            if match:
                filename = "{} [{:02}]".format(match.group(1), int(match.group(2)) + 1)
            else:
                filename += " [01]"
    filename = filename + ext

    with open(filename, "w+", encoding=encoding, newline="") as text_file:
        for highlight in sorted(highlights, key=sort_by):
            date_text, high_comment, high_text, page_text, chapter = highlight
            if format_ == MANY_HTML:
                text += HIGH_BLOCK % {"page": page_text, "date": date_text,
                                      "highlight": high_text, "comment": high_comment,
                                      "chapter": chapter}
            elif format_ == MANY_TEXT:
                text += (page_text + space + date_text + line_break +
                         ("[{}]{}".format(chapter, nl) if chapter else "") +
                         high_text + high_comment)
                text += 2 * nl
            elif format_ == MANY_CSV:
                data = {"title": title, "authors": authors, "page": page_text,
                        "date": date_text, "text": high_text, "comment": high_comment,
                        "chapter": chapter}
                text += get_csv_row(data) + "\n"
            elif format_ == MANY_MD:
                high_text = high_text.replace(nl, "  " + nl)
                high_comment = high_comment.replace(nl, "  " + nl)
                if high_comment:
                    high_comment = "  " + high_comment
                if chapter:
                    chapter = "***{0}***{1}{1}".format(chapter, nl).replace(nl, "  " + nl)
                text += ("*" + page_text + space + date_text + line_break +
                         chapter + high_text + high_comment +
                         "  \n&nbsp;  \n\n").replace("-", "\\-")
        if format_ == MANY_HTML:
            text += "\n</div>\n</body>\n</html>"

        text_file.write(text)


__all__ = ("_", "decode_data", "encode_data", "sanitize_filename", "get_csv_row",
           "get_book_text", "save_file", "XTableWidgetIntItem", "XTableWidgetPercentItem",
           "XTableWidgetTitleItem", "DropTableWidget", "XMessageBox", "About", "AutoInfo",
           "ToolBar", "TextDialog", "Status", "LogStream", "Scanner", "HighlightScanner",
           "ReLoader", "DBLoader", "XToolButton", "Filter")


# ___ _______________________ SUBCLASSING ___________________________


class XTableWidgetIntItem(QTableWidgetItem):
    """ Sorts numbers writen as strings (after 1 is 2 not 11)
    """

    def __lt__(self, value):
        try:
            return int(self.data(Qt.DisplayRole)) < int(value.data(Qt.DisplayRole))
        except ValueError:  # no text
            this_text = self.data(Qt.DisplayRole)
            if not this_text:
                this_text = "0"
            that_text = value.data(Qt.DisplayRole)
            if not that_text:
                that_text = "0"
            return int(this_text) < int(that_text)


class XTableWidgetPercentItem(QTableWidgetItem):
    """ Sorts percentages writen as strings (e.g. 35%)
    """

    def __lt__(self, value):
        return int(self.data(Qt.DisplayRole)[:-1]) < int(value.data(Qt.DisplayRole)[:-1])


class XTableWidgetTitleItem(QTableWidgetItem):
    """ Sorts titles ignoring the leading "A" or "The"
    """

    def __lt__(self, value):
        t1 = self.data(Qt.DisplayRole).lower()
        t1 = (t1[2:] if t1.startswith("a ") else
              t1[4:] if t1.startswith("the ") else
              t1[3:] if t1.startswith("an ") else t1)

        t2 = value.data(Qt.DisplayRole).lower()
        t2 = (t2[2:] if t2.startswith("a ") else
              t2[4:] if t2.startswith("the ") else
              t2[3:] if t2.startswith("an ") else t2)

        return t1 < t2


class DropTableWidget(QTableWidget):
    fileDropped = Signal(list)

    def __init__(self, parent=None):
        super(DropTableWidget, self).__init__(parent)
        # noinspection PyArgumentList
        self.app = QApplication.instance()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls and not self.app.base.db_mode:
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
        self.check_box.stateChanged.connect(self.checkbox_state_changed)
        self.checked = False

        self.input = QLineEdit()
        self.input.textChanged.connect(self.input_text_changed)
        self.typed_text = ""

    def set_check(self, text):
        """ Sets the Popup's CheckBox

        :type text: str|unicode
        :param text: The CheckBox's text
        """
        self.add_to_layout(self.check_box)
        self.check_box.setText(text)

    def checkbox_state_changed(self, state):
        """ Update the checked variable

        :type state: bool
        :param state: The CheckBox's state
        """
        self.checked = bool(state)

    def set_input(self, text):
        """ Sets the Popup's text input

        :type text: str|unicode|bool
        :param text: The QLineEdit's text
        """
        self.add_to_layout(self.input)
        if not isinstance(text, bool):
            self.input.setText(text)

    def input_text_changed(self, text):
        """ Update the typed_text variable

        :type text: str|unicode
        :param text: The QLineEdit's text
        """
        self.typed_text = text

    def add_to_layout(self, widget):
        """ Add the given widget to the popup's layout
        Only one widget can be added in a popup instance

        :type widget: QWidget
        :param widget: The widget to be added
        """
        # noinspection PyArgumentList
        self.layout().addWidget(widget, 1, 1 if PYTHON2 else 2)


class XToolButton(QToolButton):
    right_clicked = Signal()

    def __init__(self, parent=None):
        super(XToolButton, self).__init__(parent)
        self.installEventFilter(self)

    # def mousePressEvent(self, QMouseEvent):
    #     if QMouseEvent.button() == Qt.RightButton:
    #         # do what you want here
    #         print("Right Button Clicked")
    #         QMouseEvent.accept()

    def eventFilter(self, obj, event):
        if obj.objectName() == "db_btn":
            if event.type() == QEvent.ContextMenu:
                self.right_clicked.emit()
                return True
            else:
                return False
        else:
            # pass the event on to the parent class
            return QToolButton.eventFilter(self, obj, event)

# ___ _______________________ WORKERS _______________________________


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
            for dir_path, dirs, files in os.walk(self.path):
                if dir_path.lower().endswith(".sdr"):  # a book's metadata folder
                    if dir_path.lower().endswith("evernote.sdr"):
                        continue
                    for file_ in files:  # get the .lua file not the .old (backup)
                        if splitext(file_)[1].lower() == ".lua":
                            self.found.emit(join(dir_path, file_))
                # older metadata storage or android history folder
                elif (dir_path.lower().endswith(join("koreader", "history"))
                      or basename(dir_path).lower() == "history"):
                    for file_ in files:
                        if splitext(file_)[1].lower() == ".lua":
                            self.found.emit(join(dir_path, file_))
                    continue
        except UnicodeDecodeError:  # os.walk error
            pass


class ReLoader(QObject):
    found = Signal(unicode)
    finished = Signal()

    def __init__(self, paths):
        super(ReLoader, self).__init__()
        self.paths = paths

    def process(self):
        for path in self.paths:
            self.found.emit(path)
        self.finished.emit()


class DBLoader(QObject):
    found = Signal(unicode, dict, unicode)
    finished = Signal()

    def __init__(self, books):
        super(DBLoader, self).__init__()
        self.books = books

    def process(self):
        for book in self.books:
            self.found.emit(book["path"], book["data"], book["date"])
        self.finished.emit()


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
        highlights = self.base.get_highlights_from_data(data, path)
        for highlight in highlights:
            self.found.emit(highlight)

# ___ _______________________ GUI STUFF _____________________________


from gui_about import Ui_About
from gui_auto_info import Ui_AutoInfo
from gui_toolbar import Ui_ToolBar
from gui_status import Ui_Status
from gui_edit import Ui_TextDialog
from gui_filter import Ui_Filter


class ToolBar(QWidget, Ui_ToolBar):

    def __init__(self, parent=None):
        super(ToolBar, self).__init__(parent)
        self.setupUi(self)
        self.base = parent

        self.buttons = (self.check_btn, self.scan_btn, self.export_btn, self.open_btn,
                        self.merge_btn, self.delete_btn, self.clear_btn, self.about_btn,
                        self.books_view_btn, self.high_view_btn, self.filter_btn)
        self.size_menu = self.create_size_menu()
        self.db_menu = self.create_db_menu()
        self.db_btn.setMenu(self.db_menu)

        for btn in [self.loaded_btn, self.db_btn,
                    self.books_view_btn, self.high_view_btn]:
            btn.clicked.connect(self.change_view)

        self.check_btn.clicked.connect(parent.on_check_btn)
        self.check_btn.hide()

    @Slot(QPoint)
    def on_tool_frame_customContextMenuRequested(self, point):
        """ The Toolbar is right-clicked

        :type point: QPoint
        :param point: The point where the right-click happened
        """
        self.size_menu.exec_(self.tool_frame.mapToGlobal(point))

    def create_size_menu(self):
        """ Create the toolbar's buttons size menu
        """
        menu = QMenu(self)
        group = QActionGroup(self)
        sizes = (_("Tiny"), 16), (_("Small"), 32), (_("Medium"), 48), (_("Big"), 64)
        for name, size in sizes:
            action = QAction(name, menu)
            action.setCheckable(True)
            if size == self.base.toolbar_size:
                action.setChecked(True)
            action.triggered.connect(partial(self.set_btn_size, size))
            group.addAction(action)
            menu.addAction(action)
        return menu

    def set_btn_size(self, size):
        """ Changes the Toolbar's icons size

        :type size: int
        :param size: The Icons' size preset
        """
        self.base.toolbar_size = size
        button_size = QSize(size, size)
        half_size = QSize(size * .5, size * .5)

        for btn in self.buttons:
            btn.setMinimumWidth(size + 10)
            btn.setIconSize(button_size)

        for btn in [self.loaded_btn, self.db_btn]:
            # btn.setMinimumWidth(size + 10)
            btn.setIconSize(half_size)
        # noinspection PyArgumentList
        QApplication.processEvents()

    @Slot()
    def on_scan_btn_clicked(self):
        """ The `Scan Directory` button is pressed
        """
        path = QFileDialog.getExistingDirectory(self.base,
                                                _("Select a directory with books or "
                                                  "your eReader's drive"),
                                                self.base.last_dir,
                                                QFileDialog.ShowDirsOnly)
        if path:
            self.base.last_dir = path
            self.base.high_list.clear()
            self.base.reload_highlights = True
            self.base.loading_thread(Scanner, path, self.base.kor_text, clear=False)

    @Slot()
    def on_export_btn_clicked(self):
        """ The `Export` button is pressed
        """
        self.base.on_export()

    @Slot()
    def on_open_btn_clicked(self):
        """ The `Open Book` button is pressed
        """
        if self.base.current_view == BOOKS_VIEW:
            try:
                idx = self.base.sel_indexes[-1]
            except IndexError:  # nothing selected
                return
            item = self.base.file_table.item(idx.row(), 0)
            self.base.on_file_table_itemDoubleClicked(item)
        if self.base.current_view == HIGHLIGHTS_VIEW:
            try:
                idx = self.base.sel_high_view[-1]
            except IndexError:  # nothing selected
                return
            data = self.base.high_table.item(idx.row(), HIGHLIGHT_H).data(Qt.UserRole)
            self.base.open_file(data["path"])

    @Slot(bool)
    def on_filter_btn_toggled(self, state):
        """ The `Find` button is pressed

        :type state: bool
        :param state: Pressed or not
        """
        if state:
            self.base.filter.show()
        else:
            self.base.filter.hide()
            self.base.filter.on_clear_filter_btn_clicked()

    @Slot()
    def on_merge_btn_clicked(self):
        """ The `Merge` button is pressed
        """
        data = [self.base.file_table.item(idx.row(), idx.column()).data(Qt.UserRole)
                for idx in self.base.sel_indexes]
        if self.base.same_cre_version(data):
            self.base.on_merge_highlights()
        else:
            self.base.wrong_cre_version()

    @Slot()
    def on_delete_btn_clicked(self):
        """ The `Delete` button is pressed
        """
        self.base.delete_actions(0)

    @Slot()
    def on_clear_btn_clicked(self):
        """ The `Clear List` button is pressed
        """
        if self.base.current_view == HIGHLIGHTS_VIEW:
            (self.base.high_table.model()  # clear Books view too
             .removeRows(0, self.base.high_table.rowCount()))
        self.base.loaded_paths.clear()
        self.base.reload_highlights = True
        self.base.file_table.model().removeRows(0, self.base.file_table.rowCount())
        self.activate_buttons()

    @Slot()
    def on_db_btn_right_clicked(self):
        """ The context menu of the "Archived" button is pressed
        """
        # noinspection PyArgumentList
        self.db_menu.exec_(QCursor.pos())

    def create_db_menu(self):
        """ Create the database menu
        """
        menu = QMenu(self)

        action = QAction(_("Create new database"), menu)
        action.setIcon(self.base.ico_db_add)
        action.triggered.connect(partial(self.base.change_db, NEW_DB))
        menu.addAction(action)

        action = QAction(_("Reload database"), menu)
        action.setIcon(self.base.ico_refresh)
        action.triggered.connect(partial(self.base.change_db, RELOAD_DB))
        menu.addAction(action)

        action = QAction(_("Change database"), menu)
        action.setIcon(self.base.ico_db_open)
        action.triggered.connect(partial(self.base.change_db, CHANGE_DB))
        menu.addAction(action)
        return menu

    def change_view(self):
        """ Changes what is shown in the app
        """
        new = self.update_archived() if self.db_btn.isChecked() else self.update_loaded()
        if self.books_view_btn.isChecked():  # Books view
            # self.add_btn_menu(self.base.toolbar.export_btn)
            if self.base.sel_idx:
                item = self.base.file_table.item(self.base.sel_idx.row(),
                                                 self.base.sel_idx.column())
                self.base.on_file_table_itemClicked(item, reset=False)
        else:  # Highlights view
            for btn in [self.base.toolbar.export_btn, self.base.toolbar.delete_btn]:
                self.remove_btn_menu(btn)
            if self.base.reload_highlights and not new:
                self.base.scan_highlights_thread()

        self.base.current_view = (BOOKS_VIEW if self.books_view_btn.isChecked()
                                  else HIGHLIGHTS_VIEW)
        self.base.views.setCurrentIndex(self.base.current_view)
        self.setup_buttons()
        self.activate_buttons()
        if self.base.filter.isVisible():
            self.filter_btn.setChecked(False)
        self.base.filter.show_all()

    def update_loaded(self):
        """ Reloads the previously scanned metadata
        """
        if self.base.db_mode:
            self.base.db_mode = False
            self.base.reload_highlights = True
            self.base.loading_thread(ReLoader, self.base.books2reload, self.base.kor_text)
            return True

    def update_archived(self):
        """ Reloads the archived metadata from the db
        """
        if not self.base.db_mode:
            self.base.books2reload = self.base.loaded_paths.copy()
            self.base.db_mode = True
            self.base.reload_highlights = True
            self.base.read_books_from_db()
            text = _("Loading {} database").format(APP_NAME)
            self.base.loading_thread(DBLoader, self.base.books, text)
            if not len(self.base.books):  # no books in the db
                text = _('There are no books currently in the archive.\nTo add/'
                         'update one or more books, select them in the "Loaded" '
                         'view and in their right-click menu, press "Archive".')
                self.base.popup(_("Info"), text, icon=QMessageBox.Question)
            return True

    def setup_buttons(self):
        """ Shows/Hides toolbar's buttons based on the view selected
        """
        books_view = self.books_view_btn.isChecked()
        db_mode = self.db_btn.isChecked()

        self.scan_btn.setVisible(not db_mode)
        self.merge_btn.setVisible(books_view and not db_mode)
        self.delete_btn.setVisible(books_view)
        self.clear_btn.setVisible(not db_mode)

        if self.base.db_mode:
            self.remove_btn_menu(self.base.toolbar.delete_btn)
        else:
            self.add_btn_menu(self.base.toolbar.delete_btn)
        self.base.status.setVisible(books_view)

    def activate_buttons(self):
        """ Enables/Disables toolbar's buttons based on selection/view
        """
        if self.base.high_table.isVisible():  # Highlights view
            try:
                idx = self.base.sel_high_view[-1]
            except IndexError:
                idx = None
            count = self.base.high_table.rowCount()
        else:
            idx = self.base.sel_idx
            count = self.base.file_table.rowCount()
        if idx:
            row = idx.row()
            if self.base.high_table.isVisible():  # Highlights view
                data = self.base.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
                book_exists = isfile(data["path"])
            else:
                book_exists = self.base.file_table.item(row, TYPE).data(Qt.UserRole)[1]
        else:
            book_exists = False

        self.export_btn.setEnabled(bool(idx))
        self.open_btn.setEnabled(book_exists)
        self.delete_btn.setEnabled(bool(idx))
        self.clear_btn.setEnabled(bool(count))

        self.merge_btn.setEnabled(False)
        if len(self.base.sel_indexes) == 2:  # check if we can sync/merge
            idx1, idx2 = self.base.sel_indexes
            data1 = self.base.file_table.item(idx1.row(), idx1.column()).data(Qt.UserRole)
            path1 = self.base.file_table.item(idx1.row(), TYPE).data(Qt.UserRole)[0]
            data2 = self.base.file_table.item(idx2.row(), idx2.column()).data(Qt.UserRole)
            path2 = self.base.file_table.item(idx2.row(), TYPE).data(Qt.UserRole)[0]
            self.merge_btn.setEnabled(self.base.same_book(data1, data2, path1, path2))

    @staticmethod
    def add_btn_menu(btn):
        """ Adds a menu arrow to a toolbar button

        :type btn: QToolButton
        :param btn: The button to change
        """
        btn.setStyleSheet("")
        btn.setPopupMode(QToolButton.MenuButtonPopup)

    @staticmethod
    def remove_btn_menu(btn):
        """ Removes the menu arrow from a toolbar button

        :type btn: QToolButton
        :param btn: The button to change
        """
        btn.setStyleSheet("QToolButton::menu-indicator{width:0px;}")
        btn.setPopupMode(QToolButton.DelayedPopup)

    @Slot()
    def on_about_btn_clicked(self):
        """ The `About` button is pressed
        """
        self.base.about.create_text()
        self.base.about.show()


class Filter(QDialog, Ui_Filter):

    def __init__(self, parent=None):
        super(Filter, self).__init__(parent)
        self.setupUi(self)
        # Remove the question mark widget from dialog
        self.setWindowFlags(self.windowFlags() ^
                            Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(_("Filter").format(APP_NAME))
        self.base = parent

    def keyPressEvent(self, event):
        """ Handles the key press events

        :type event: QKeyEvent
        :param event: The key press event
        """
        key, mod = event.key(), event.modifiers()
        # print(key, mod, QKeySequence(key).toString())
        if mod == Qt.ControlModifier:  # if control is pressed
            if key == Qt.Key_F:
                self.close()
                return True
        if key == Qt.Key_Escape:
            self.close()
            return True

    @Slot()
    def on_filter_txt_returnPressed(self):
        self.on_filter()

    @Slot()
    def on_filter_btn_clicked(self):
        """ The `Filter` button is pressed
        """
        self.filtered_lbl.setText("")
        self.on_filter()

    def on_filter(self):
        """ Filter the table's rows
        """
        txt = self.filter_txt.text().lower()
        filtered = 0
        if self.base.toolbar.books_view_btn.isChecked():
            row_count = self.base.file_table.rowCount()
            for row in range(row_count):
                title = self.base.file_table.item(row, TITLE).data(0)
                if title == _("NO TITLE FOUND"):
                    title = ""
                data = self.base.file_table.item(row, TITLE).data(Qt.UserRole)
                highlights = self.base.get_highlights_from_data(data)

                if self.filter_box.currentIndex() == FILTER_ALL:
                    if txt in title.lower():
                        self.base.file_table.setRowHidden(row, False)
                        continue
                    for high in highlights:
                        if txt in high["text"].lower() or txt in high["comment"].lower():
                            self.base.file_table.setRowHidden(row, False)
                            break
                    else:
                        self.base.file_table.setRowHidden(row, True)
                        filtered += 1
                elif self.filter_box.currentIndex() == FILTER_HIGH:
                    for high in highlights:
                        if txt in high["text"].lower():
                            self.base.file_table.setRowHidden(row, False)
                            break
                    else:
                        self.base.file_table.setRowHidden(row, True)
                        filtered += 1
                elif self.filter_box.currentIndex() == FILTER_COMM:
                    for high in highlights:
                        if txt in high["comment"].lower():
                            self.base.file_table.setRowHidden(row, False)
                            break
                    else:
                        self.base.file_table.setRowHidden(row, True)
                        filtered += 1
                elif self.filter_box.currentIndex() == FILTER_TITLES:
                    if txt in title.lower():
                        self.base.file_table.setRowHidden(row, False)
                    else:
                        self.base.file_table.setRowHidden(row, True)
                        filtered += 1
        else:
            row_count = self.base.high_table.rowCount()
            for row in range(row_count):
                title = self.base.high_table.item(row, TITLE_H).data(0)
                if title == _("NO TITLE FOUND"):
                    title = ""
                high_txt = self.base.high_table.item(row, HIGHLIGHT_H).data(0)
                high_comm = self.base.high_table.item(row, COMMENT_H).data(0)

                if self.filter_box.currentIndex() == FILTER_ALL:
                    if (txt in title.lower() or txt in high_txt.lower()
                            or txt in high_comm.lower()):
                        self.base.high_table.setRowHidden(row, False)
                    else:
                        self.base.high_table.setRowHidden(row, True)
                        filtered += 1
                elif self.filter_box.currentIndex() == FILTER_HIGH:
                    if txt in high_txt.lower():
                        self.base.high_table.setRowHidden(row, False)
                    else:
                        self.base.high_table.setRowHidden(row, True)
                        filtered += 1
                elif self.filter_box.currentIndex() == FILTER_COMM:
                    if txt in high_comm.lower():
                        self.base.high_table.setRowHidden(row, False)
                    else:
                        self.base.high_table.setRowHidden(row, True)
                        filtered += 1
                elif self.filter_box.currentIndex() == FILTER_TITLES:
                    if txt in title.lower():
                        self.base.high_table.setRowHidden(row, False)
                        continue
                    else:
                        self.base.high_table.setRowHidden(row, True)
                        filtered += 1
        self.filtered_lbl.setText(_("Showing {}/{}").format(row_count - filtered,
                                                            row_count))

    @Slot()
    def on_clear_filter_btn_clicked(self):
        """ The `Clear` button is pressed
        """
        self.filter_txt.clear()
        self.filtered_lbl.setText("")
        self.show_all()

    def show_all(self):
        """ Shows all the rows of a table
        """
        if self.base.toolbar.books_view_btn.isChecked():
            table = self.base.file_table
        else:
            table = self.base.high_table

        for row in range(table.rowCount()):
            table.setRowHidden(row, False)

    def closeEvent(self, event):
        """ Accepts or rejects the `close` command

        :type event: QCloseEvent
        :parameter event: The `exit` event
        """
        self.base.toolbar.filter_btn.setChecked(False)
        self.on_clear_filter_btn_clicked()
        event.accept()


class About(QDialog, Ui_About):

    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        self.setupUi(self)
        # Remove the question mark widget from dialog
        self.setWindowFlags(self.windowFlags() ^
                            Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(_("About {}").format(APP_NAME))
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
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:14.0) "
                                "Gecko/20100101 Firefox/24.0.1",
                  "Referer": "http://whateveritis.com"}
        url = "http://www.noembryo.com/apps.php?kohighlights"
        try:
            html_text = requests.get(url, headers=header).content
        except requests.exceptions.ConnectionError:
            return
        soup_text = BeautifulSoup(html_text, "html.parser")
        results = soup_text.findAll(name="p")
        results = "".join([str(i) for i in results])
        match = re.search(r"\d+\.\d+\.\d+\.\d+", results, re.DOTALL)
        try:
            version_new = match.group(0)
        except AttributeError:  # no match found
            version_new = "0.0.0.0"
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
                <p align="center"><b>{3}</b> is a utility for viewing
                    <a href="https://github.com/koreader/koreader">Koreader</a>'s
                    highlights<br/>and/or export them to simple text</p>
                <p align="center">Version {1}</p>
                <p align="center">Visit
                    <a href="https://github.com/noEmbryo/KoHighlights">
                    {3} page at GitHub</a>, or</p>
                <p align="center"><a href="http://www.noembryo.com/apps.php?app_index">
                   noEmbryo's page</a> with more Apps and stuff...</p>
                <p align="center">Use it and if you like it, consider to
                <p align="center"><a href="https://www.paypal.com/cgi-bin/webscr?
                    cmd=_s-xclick &hosted_button_id=RBYLVRYG9RU2S">
                <img src="{2}" alt="PayPal Button"
                    width="142" height="27" border="0"></a></p>
                <p align="center">&nbsp;</p></td>
            </tr>
          </table>
        </center>
        </body>""").format(splash, self.base.version, paypal, APP_NAME)
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
        for i in [self.act_page, self.act_date, self.act_text, self.act_chapter,
                  self.act_comment]:
            self.show_menu.addAction(i)
            # noinspection PyUnresolvedReferences
            i.triggered.connect(self.on_show_items)
            i.setChecked(True)

        action = QAction(_("Date Format"), self.show_menu)
        action.setIcon(QIcon(":/stuff/calendar.png"))
        action.triggered.connect(self.set_date_format)
        self.show_menu.addAction(action)

        sort_menu = QMenu(self)
        ico_sort = QIcon(":/stuff/sort.png")
        group = QActionGroup(self)

        action = QAction(_("Date"), sort_menu)
        action.setCheckable(True)
        action.setChecked(not self.base.high_by_page)
        action.triggered.connect(self.base.set_highlight_sort)
        action.setData(False)
        group.addAction(action)
        sort_menu.addAction(action)

        action = QAction(_("Page"), sort_menu)
        action.setCheckable(True)
        action.setChecked(self.base.high_by_page)
        action.triggered.connect(self.base.set_highlight_sort)
        action.setData(True)
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

    def set_date_format(self):
        """ Changes the date format
        """
        popup = self.base.popup(_("Set custom Date format"),
                                _("The default format is %Y-%m-%d %H:%M:%S\nUse these "
                                  "symbols in any order, combined with any other "
                                  "character.\nFor more info about the supported symbols "
                                  "press Help."),
                                icon=QMessageBox.Information, buttons=2,
                                extra_text=_("Help"), input_text=self.base.date_format,
                                button_text=(_("OK"), _("Use Default")))
        if popup.buttonRole(popup.clickedButton()) == QMessageBox.AcceptRole:
            self.base.date_format = popup.typed_text
        elif popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
            self.base.date_format = DATE_FORMAT
        elif popup.buttonRole(popup.clickedButton()) == QMessageBox.ApplyRole:
            webbrowser.open("https://docs.python.org/2.7/library/datetime.html"
                            "#strftime-strptime-behavior")
        self.on_show_items()

    def animation(self, run):
        """ Creates or deletes temporary files and folders

        :type run: bool
        :param run: Start/stop animation
        """
        # if action == "start":
        if run:
            self.anim_lbl.show()
            self.wait_anim.start()
        else:
            self.anim_lbl.hide()
            self.wait_anim.stop()


# if __name__ == "__main__":
#     with open("secondary.py", str("r")) as py_text:
#         import re
#         script = py_text.read()
#         result = tuple(re.findall(r"class (.+)\(", script))
#         print("__all__ = {}".format(result))
