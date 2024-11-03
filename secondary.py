# coding=utf-8
from boot_config import *
from boot_config import _

import os, re
import webbrowser
import platform
from functools import partial
from ntpath import normpath
from os.path import join, basename, splitext, isfile, abspath
from copy import deepcopy
from pprint import pprint

if QT5:  # ___ ______________ DEPENDENCIES __________________________
    from PySide2.QtCore import (QObject, Qt, Signal, QPoint, Slot, QSize, QEvent, QRect,
                                QTimer, QUrl)
    from PySide2.QtGui import (QFont, QMovie, QIcon, QCursor, QPalette, QColor, QPixmap,
                               QPainter, QPen)
    from PySide2.QtWidgets import (QTableWidgetItem, QTableWidget, QMessageBox, QLineEdit,
                                   QApplication, QWidget, QDialog, QFileDialog,
                                   QStyleFactory, QActionGroup, QMenu, QAction,
                                   QToolButton, QCheckBox)
else:  # Qt6
    from PySide6.QtCore import (QObject, Qt, Signal, QEvent, QPoint, Slot, QSize, QRect,
                                QTimer, QUrl)
    from PySide6.QtGui import (QFont, QActionGroup, QAction, QCursor, QMovie, QIcon,
                               QPalette, QColor, QPixmap, QPainter, QPen)
    from PySide6.QtWidgets import (QTableWidgetItem, QTableWidget, QApplication,
                                   QLineEdit, QToolButton, QWidget, QMenu, QFileDialog,
                                   QDialog, QMessageBox, QCheckBox, QStyleFactory)
import requests
from bs4 import BeautifulSoup
from future.moves.urllib.parse import unquote, urlencode
from packaging.version import parse as version_parse
from slppu import slppu as lua  # https://github.com/noembryo/slppu

__author__ = "noEmbryo"


def decode_data(path):
    """ Converts a lua table to a Python dict

    :type path: str|unicode
    :param path: The path to the lua file
    """
    with open(path, "r", encoding="utf8", newline="\n") as txt_file:
        header, data = txt_file.read().split("\n", 1)
        data = lua.decode(data[7:].replace("--", "—"))
        if type(data) is dict:
            data["original_header"] = header
            return data


def encode_data(path, data):
    """ Converts a Python dict to a lua table

    :type path: str|unicode
    :param path: The path to the lua file
    :type data: dict
    :param data: The dictionary to be encoded as lua table
    """
    with open(path, "w+", encoding="utf8", newline="") as txt_file:
        lua_text = f'{data.pop("original_header", "")}\nreturn '
        lua_text += lua.encode(data)
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


def create_chapter_map(all_chapter_parts):
    """ Create the chapter map

    :type all_chapter_parts: list
    :param all_chapter_parts: The list of all chapter parts
    """
    chapter_map = {}

    # Build the chapter map
    for chapter_parts in all_chapter_parts:
        current_level = chapter_map

        highlight = chapter_parts[-1]["Highlight"]
        parts = chapter_parts[:-1]
        for part in parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

        # Initialize highlights list if not present
        if "highlight" not in current_level:
            current_level["highlight"] = []
        current_level["highlight"].append(highlight)

    # Construct the final chapter map
    final_chapter_map = []
    for part, chapters in chapter_map.items():
        part_structure = [part]
        for chapter, details in chapters.items():
            chapter_structure = [chapter]

            if "highlight" in details:  # If highlights exist, add them to the structure
                chapter_structure.extend(details["highlight"])

            chapter_structure.extend(build_structure(details))
            part_structure.append(chapter_structure)
        final_chapter_map.append(part_structure)

    return final_chapter_map


def build_structure(mapping):
    """ Construct the final nested list structure

    :type mapping: dict
    :param mapping: The mapping to be processed
    """
    result = []
    for key, value in mapping.items():
        if key != "highlight":
            sub_structure = [key]
            # If there are highlights, include them in the structure
            if "highlight" in value and value["highlight"]:
                sub_structure.extend(value["highlight"])
            # Recursively build sub-structures for deeper levels
            sub_structure.extend(build_structure(value))
            result.append(sub_structure)
    return result


def generate_markdown(chapter_list, level=1, max_level=6):
    """ Generate a markdown string from a chapter list
    """
    markdown = ""
    for item in chapter_list:
        if isinstance(item, list):
            # Determine the appropriate heading level
            current_level = level if level <= max_level else max_level
            markdown += f"{'#' * current_level} {item[0]}\n\n"
            # Recursively process the sub-chapters
            markdown += generate_markdown(item[1:], level + 1, max_level)
        else:
            # Add highlight texts without any heading
            markdown += f"{item}\n"
    return markdown


def get_book_text(args):
    """ Create the book's contents
    """
    title = args["title"]
    authors = args["authors"]
    highlights = args["highlights"]
    format_ = args["format_"]
    line_break = args["line_break"]
    space = args["space"]
    text = args["text"]

    custom_template = args.get("custom_template", {})
    customize = custom_template.get("active")
    templ_head = custom_template.get("templ_head")
    templ_body = custom_template.get("templ_body")
    split_chapters = custom_template.get("split_chapters")
    head_min = custom_template.get("head_min")
    head_max = custom_template.get("head_max")

    nl = os.linesep
    if format_ == ONE_TEXT:
        name = title
        if authors:
            name = f"{authors} - {title}"
        line = "-" * 80
        text += line + nl + name + nl + line + nl
        highlights = [i[HI_PAGE] + space + i[HI_DATE] + line_break
                      + (f"[{i[HI_CHAPTER]}]{nl}" if i[HI_CHAPTER] else "")
                      + i[HI_TEXT] + i[HI_COMMENT] for i in highlights]
        text += (nl * 2).join(highlights) + nl * 2
    elif format_ == ONE_HTML:
        text += BOOK_BLOCK % {"title": title, "authors": authors}
        for high in highlights:
            date_text, high_comment, high_text, page_text, chapter = high
            text += HIGH_BLOCK % {"page": page_text, "date": date_text,
                                  "highlight": high_text, "comment": high_comment,
                                  "chapter": chapter}
        text += "</div>\n"
    elif format_ == ONE_CSV:
        for high in highlights:
            date_text, high_comment, high_text, page_text, chapter = high
            data = {"title": title, "authors": authors, "page": page_text,
                    "date": date_text, "text": high_text, "comment": high_comment,
                    "chapter": chapter}
            # data = {k.encode("utf8"): v.encode("utf8") for k, v in data.items()}
            text += get_csv_row(data) + "\n"
    elif format_ == ONE_MD:
        highs = []
        if not customize:
            text += f"\n---\n## {title}  \n##### {authors}  \n---\n"
            for i in highlights:
                comment = i[HI_COMMENT].replace(nl, "  " + nl)
                # if comment:
                #     comment = "  " + comment
                chapter = i[HI_CHAPTER]
                if chapter:
                    chapter = f"***{chapter}***{nl}{nl}".replace(nl, "  " + nl)
                high = i[HI_TEXT].replace(nl, "  " + nl)
                hi_text = ("*" + i[HI_PAGE] + space + i[HI_DATE] + line_break + chapter +
                           high + comment + "  \n&nbsp;  \n")
                highs.append(hi_text.replace("-", "\\-"))
        else:  # use custom markdown template
            text += templ_head.format(title, authors)
            do_split = False
            if split_chapters:
                for i in highlights:
                    if SPLITTER in i[HI_CHAPTER]:
                        do_split = True
                        break
            if do_split:
                all_chapter_parts = []
                for idx, i in enumerate(highlights):
                    if SPLITTER in i[HI_CHAPTER]:
                        chap_parts = [j.rstrip(SPLITTER)
                                      for j in i[HI_CHAPTER].split(SPLITTER)]
                        # get the highlight's formated text
                        comment = i[HI_COMMENT].replace(nl, "  " + nl).replace("-", "\\-")
                        high = i[HI_TEXT].replace(nl, "  " + nl).replace("-", "\\-")
                        date_ = i[HI_DATE].replace("-", "\\-")
                        hi_text = templ_body.format(date_, comment, high, i[HI_PAGE], "")

                        chap_parts.append({"Highlight": hi_text})
                        all_chapter_parts.append(chap_parts)
                chapter_map = create_chapter_map(all_chapter_parts)
                text += generate_markdown(chapter_map, head_min, head_max)
            else:
                for i in highlights:
                    comment = i[HI_COMMENT].replace(nl, "  " + nl).replace("-", "\\-")
                    # comment = "  " + comment if comment.strip() else ""
                    high = i[HI_TEXT].replace(nl, "  " + nl).replace("-", "\\-")
                    date_ = i[HI_DATE].replace("-", "\\-")
                    highs.append(templ_body.format(date_, comment, high,
                                                   i[HI_PAGE], i[HI_CHAPTER]))
        text += nl.join(highs) + "\n---\n"
    return text


def save_file(args):
    """ Saves the book's exported file
    """
    ext = text = ""
    encoding = "utf-8"
    title = name = args["title"]
    authors = args["authors"]
    format_ = args["format_"]
    if authors:
        name = f"{authors} - {name}"
    if format_ == MANY_TEXT:
        ext = ".txt"
    elif format_ == MANY_HTML:
        ext = ".html"
        text = HTML_HEAD
    elif format_ == MANY_CSV:
        ext = ".csv"
        text = CSV_HEAD
        encoding = "utf-8-sig"
    elif format_ == MANY_MD:
        ext = ".md"
    args["text"] = text

    filename = join(args["dir_path"], sanitize_filename(name))
    if NO_TITLE in title:  # don't overwrite unknown title files
        while isfile(filename + ext):
            match = re.match(r"(.+?) \[(\d+?)]$", filename)
            if match:
                filename = "{} [{:02}]".format(match.group(1), int(match.group(2)) + 1)
            else:
                filename += " [01]"
    filename = filename + ext

    with open(filename, "w+", encoding=encoding, newline="") as text_file:
        args["format_"] += 1  # the format is changed to the MERGED file, to get the text
        text = get_book_text(args)
        if format_ == MANY_HTML:
            text += "\n</body>\n</html>"
        text_file.write(text)


__all__ = ("decode_data", "encode_data", "sanitize_filename", "get_csv_row",
           "get_book_text", "save_file", "XTableWidgetIntItem", "XTableWidgetPercentItem",
           "XTableWidgetTitleItem", "DropTableWidget", "XMessageBox", "About", "AutoInfo",
           "ToolBar", "TextDialog", "Status", "LogStream", "Scanner", "HighlightScanner",
           "ReLoader", "DBLoader", "XToolButton", "Filter", "XThemes", "XIconGlyph",
           "SyncGroup", "SyncItem", "XTableWidget", "Prefs")


# ___ _______________________ SUBCLASSING ___________________________


class XTableWidgetIntItem(QTableWidgetItem):
    """ Sorts numbers writen as strings (after 1 is 2 not 11)
    """

    def __lt__(self, value):
        parts1 = re.split(r'(\d+)', self.data(Qt.DisplayRole))
        parts2 = re.split(r'(\d+)', value.data(Qt.DisplayRole))

        for part1, part2 in zip(parts1, parts2):
            if part1 != part2:
                if part1.isdigit() and part2.isdigit():
                    return int(part1) < int(part2)
                else:
                    return part1 < part2

        # If we reach this point, it means that the string have a common prefix,
        # so we need to check the lengths of the remaining parts
        return len(parts1) < len(parts2)


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
        # if event.mimeData().hasUrls and not self.app.base.db_mode:
        if event.mimeData().hasUrls:
            if self.app.base.db_mode:
                links = [i.toLocalFile() for i in event.mimeData().urls()]
                if len(links) == 1 and splitext(links[0])[1].lower() == ".db":
                    event.accept()
                    return True
                event.ignore()
                return False
            else:
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


class XTableWidget(QTableWidget):
    """ QTableWidget with support for drag and drop move of rows that contain widgets
    """

    def __init__(self, *args, **kwargs):
        super(XTableWidget, self).__init__(*args, **kwargs)
        self.viewport().setAcceptDrops(True)
        self.selection = self.selectionModel()
        self.base = None

    def dropEvent(self, event):
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)
            # rows = sorted(set(i.row() for i in self.selectedItems()))
            rows = sorted(set(i.row() for i in self.selection.selectedRows()))
            rows_to_move = []
            for row in rows:
                items = dict()
                for col in range(self.columnCount()):
                    # get the widget or item of current cell
                    widget = self.cellWidget(row, col)
                    if isinstance(widget, type(None)):  # a normal QTableWidgetItem
                        items[col] = {"kind": "QTableWidgetItem",
                                      "item": QTableWidgetItem(self.item(row, col))}
                    else:  # another kind of widget.
                        # So we catch the widget's unique characteristics
                        items[col] = {"kind": "QWidget", "item": widget.data}
                rows_to_move.append(items)

            for row in reversed(rows):
                self.removeRow(row)
                # if row < drop_row:
                #     drop_row -= 1
            for row, data in enumerate(rows_to_move):
                row += drop_row
                self.insertRow(row)

                for col, info in data.items():
                    if info["kind"] == "QTableWidgetItem":
                        # for QTableWidgetItem we can re-create the item directly
                        self.setItem(row, col, info["item"])
                    else:  # for other widgets we call
                        # the parent's callback function to get them
                        widget = self.base.create_sync_widget(info["item"])
                        widget.idx = row
                        self.base.sync_table.setRowHeight(row, widget.sizeHint().height())
                        self.setCellWidget(row, col, widget)

            self.base.update_sync_groups()
            event.accept()
        super(XTableWidget, self).dropEvent(event)

    def drop_on(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount() - 1
        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def is_below(self, pos, index):
        rect = self.visualRect(index)
        margin = 2
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
        # noinspection PyTypeChecker
        return rect.contains(pos, True) and not (int(self.model().flags(
            index)) & Qt.ItemIsDropEnabled) and pos.y() >= rect.center().y()


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
        self.layout().addWidget(widget, 1, 2)


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
    found = Signal(str)
    finished = Signal()

    def __init__(self, path):
        super(Scanner, self).__init__()
        self.path = path

    def process(self):
        try:
            for dir_path, dirs, files in os.walk(self.path):
                if dir_path.lower().endswith(".sdr"):  # a book's metadata folder
                    if dir_path.lower().endswith("evernote.sdr"):
                        continue
                    for file_ in files:  # get the .lua file not the .old (backup)
                        if splitext(file_)[1].lower() == ".lua":
                            if file_.lower() == "custom_metadata.lua":
                                continue  # no highlights in custom_metadata.lua
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
        self.finished.emit()


class ReLoader(QObject):
    found = Signal(str)
    finished = Signal()

    def __init__(self, paths):
        super(ReLoader, self).__init__()
        self.paths = paths

    def process(self):
        # print("Loading data from files")
        for path in self.paths:
            self.found.emit(path)
        self.finished.emit()


class DBLoader(QObject):
    found = Signal(str, dict, str)
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
            meta_path = self.base.file_table.item(row, PATH).data(0)
            highlights = self.base.get_highlights_from_data(data, path, meta_path)
            for highlight in highlights:
                self.found.emit(highlight)
        self.finished.emit()


class XThemes(QObject):
    """ Dark and light theme palettes
    """

    def __init__(self, parent=None):
        super(XThemes, self).__init__(parent)

        # noinspection PyArgumentList
        self.app = QApplication.instance()
        self.def_style = str(self.app.style())
        # noinspection PyArgumentList
        themes = QStyleFactory.keys()
        if "Fusion" in themes:
            self.app_style = "Fusion"
        elif "Plastique" in themes:
            self.app_style = "Plastique"
        else:
            self.app_style = self.def_style
        self.def_colors = self.get_current()
        # self.def_palette = self.app.palette()

    def dark(self):
        """ Apply a dark theme
        """

        dark_palette = QPalette()

        # base
        text = 250
        dark_palette.setColor(QPalette.WindowText, QColor(text, text, text))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.Light, QColor(text, text, text))
        dark_palette.setColor(QPalette.Midlight, QColor(90, 90, 90))
        dark_palette.setColor(QPalette.Dark, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.Text, QColor(text, text, text))
        dark_palette.setColor(QPalette.BrightText, QColor(text, text, text))
        dark_palette.setColor(QPalette.ButtonText, QColor(text, text, text))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        # dark_palette.setColor(QPalette.Text, QColor(180, 180, 180))
        # dark_palette.setColor(QPalette.BrightText, QColor(180, 180, 180))
        # dark_palette.setColor(QPalette.ButtonText, QColor(180, 180, 180))
        # dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.Shadow, QColor(10, 10, 10))
        # dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(20, 50, 80))
        dark_palette.setColor(QPalette.HighlightedText, QColor(text, text, text))
        dark_palette.setColor(QPalette.Link, QColor(56, 252, 196))
        dark_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipText, QColor(text, text, text))
        dark_palette.setColor(QPalette.LinkVisited, QColor(80, 80, 80))

        # disabled
        gray = QColor(100, 100, 100)
        dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, gray)
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, gray)
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, gray)
        dark_palette.setColor(QPalette.Disabled, QPalette.HighlightedText, gray)
        dark_palette.setColor(QPalette.Disabled, QPalette.Highlight,
                              QColor(80, 80, 80))

        self.app.style().unpolish(self.app)
        self.app.setPalette(dark_palette)
        # self.app.setStyle("Fusion")
        self.app.setStyle(self.app_style)

    def light(self):
        """ Apply a light theme
        """

        light_palette = QPalette()

        # base
        light_palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        # light_palette.setColor(QPalette.Light, QColor(180, 180, 180))
        # light_palette.setColor(QPalette.Midlight, QColor(200, 200, 200))
        # light_palette.setColor(QPalette.Dark, QColor(225, 225, 225))
        light_palette.setColor(QPalette.Dark, QColor(180, 180, 180))
        light_palette.setColor(QPalette.Midlight, QColor(200, 200, 200))
        light_palette.setColor(QPalette.Light, QColor(250, 250, 250))
        light_palette.setColor(QPalette.Text, QColor(0, 0, 0))
        light_palette.setColor(QPalette.BrightText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Base, QColor(237, 237, 237))
        light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
        light_palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        # light_palette.setColor(QPalette.Highlight, QColor(76, 163, 224))
        light_palette.setColor(QPalette.Highlight, QColor(200, 230, 255))
        light_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Link, QColor(0, 162, 232))
        light_palette.setColor(QPalette.AlternateBase, QColor(225, 225, 225))
        light_palette.setColor(QPalette.ToolTipBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.LinkVisited, QColor(222, 222, 222))

        # disabled
        light_palette.setColor(QPalette.Disabled, QPalette.WindowText,
                               QColor(115, 115, 115))
        light_palette.setColor(QPalette.Disabled, QPalette.Text,
                               QColor(115, 115, 115))
        light_palette.setColor(QPalette.Disabled, QPalette.ButtonText,
                               QColor(115, 115, 115))
        light_palette.setColor(QPalette.Disabled, QPalette.Highlight,
                               QColor(190, 190, 190))
        light_palette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                               QColor(115, 115, 115))

        self.app.style().unpolish(self.app)
        self.app.setPalette(light_palette)
        # self.app.setStyle("Fusion")
        self.app.setStyle(self.app_style)

    def normal(self):
        """ Apply the normal theme
        """
        normal_palette = QPalette()

        normal_palette.setColor(QPalette.WindowText, self.def_colors["WindowText"])
        normal_palette.setColor(QPalette.Button, self.def_colors["Button"])
        normal_palette.setColor(QPalette.Light, self.def_colors["Light"])
        normal_palette.setColor(QPalette.Midlight, self.def_colors["Midlight"])
        normal_palette.setColor(QPalette.Dark, self.def_colors["Dark"])
        normal_palette.setColor(QPalette.Text, self.def_colors["Text"])
        normal_palette.setColor(QPalette.BrightText, self.def_colors["BrightText"])
        normal_palette.setColor(QPalette.ButtonText, self.def_colors["ButtonText"])
        normal_palette.setColor(QPalette.Base, self.def_colors["Base"])
        normal_palette.setColor(QPalette.Window, self.def_colors["Window"])
        normal_palette.setColor(QPalette.Shadow, self.def_colors["Shadow"])
        normal_palette.setColor(QPalette.Highlight, self.def_colors["Highlight"])
        normal_palette.setColor(QPalette.HighlightedText,
                                self.def_colors["HighlightedText"])
        normal_palette.setColor(QPalette.Link, self.def_colors["Link"])
        normal_palette.setColor(QPalette.AlternateBase,
                                self.def_colors["AlternateBase"])
        normal_palette.setColor(QPalette.ToolTipBase, self.def_colors["ToolTipBase"])
        normal_palette.setColor(QPalette.ToolTipText, self.def_colors["ToolTipText"])
        normal_palette.setColor(QPalette.LinkVisited, self.def_colors["LinkVisited"])

        # # disabled
        # normal_palette.setColor(QPalette.Disabled, QPalette.WindowText,
        #                         QColor(115, 115, 115))
        # normal_palette.setColor(QPalette.Disabled, QPalette.Text,
        #                         QColor(115, 115, 115))
        # normal_palette.setColor(QPalette.Disabled, QPalette.ButtonText,
        #                         QColor(115, 115, 115))
        # normal_palette.setColor(QPalette.Disabled, QPalette.Highlight,
        #                         QColor(190, 190, 190))
        # normal_palette.setColor(QPalette.Disabled, QPalette.HighlightedText,
        #                         QColor(115, 115, 115))

        self.app.style().unpolish(self.app.base)
        self.app.setPalette(normal_palette)
        # self.app.setPalette(self.def_palette)
        self.app.setStyle(self.def_style)

    @staticmethod
    def get_current():
        """ Return the current theme's data
        """
        light_palette = QPalette()
        data = {'WindowText': (light_palette.color(QPalette.WindowText)),
                'Button': (light_palette.color(QPalette.Button)),
                'Light': (light_palette.color(QPalette.Light)),
                'Midlight': (light_palette.color(QPalette.Midlight)),
                'Dark': (light_palette.color(QPalette.Dark)),
                'Text': (light_palette.color(QPalette.Text)),
                'BrightText': (light_palette.color(QPalette.BrightText)),
                'ButtonText': (light_palette.color(QPalette.ButtonText)),
                'Base': (light_palette.color(QPalette.Base)),
                'Window': (light_palette.color(QPalette.Window)),
                'Shadow': (light_palette.color(QPalette.Shadow)),
                'Highlight': (light_palette.color(QPalette.Highlight)),
                'HighlightedText': (light_palette.color(QPalette.HighlightedText)),
                'Link': (light_palette.color(QPalette.Link)),
                'AlternateBase': (light_palette.color(QPalette.AlternateBase)),
                'ToolTipBase': (light_palette.color(QPalette.ToolTipBase)),
                'ToolTipText': (light_palette.color(QPalette.ToolTipText)),
                'LinkVisited': (light_palette.color(QPalette.LinkVisited))}
        return data


class XIconGlyph(QObject):
    """ A Font char to QIcon converter

    * Usage in Base:
    QFontDatabase.addApplicationFont(":/stuff/font.ttf")  # add custom font or use existing
    # pprint(QFontDatabase.families())

    self.font_ico = XIconGlyph(self, glyph=None)

    ico = self.font_ico.get_icon({"char": "✓",
                                  "size": (32, 32),
                                  "size_ratio": 1.2,
                                  "offset": (0, -2),
                                  "family": "XFont",
                                  "color": "#FF0000",
                                  "active": "orange",
                                  "hover": (160, 50, 255),
                                  })
    self.tool_btn.setIcon(ico)
    """

    def __init__(self, parent, glyph=None):
        super(XIconGlyph, self).__init__(parent)
        self.char = ""
        self.family = ""
        self.color = parent.palette().text().color().name()  # use the default
        self.active = None
        self.hover = None
        self.disabled = parent.palette().dark().color().name()
        self.icon_size = 16, 16
        self.size_ratio = 1
        self.offset = 0, 0
        self.glyph = glyph
        if glyph:
            self._parse_glyph(glyph)

    def _parse_glyph(self, glyph):
        """ Set the glyph options

        :type glyph: dict
        """
        if self.glyph:
            self.glyph.update(glyph)

        family = glyph.get("family")
        if family:
            self.family = family
        char = glyph.get("char")
        if char:
            self.char = char
        icon_size = glyph.get("size")
        if icon_size:
            self.icon_size = icon_size
        offset = glyph.get("offset")
        if offset:
            self.offset = offset
        size_ratio = glyph.get("size_ratio")
        if size_ratio:
            self.size_ratio = size_ratio
        active = glyph.get("active")
        if active:
            self.active = active
        hover = glyph.get("hover")
        if hover:
            self.hover = hover
        color = glyph.get("color")
        if color:
            self.color = color
        disabled = glyph.get("disabled")
        if disabled:
            self.disabled = disabled

    def _get_char_pixmap(self, color):
        """ Create an icon from a font character

        :type color: str|tuple
        :param color: The color of the icon
        :return: QPixmap
        """
        if isinstance(color, tuple):
            color = QColor(*color)
        else:
            color = QColor(color)
        font = QFont()
        if self.family:
            font.setFamily(self.family)
        font.setPixelSize(self.icon_size[1] * self.size_ratio)

        pixmap = QPixmap(*self.icon_size)
        pixmap.fill(QColor(0, 0, 0, 0))  # fill with transparency

        painter = QPainter(pixmap)
        painter.setFont(font)
        pen = QPen()
        pen.setColor(color)
        painter.setPen(pen)
        painter.drawText(QRect(QPoint(*self.offset), QSize(*self.icon_size)),
                         Qt.AlignCenter | Qt.AlignVCenter, self.char)
        painter.end()
        return pixmap

    def get_icon(self, glyph=None):
        """ Get the icon from the glyph

        :type glyph: dict
        :return: QIcon
        """
        if glyph:
            self._parse_glyph(glyph)

        icon = QIcon()
        icon.addPixmap(self._get_char_pixmap(self.color), QIcon.Normal, QIcon.Off)
        if self.active:  # the checkable down state icon
            icon.addPixmap(self._get_char_pixmap(self.active),
                           QIcon.Active, QIcon.On)
        if self.hover:  # the mouse hover state icon
            icon.addPixmap(self._get_char_pixmap(self.hover),
                           QIcon.Active, QIcon.Off)
        if self.disabled:  # the disabled state icon
            icon.addPixmap(self._get_char_pixmap(self.disabled),
                           QIcon.Disabled, QIcon.Off)
        return icon

# ___ _______________________ GUI STUFF _____________________________


from gui_about import Ui_About
from gui_auto_info import Ui_AutoInfo
from gui_toolbar import Ui_ToolBar
from gui_status import Ui_Status
from gui_edit import Ui_TextDialog
from gui_filter import Ui_Filter
from gui_sync_group import Ui_SyncGroup
from gui_sync_item import Ui_SyncItem
from gui_prefs import Ui_Prefs
from gui_edit_template import Ui_EditTemplate


class ToolBar(QWidget, Ui_ToolBar):

    def __init__(self, parent=None):
        """ The Toolbar

        :type parent: Base
        """
        super(ToolBar, self).__init__(parent)
        self.setupUi(self)
        self.base = parent

        self.buttons = (self.scan_btn, self.export_btn, self.open_btn, self.merge_btn,
                        self.delete_btn, self.clear_btn, self.about_btn, self.filter_btn,
                        self.books_view_btn, self.high_view_btn, self.sync_view_btn,
                        self.add_btn, self.prefs_btn)

        self.size_menu = QMenu(self)
        # self.size_menu.aboutToShow.connect(self.create_size_menu)

        self.db_menu = QMenu()
        self.db_menu.setToolTipsVisible(True)
        self.db_menu.aboutToShow.connect(self.create_db_menu)
        self.db_btn.setMenu(self.db_menu)

        for btn in [self.books_view_btn, self.high_view_btn, self.sync_view_btn,
                    self.loaded_btn, self.db_btn]:
            btn.clicked.connect(self.change_view)

    @Slot(QPoint)
    def on_tool_frame_customContextMenuRequested(self, point):
        """ The Toolbar is right-clicked

        :type point: QPoint
        :param point: The point where the right-click happened
        """
        self.size_menu.clear()
        group = QActionGroup(self)
        sizes = (_("Tiny"), 16), (_("Small"), 32), (_("Medium"), 48), (_("Big"), 64)
        for name, size in sizes:
            action = QAction(name, self.size_menu)
            action.setCheckable(True)
            if size == self.base.toolbar_size:
                action.setChecked(True)
            action.triggered.connect(partial(self.set_btn_size, size))
            group.addAction(action)
            self.size_menu.addAction(action)
        if QT6:  # QT6 requires exec() instead of exec_()
            self.size_menu.exec_ = getattr(self.size_menu, "exec")
        self.size_menu.exec_(self.tool_frame.mapToGlobal(point))

    def set_btn_size(self, size):
        """ Changes the Toolbar's icons size

        :type size: int
        :param size: The Icons' size preset
        """
        self.base.toolbar_size = size
        button_size = QSize(size, size)
        half_size = QSize(int(size * .5), int(size * .5))

        for btn in self.buttons:
            btn.setMinimumWidth(size + 10)
            btn.setIconSize(button_size)
            # btn.setStyleSheet("QToolButton:disabled {background-color: rgb(0, 0, 0);}")

        for btn in [self.loaded_btn, self.db_btn]:
            # btn.setMinimumWidth(size + 10)
            btn.setIconSize(half_size)
        # noinspection PyArgumentList
        QApplication.processEvents()

        if self.base.theme in [THEME_NONE_NEW, THEME_DARK_NEW, THEME_LIGHT_NEW]:
            self.base.set_new_icons(menus=False)

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

    @Slot()
    def on_add_btn_clicked(self):
        """ The `Add` sync group button is pressed
        """
        if self.base.current_view == SYNC_VIEW:
            info = {"title": "",
                    "sync_pos": False,
                    "merge": False,
                    "sync_db": True,
                    "items": [{"path": "", "data": {}}],
                    "enabled": True}
            self.base.create_sync_row(info)

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
        if self.base.current_view == SYNC_VIEW:
            if self.base.merge_warning_stop():
                return
            text = _("Synchronize all active Sync groups?")
            popup = self.base.popup(_("Sync"), text, icon=QMessageBox.Question,
                                    buttons=2)
            if popup.buttonRole(popup.clickedButton()) == QMessageBox.AcceptRole:
                changed_total = 0
                for idx in range(self.base.sync_table.rowCount()):
                    group = self.base.sync_table.cellWidget(idx, 0)
                    if group.power_btn.isChecked():
                        changed = self.base.synchronize_group(group, multi=True)
                        if changed:
                            changed_total += 1
                text = _(f"Synchronization process completed\n"
                         f"{changed_total} groups were synchronized")
                self.base.popup(_("Information"), text, QMessageBox.Information)
            return
        data = [self.base.file_table.item(idx.row(), idx.column()).data(Qt.UserRole)
                for idx in self.base.sel_indexes]
        if self.base.same_cre_version(*data):
            self.base.on_merge_highlights()
        else:
            self.base.wrong_cre_version()

    @Slot()
    def on_delete_btn_clicked(self):
        """ The `Delete` button is pressed
        """
        if self.base.current_view == BOOKS_VIEW:
            # self.base.delete_actions(0)
            if not self.base.db_mode:
                self.delete_btn.showMenu()
            else:
                self.base.delete_actions()
        elif self.base.current_view == HIGHLIGHTS_VIEW:
            self.base.on_delete_highlights()
        elif self.base.current_view == SYNC_VIEW:
            for index in sorted(self.base.sel_sync_view)[::-1]:
                row = index.row()
                del self.base.sync_groups[row]
                self.base.sync_table.model().removeRow(row)
            self.base.update_sync_groups()

    @Slot()
    def on_clear_btn_clicked(self):
        """ The `Clear List` button is pressed
        """
        if self.base.current_view == SYNC_VIEW and not self.base.reload_from_sync:
            return
        self.base.loaded_paths.clear()
        self.base.reload_highlights = True
        self.base.file_table.model().removeRows(0, self.base.file_table.rowCount())
        self.base.high_table.model().removeRows(0, self.base.high_table.rowCount())
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
        self.db_menu.clear()
        action = QAction(_("Create new database"), self.db_menu)
        action.setIcon(self.base.ico_db_add)
        action.setToolTip(_("Create a new database file"))
        action.triggered.connect(partial(self.base.change_db, NEW_DB))
        self.db_menu.addAction(action)

        action = QAction(_("Reload database"), self.db_menu)
        action.setIcon(self.base.ico_refresh)
        action.setToolTip(_("Reload the current database"))
        action.triggered.connect(partial(self.base.change_db, RELOAD_DB))
        self.db_menu.addAction(action)

        action = QAction(_("Change database"), self.db_menu)
        action.setIcon(self.base.ico_db_open)
        action.setToolTip(_("Load a different database file"))
        action.triggered.connect(partial(self.base.change_db, CHANGE_DB))
        self.db_menu.addAction(action)

        action = QAction(_("Compact database"), self.db_menu)
        action.setIcon(self.base.ico_db_compact)
        action.setToolTip(_("Compact the database to minimize file size"))
        action.triggered.connect(partial(self.base.vacuum_db, True))
        self.db_menu.addAction(action)

        if QT6:  # QT6 requires exec() instead of exec_()
            self.db_menu.exec_ = getattr(self.db_menu, "exec")

    def change_view(self):
        """ Changes what is shown in the app
        """
        reloaded = False
        if self.base.reload_from_sync or not self.sync_view_btn.isChecked():
            self.base.reload_from_sync = False
            reloaded = (self.update_archived()
                        if self.db_btn.isChecked() else self.update_loaded())
        if self.books_view_btn.isChecked():  # Books view
            self.base.current_view = BOOKS_VIEW
            self.merge_btn.setToolTip(TOOLTIP_MERGE)
            self.merge_btn.setStatusTip(TOOLTIP_MERGE)
            if self.base.sel_idx:
                item = self.base.file_table.item(self.base.sel_idx.row(),
                                                 self.base.sel_idx.column())
                self.base.on_file_table_itemClicked(item, reset=False)
        elif self.high_view_btn.isChecked():  # Highlights view
            self.base.current_view = HIGHLIGHTS_VIEW
            if self.base.reload_highlights and not reloaded:
                self.base.scan_highlights_thread()
        else:  # Sync view
            self.base.current_view = SYNC_VIEW
            self.merge_btn.setToolTip(TOOLTIP_SYNC)
            self.merge_btn.setStatusTip(TOOLTIP_SYNC)

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
            self.base.load_db_rows()
            # text = _(f"Loading {APP_NAME} database")
            # self.base.loading_thread(DBLoader, self.base.books, text)
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
        high_view = self.high_view_btn.isChecked()
        sync_view = self.sync_view_btn.isChecked()
        db_mode = self.db_btn.isChecked()

        self.scan_btn.setVisible(not (db_mode or sync_view))
        self.export_btn.setVisible(not sync_view)
        self.open_btn.setVisible(not sync_view)
        self.add_btn.setVisible(sync_view)
        self.filter_btn.setVisible(not sync_view)
        self.merge_btn.setVisible(sync_view or not (db_mode or high_view))
        # self.delete_btn.setVisible(books_view or sync_view)
        self.clear_btn.setVisible(not (db_mode or sync_view))

        self.mode_grp.setEnabled(not sync_view)

        self.set_btn_menu(self.export_btn, books_view)
        self.set_btn_menu(self.merge_btn, books_view)
        self.set_btn_menu(self.delete_btn, books_view and not db_mode)

    def activate_buttons(self):
        """ Enables/Disables toolbar's buttons based on selection/view
        """
        count = 0
        sync_enable = False
        book_exists = False
        if self.base.current_view == HIGHLIGHTS_VIEW:  # Highlights view
            try:
                idx = self.base.sel_high_view[-1]
            except IndexError:
                idx = None
            count = self.base.high_table.rowCount()
        elif self.base.current_view == BOOKS_VIEW:  # Books view
            idx = self.base.sel_idx
            count = self.base.file_table.rowCount()
            if len(self.base.sel_indexes) == 2:  # check if we can sync/merge
                idx1, idx2 = self.base.sel_indexes
                data1 = self.base.file_table.item(idx1.row(),
                                                  idx1.column()).data(Qt.UserRole)
                path1 = self.base.file_table.item(idx1.row(), TYPE).data(Qt.UserRole)[0]
                data2 = self.base.file_table.item(idx2.row(),
                                                  idx2.column()).data(Qt.UserRole)
                path2 = self.base.file_table.item(idx2.row(), TYPE).data(Qt.UserRole)[0]
                sync_enable = self.base.same_book(data1, data2, path1, path2)
        else:  # Sync view
            try:
                idx = self.base.sel_sync_view[-1]
            except IndexError:
                idx = None
            sync_enable = True

        if idx:
            row = idx.row()
            if self.base.file_table.isVisible():  # Books view
                book_exists = self.base.file_table.item(row, TYPE).data(Qt.UserRole)[1]
            elif self.base.high_table.isVisible():  # Highlights view
                data = self.base.high_table.item(row, HIGHLIGHT_H).data(Qt.UserRole)
                book_exists = isfile(data["path"])

        self.export_btn.setEnabled(bool(idx) and not self.base.sync_table.isVisible())
        self.open_btn.setEnabled(book_exists)
        self.delete_btn.setEnabled(bool(idx))
        self.clear_btn.setEnabled(bool(count))
        self.merge_btn.setEnabled(sync_enable)

    @staticmethod
    def set_btn_menu(btn, status=True):
        """ Adds a menu arrow to a toolbar button

        :type btn: QToolButton
        :param btn: The button to change
        """
        if status:
            btn.setStyleSheet("")
            btn.setPopupMode(QToolButton.MenuButtonPopup)
        else:
            btn.setStyleSheet("QToolButton::menu-indicator{width:0px;}")
            btn.setPopupMode(QToolButton.DelayedPopup)

    @Slot()
    def on_prefs_btn_clicked(self):
        """ The `Preferences` button is pressed
        """
        self.base.prefs.show()

    @Slot()
    def on_about_btn_clicked(self):
        """ The `About` button is pressed
        """
        self.base.about.setup_tabs()
        self.base.about.show()


class Filter(QDialog, Ui_Filter):

    def __init__(self, parent=None):
        """ Initializes the `Filter` dialog

        :type parent: Base
        """
        super(Filter, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(_("Filter"))
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
                if title == NO_TITLE:
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
        elif self.base.toolbar.high_view_btn.isChecked():
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
                        # continue
                    else:
                        self.base.high_table.setRowHidden(row, True)
                        filtered += 1
        else:
            print("SYNC FILTERRRRRRRRRRRRRRRRR")
            return
        self.filtered_lbl.setText(_(f"Showing {row_count - filtered}/{row_count}"))

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


class Prefs(QDialog, Ui_Prefs):

    def __init__(self, parent=None):
        super(Prefs, self).__init__(parent)
        self.setupUi(self)
        self.base = parent
        self.themes = XThemes(parent)
        self.show_items = [self.show_page_chk, self.show_date_chk, self.show_high_chk,
                           self.show_chap_chk, self.show_comm_chk]
        self.edit_template = EditTemplate(parent=self.base)

    @Slot(int)
    def on_theme_box_currentIndexChanged(self, idx):
        """ Selects the app's theme style
        """
        if idx == THEME_NONE_OLD:
            self.themes.normal()
            self.base.set_old_icons()
            if self.base.theme not in [THEME_NONE_OLD, THEME_NONE_NEW]:
                self.no_theme_popup(idx)
                return
        elif idx == THEME_NONE_NEW:
            self.themes.normal()
            self.base.set_new_icons()
            if self.base.theme not in [THEME_NONE_OLD, THEME_NONE_NEW]:
                self.no_theme_popup(idx)
                return
        elif idx == THEME_DARK_OLD:
            self.themes.dark()
            self.base.set_old_icons()
        elif idx == THEME_DARK_NEW:
            self.themes.dark()
            self.base.set_new_icons()
        elif idx == THEME_LIGHT_OLD:
            self.themes.light()
            self.base.set_old_icons()
        elif idx == THEME_LIGHT_NEW:
            self.themes.light()
            self.base.set_new_icons()

        self.base.theme = idx
        self.base.reset_theme_colors()

    def no_theme_popup(self, idx):
        self.base.theme = idx
        self.base.reset_theme_colors()
        self.base.popup(_("Warning"), _("The theme will be fully reset after "
                                        "the application is restarted."))

    @Slot()
    def on_alt_title_sort_chk_stateChanged(self):
        """ Ignore the english articles while sorting by Title
        """
        self.base.toggle_title_sort()

    @Slot()
    def on_show_page_chk_stateChanged(self):
        """ Show the highlight's page number
        """
        self.base.show_items[0] = self.show_page_chk.isChecked()
        self.on_show_items(0)

    @Slot()
    def on_show_date_chk_stateChanged(self):
        """ Show the highlight's date
        """
        self.base.show_items[1] = self.show_date_chk.isChecked()
        self.on_show_items(1)

    @Slot()
    def on_show_high_chk_stateChanged(self):
        """ Show the highlight's text
        """
        self.base.show_items[2] = self.show_high_chk.isChecked()
        self.on_show_items(2)

    @Slot()
    def on_show_chap_chk_stateChanged(self):
        """ Show the highlight's chapter
        """
        self.base.show_items[3] = self.show_chap_chk.isChecked()
        self.on_show_items(3)

    @Slot()
    def on_show_comm_chk_stateChanged(self):
        """ Show the highlight's comment
        """
        self.base.show_items[4] = self.show_comm_chk.isChecked()
        self.on_show_items(4)

    @Slot()
    def on_show_ref_pg_chk_stateChanged(self):
        """ Use the highlight's reference page if exists
        """
        self.base.set_show_ref_pg()

    def on_show_items(self, idx=None):
        """ Show/Hide elements of the highlight info
        """
        if idx is not None:
            self.base.show_items[idx] = self.show_items[idx].isChecked()
        try:
            table_idx = self.base.file_table.selectionModel().selectedRows()[-1]
        except IndexError:  # nothing selected
            return
        item = self.base.file_table.item(table_idx.row(), 0)
        self.base.on_file_table_itemClicked(item)

    @Slot()
    def on_custom_date_btn_clicked(self):
        """ Changes the date format template
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

    @Slot()
    def on_custom_template_chk_stateChanged(self):
        """ Use a custom tamlate for markdown
        """
        self.base.custom_template = self.custom_template_chk.isChecked()

    @Slot()
    def on_custom_template_btn_clicked(self):
        """ Changes the Markdown format template
        """
        self.edit_template.set_default()
        self.edit_template.split_chapters_frm.hide()
        self.edit_template.exec_()

    @Slot(QPoint)
    def on_custom_template_btn_customContextMenuRequested(self, _):
        """ Right click on the Edit template button

        :type _: QPoint
        :param _: The point of the click
        """
        self.edit_template.set_default()
        self.edit_template.split_chapters_frm.show()
        self.edit_template.exec_()

    @Slot(int)
    def on_sort_box_currentIndexChanged(self, idx):
        """ Change the sort order of the Highlight list
        """
        self.base.set_highlight_sort(bool(idx))

    def closeEvent(self, event):
        """ Accepts or rejects the `exit` command

        :type event: QCloseEvent
        :parameter event: The `exit` event
        """
        self.base.settings_save()
        event.accept()


class About(QDialog, Ui_About):

    def __init__(self, parent=None):
        """ Initializes the `About` dialog

        :type parent: Base
        """
        super(About, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(_(f"About {APP_NAME}"))
        self.base = parent

    @Slot()
    def on_about_tabs_currentChanged(self):
        self.setup_tabs()

    def setup_tabs(self):
        if self.about_tabs.currentWidget().objectName() == "info_tab":  # Information
            self.create_text()
        elif self.about_tabs.currentWidget().objectName() == "system_tab":  # System
            self.system_txt.setPlainText(self.get_system_info())
        elif self.about_tabs.currentWidget().objectName() == "usage_tab":  # Usage guide
            self.create_usage_text()

    @Slot(QUrl)
    def on_usage_txt_anchorClicked(self, url):
        """ Handles the link clicks on the track's properties

        :type url: QUrl object
        :parameter url: The link's command
        """
        link = unquote(url.toString())
        if link.startswith("http"):
            webbrowser.open(link)
            return

    @Slot()
    def on_usage_btn_clicked(self):
        """ The `Documentation` button is pressed
        """
        webbrowser.open("https://noembryo.github.io/KoHighlights/")

    @Slot()
    def on_updates_btn_clicked(self):
        """ The `Check for Updates` button is pressed
        """
        self.check_for_updates()

    def check_for_updates(self):
        """ Checks the website for the current version
        """
        version_new = self.get_online_version()
        if not version_new:
            self.base.popup(_("No response!"), _("Version info is unreachable!\n"
                                                 "Please, try again later..."), buttons=1)
            return
        # current_version = LooseVersion(self.base.version)
        current_version = version_parse(self.base.version)
        if version_new > current_version:
            popup = self.base.popup(_("Newer version exists!"),
                                    _(f"There is a newer version (v.{version_new}) online"
                                      f".\nOpen the site to download it now?"),
                                    icon=QMessageBox.Information, buttons=2)
            if popup.clickedButton().text() == "OK":
                webbrowser.open("http://www.noembryo.com/apps.php?katalib")
                self.close()
        elif version_new == current_version:
            self.base.popup(_("No newer version exists!"),
                            _(f"{APP_NAME} is up to date (v.{current_version})"),
                            icon=QMessageBox.Information, buttons=1)
        elif version_new < current_version:
            self.base.popup(_("No newer version exists!"),
                            _(f"It seems that you are using a newer version "
                              f"({current_version})\nthan the one online "
                              f"({version_new})!"), icon=QMessageBox.Question, buttons=1)

    @staticmethod
    def get_online_version():
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:14.0) "
                                "Gecko/20100101 Firefox/24.0.1",
                  "Referer": "http://noembryo.com"}
        url = str("http://www.noembryo.com/apps.php?kohighlights")
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
        # return LooseVersion(version_new)
        return version_parse(version_new)

    def create_text(self):
        # color = self.palette().color(QPalette.WindowText).name()  # for links
        splash = ":/stuff/logo.png"
        paypal = ":/stuff/paypal.png"
        info = _(f"""<body style="font-size:10pt; font-weight:400; font-style:normal">
        <center>
          <table width="100%" border="0">
            <tr>
                <p align="center"><img src="{splash}" width="256" height ="212"></p>
                <p align="center"><b>{APP_NAME}</b> is a utility for viewing
                    <a href="https://github.com/koreader/koreader">KOReader</a>'s
                    highlights<br/>and/or export them to simple text</p>
                <p align="center">Version {self.base.version}</p>
                <p align="center">Visit
                    <a href="https://github.com/noEmbryo/KoHighlights">
                    {APP_NAME} page at GitHub</a>, or</p>
                <p align="center"><a href="http://www.noembryo.com/apps.php?app_index">
                   noEmbryo's page</a> with more Apps and stuff...</p>
                <p align="center">Use it and if you like it, consider to
                <p align="center"><a
                 href="https://www.paypal.com/donate/?hosted_button_id=RBYLVRYG9RU2S">
                <img src="{paypal}" alt="PayPal Button"
                    width="142" height="27" border="0"></a></p>
                <p align="center">&nbsp;</p></td>
            </tr>
          </table>
        </center>
        </body>""")
        self.text_lbl.setText(info)

    def get_system_info(self):
        """ Returns a text with all the system info we have
        """
        text = (f"{APP_NAME}:\t{self.base.version}\t[{platform.architecture()[0]}]\n"
                f"Path:\t{APP_DIR}\n"
                f"Settings path:\t{SETTINGS_DIR}\n"
                f"Database path:\t{abspath(self.base.db_path)}\n"
                f"\n"
                f"Python:\t{platform.python_version()}\n"
                f"Qt version:\t{qVersion()}\n"
                f"Platform:\t{platform.platform()}\n"
                f"System:\t{platform.system()}\n"
                f"Release:\t{platform.release()}\n"
                f"Version:\t{platform.version()}\n"
                f"Name:\t{platform.node()}\n"
                f"Processor:\t{platform.processor()}\n"
                f"Machine:\t{platform.machine()}\n"
                )
        if platform.system() == "Windows":
            text += f"WinInfo:\t{' '.join(platform.win32_ver())}\n"
        return text

    def create_usage_text(self):
        with open(join(APP_DIR, "docs", "index.md"), encoding="utf8") as f:
            text = f.read().replace("./images/", "docs/images/")
            text = text.replace(" (Usage)", "")
            text = text.split("___", 1)[1]
            self.usage_txt.setMarkdown(text)


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
        self.setupUi(self)

        self.base = parent
        # self.on_ok = None

    @Slot()
    def on_ok_btn_clicked(self):
        """ The OK button is pressed
        """
        self.base.edit_comment_ok()


class EditTemplate(QDialog, Ui_EditTemplate):

    def __init__(self, parent=None):
        super(EditTemplate, self).__init__(parent)
        self.setupUi(self)

        self.base = parent
        self.setWindowTitle(_("Edit Markdown template"))
        self.error =False
        head_txt = _("You can use the variables: {0}=Title, {1}=Authors")
        self.head_help_lbl.setText(head_txt)
        body_txt = _("You can use the variables: {0}=Date, {1}=Comment, "
                     "{2}=Highlighted text, {3}=Page number, {4}=Chapter name")
        self.body_help_lbl.setText(body_txt)
        self.setStyleSheet("QGroupBox{font-weight: bold;}")
        self.split_chapters_frm.hide()

    @Slot()
    def on_head_edit_txt_textChanged(self):
        try:
            self.error = False
            self.head_preview_txt.setStyleSheet(self.styleSheet())
            text = self.head_edit_txt.toPlainText().format("Book's Title",
                                                           "Book's Authors")
        except ValueError:  # single '{' encountered, paint text red
            self.error = True
            if self.base.theme in (THEME_DARK_NEW, THEME_DARK_OLD):
                col = "#DD0000"
            else:
                col = "#990000"
            style = self.head_preview_txt.styleSheet() + f'QTextEdit {{color: "{col}";}}'
            self.head_preview_txt.setStyleSheet(style)
            return
        self.head_preview_txt.setMarkdown(text)

    @Slot()
    def on_body_edit_txt_textChanged(self):
        try:
            self.error = False
            self.body_preview_txt.setStyleSheet(self.styleSheet())
            text = (self.body_edit_txt.toPlainText()
                    .format("2023-03-07 14:43:01", "A comment", "The highlighted Text",
                            "420", "Chapter name"))
            # HI_DATE, HI_COMMENT, HI_TEXT, HI_PAGE, HI_CHAPTER
        except (ValueError, IndexError):  # single '{' encountered, paint text red
            self.error = True
            if self.base.theme in (THEME_DARK_NEW, THEME_DARK_OLD):
                col = "#DD0000"
            else:
                col = "#990000"
            style = self.body_preview_txt.styleSheet() + f'QTextEdit {{color: "{col}";}}'
            self.body_preview_txt.setStyleSheet(style)
            return
        self.body_preview_txt.setMarkdown(text)

    @Slot()
    def on_split_chapters_chk_stateChanged(self):
        """ Enables the spliting of chapters for different heading levels
        """
        self.base.split_chapters = self.split_chapters_chk.isChecked()

    @Slot(int)
    def on_head_min_box_currentIndexChanged(self, idx):
        """ Changes the minimum heading level
        """
        self.base.head_min = idx + 1
        if self.base.head_max < self.base.head_min:
            self.head_max_box.setCurrentIndex(idx)

    @Slot(int)
    def on_head_max_box_currentIndexChanged(self, idx):
        """ Changes the maximum heading level
        """
        self.base.head_max = idx + 1
        if self.base.head_min > self.base.head_max:
            self.head_min_box.setCurrentIndex(idx)

    @Slot()
    def on_default_btn_clicked(self):
        """ The Default button is pressed
        """
        self.set_default(clear=True)

    def set_default(self, clear=False):
        """ Sets the default template if empty

        :type clear: bool
        :param clear: Replace the template with the default anyway
        """
        if not clear:
            if not self.head_edit_txt.toPlainText().strip():
                self.head_edit_txt.setText(MD_HEAD)
            if not self.body_edit_txt.toPlainText().strip():
                self.body_edit_txt.setText(MD_HIGH)
        else:
            self.head_edit_txt.setText(MD_HEAD)
            self.body_edit_txt.setText(MD_HIGH)

    @Slot()
    def on_ok_btn_clicked(self):
        """ The OK button is pressed
        """
        if not self.error:
            self.set_default()
            self.base.templ_head = self.head_edit_txt.toPlainText()
            self.base.templ_body = self.body_edit_txt.toPlainText()
            self.close()
        else:
            popup = self.base.popup(_("Error"),
                                    _("There is a single '{' or '}' in the template "
                                      "without its pair."),
                                    icon=QMessageBox.Critical)
            popup.exec_()

    @Slot()
    def on_cancel_btn_clicked(self):
        """ The Cancel button is pressed
        """
        self.head_edit_txt.setText(self.base.templ_head)
        self.body_edit_txt.setText(self.base.templ_body)
        self.close()

    def closeEvent(self, event):
        """ Accepts or rejects the `exit` command

        :type event: QCloseEvent
        :parameter event: The `exit` event
        """
        if self.error:  # don't close if there is an error
            event.ignore()
            return
        event.accept()


class Status(QWidget, Ui_Status):

    def __init__(self, parent=None):
        """ Initializes the StatusBar

        :type parent: Base
        """
        super(Status, self).__init__(parent)
        self.setupUi(self)
        self.base = parent

        self.wait_anim = QMovie(":/stuff/wait.gif")
        self.anim_lbl.setMovie(self.wait_anim)
        self.anim_lbl.hide()

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


class SyncGroup(QWidget, Ui_SyncGroup):

    def __init__(self, parent=None):
        """ Initializes the StatusBar

        :type parent: Base
        """
        super(SyncGroup, self).__init__(parent)
        self.setupUi(self)
        self.base = parent
        self.sync_items = []
        self.items_layout = self.items_frm.layout()

        self.idx = None
        self.data = None
        self.new_format = True
        self.def_btn_icos = []
        self.buttons = [(self.power_btn, "Y"),
                        (self.sync_btn, "E"),
                        (self.refresh_btn, "Z")]
        self.setup_buttons()
        self.setup_icons()

        font = QFont()
        font.setBold(True)
        font.setPointSize(QFont.pointSize(QFont()) + 3)
        self.title_lbl.setFont(font)

        power_color = self.base.palette().button().color().name()
        self.css = ('QFrame#items_frm, QFrame#checks_frm,'
                    'QToolButton {background-color: "%s";}')
        self.setStyleSheet(self.css % power_color)

        self.sync_pos_chk.stateChanged.connect(self.update_data)
        self.merge_chk.stateChanged.connect(self.update_data)
        self.sync_db_chk.stateChanged.connect(self.update_data)

    @Slot(QPoint)
    def on_group_frm_customContextMenuRequested(self, point):
        """ When the context menu of the SyncGroup is requested

        :type point: QPoint
        :param point: The point of the click
        """
        menu = QMenu(self)
        menu.setToolTipsVisible(True)
        if QT6:  # QT6 requires exec() instead of exec_()
            menu.exec_ = getattr(menu, "exec")

        action = QAction(_("Rename group"), menu)
        action.setIcon(self.base.ico_file_edit)
        action.setToolTip(_("Change the name of the Sync group"))
        action.triggered.connect(self.on_rename)
        menu.addAction(action)

        action = QAction(_("Sync group"), menu)
        action.setIcon(self.base.ico_files_merge)
        action.setToolTip(_("Sync the Sync group items"))
        action.triggered.connect(self.on_sync_btn_clicked)
        menu.addAction(action)

        action = QAction(_("Load group items"), menu)
        action.setIcon(self.base.ico_folder_open)
        action.setToolTip(_("Load the Sync group items to the Books View"))
        action.triggered.connect(self.load_group_items)
        menu.addAction(action)

        action = QAction(_("Copy Archived to group"), menu)
        action.setIcon(self.base.ico_files_merge)
        action.setToolTip(_("Copy the archived version to all Sync group items"))
        action.triggered.connect(self.archived_to_group)
        menu.addAction(action)

        menu.addSeparator()

        action = QAction(_("Delete selected"), menu)
        action.setIcon(self.base.ico_delete)
        action.setToolTip(_("Delete the selected Sync group items"))
        action.triggered.connect(self.base.toolbar.on_delete_btn_clicked)
        menu.addAction(action)

        menu.exec_(self.mapToGlobal(point))

    def on_rename(self):
        """ Renames the SyncGroup
        """
        title = self.title_lbl.text()
        title = title if title else True
        popup = self.base.popup(_("Rename SyncGroup"),
                                _("Enter the new name of the SyncGroup:"),
                                icon=QMessageBox.Question, buttons=2,
                                input_text=title, button_text=(_("OK"), _("Cancel")))
        if popup.buttonRole(popup.clickedButton()) == QMessageBox.AcceptRole:
            text = popup.typed_text
            self.title_lbl.setText(text)
            self.data["title"] = text
            self.update_data()

    def setup_buttons(self):
        for btn, char in self.buttons:
            self.def_btn_icos.append(btn.icon())
            size = btn.iconSize().toTuple()
            btn.xig = XIconGlyph(self, {"family": "XFont", "size": size, "char": char})
        for item in self.sync_items:
            item.setup_buttons()

    def setup_icons(self):
        if self.base.theme in [THEME_NONE_NEW, THEME_DARK_NEW, THEME_LIGHT_NEW]:
            QTimer.singleShot(0, self.set_new_icons)
        else:
            self.set_old_icons()
        for item in self.sync_items:
            item.setup_icons()

    # noinspection DuplicatedCode
    def set_new_icons(self):
        """ Get the font icons with the new color palette
        """
        color = self.palette().text().color().name()
        for btn, _ in self.buttons:
            size = btn.iconSize().toTuple()
            btn.xig.color = color
            btn.setIcon(btn.xig.get_icon({"size": size}))

    def set_old_icons(self):
        """ Reload the old icons
        """
        for idx, item in enumerate(self.buttons):
            btn = item[0]
            btn.setIcon(self.def_btn_icos[idx])

    @Slot(bool)
    def on_power_btn_clicked(self, state):
        """ Enables the Group
        """
        if state:
            power_color = self.base.palette().button().color().name()
        else:
            power_color = self.base.palette().dark().color().name()
        self.setStyleSheet(self.css % power_color)

        self.data["enable"] = state
        self.update_data()

    @Slot()
    def on_refresh_btn_clicked(self, ):
        """ The `Refresh` button is pressed
        """
        items_paths = [i["path"] for i in self.data.get("items", [])]
        for item in self.sync_items:
            self.items_layout.removeWidget(item)
        self.sync_items = []
        for path in items_paths:
            self.add_item({"path": path})
        self.check_data()

    @Slot()
    def on_sync_btn_clicked(self, ):
        """ The `Sync this group` button is pressed
        """
        if self.base.merge_warning_stop():
            return
        self.base.synchronize_group(self)

    @Slot(bool)
    def on_fold_btn_toggled(self, pressed):
        """ Shows/hides the Sync paths

        :type pressed: bool
        :param pressed: The arrow button's status
        """
        if pressed:  # Closed
            self.fold_btn.setText(_("Show sync paths"))
            self.fold_btn.setArrowType(Qt.RightArrow)
        else:  # Opened
            self.fold_btn.setText(_("Hide sync paths"))
            self.fold_btn.setArrowType(Qt.DownArrow)
        self.items_frm.setHidden(pressed)
        self.update_data()
        QTimer.singleShot(200, self.reset_group_height)

    def add_item(self, data):
        """ Adds a new sync item

        :type data: dict
        :param data: The sync item data
        """
        item = SyncItem(self.base)
        item.group = self
        self.sync_items.append(item)
        item.idx = len(self.sync_items) - 1
        path = data["path"]
        if path:
            item.sync_path_txt.setText(path)
            try:
                data = decode_data(path)
            except FileNotFoundError:  # path doesn't exist
                self.data["items"][item.idx]["data"] = {}
                self.set_erroneous(item, _("Could not access the book's metadata file"))
            except PermissionError:
                self.set_erroneous(item, _("Could not access the book's metadata file"))
                self.base.error(_(f"Could not access the book's metadata file\n{path}\n\n"
                                  f"Merging this group will produce unpredictable "
                                  f"results."))
                self.data["items"][item.idx]["data"] = {}
            else:
                self.data["items"][item.idx]["data"] = data
                if not item.idx:
                    self.new_format = data.get("annotations") is not None
        self.items_layout.addWidget(item)

    def remove_item(self, item):
        """ Removes a sync item

        :type item: SyncItem
        """
        del self.data["items"][item.idx]
        self.items_layout.removeWidget(item)
        self.sync_items.remove(item)
        item.deleteLater()
        for idx, item in enumerate(self.sync_items):
            item.idx = idx

    def reset_group_height(self):
        """ Reset the height of the group row
        """
        height = self.sizeHint().height()
        self.base.sync_table.setRowHeight(self.idx, height)

    def check_data(self):
        """ Checks if the data is valid for syncing
        """
        source = {"path:": "", "data": {}}
        for idx, sync_item in enumerate(self.sync_items):
            self.set_txt_normal(sync_item)
            path = self.data["items"][idx]["path"]
            if path and not isfile(path):  # file doesn't exist
                text = _("The path to the book's metadata file does not exist")
                self.set_erroneous(sync_item, text)
                if idx:
                    continue  # check the next path
                else:
                    return  # missing source file
            elif not path:
                continue  # empty item

            data = self.data["items"][idx]["data"]
            if not idx:  # source is the first item
                source["path"] = path
                source["data"] = data
                if not data.get("cre_dom_version"):
                    text = _("The metadata file is of an older, not supported version.\n"
                             "No syncing is possible for this Sync group.")
                    self.set_erroneous(sync_item, text)
                    return
                continue  # check source with the rest

            # check if the data format is the same
            data1_new = source["data"].get("annotations") is not None
            try:
                data2_new = data.get("annotations") is not None
            except AttributeError:
                self.set_erroneous(sync_item,
                                   _("Could not access the book's metadata file"))
                self.base.error(_(f"Could not access the book's metadata file\n{path}"))
                continue
            if (data1_new and not data2_new) or (data2_new and not data1_new):
                text = _("The book's metadata files are in different format")
                self.set_erroneous(sync_item, text)
                continue

            # check if the books have the same cre version
            if not self.base.same_cre_version(source["data"], data):
                text = _("The metadata files were produced with a different version "
                         "of the reader engine")
                self.set_erroneous(sync_item, text)
                continue

            # check if the book's md5 is the same KEEP IT AS THE LAST CHECK
            if not self.base.same_book(source["data"], data, source["path"], path):
                text = _("The book file is different from the rest")
                self.set_erroneous(sync_item, text)
                sync_item.md5_diff = True
                continue

    def set_txt_normal(self, item):
        """ Sets the normal state of the item's text

        :type item: SyncItem
        """
        item.ok = True
        tooltip = _("The path to the  book's metadata file")
        item.sync_path_txt.setToolTip(tooltip)
        item.sync_path_txt.setStatusTip(tooltip)
        item.sync_path_txt.setStyleSheet(self.styleSheet())

    def set_erroneous(self, item, tooltip=""):
        """ Sets the erroneous state of the item

        :type item: SyncItem
        """
        item.ok = False
        item.sync_path_txt.setToolTip(tooltip)
        item.sync_path_txt.setStatusTip(tooltip)

        if self.base.theme in (THEME_DARK_NEW, THEME_DARK_OLD):
            color = "#DD0000"
        else:
            color = "#990000"
        style = self.styleSheet() + 'QLineEdit {color: "%s";}' % color
        item.sync_path_txt.setStyleSheet(style)

    def update_data(self):
        """ Saves and updates the sync group data when something is changed
        """
        if self.idx is None:  # on first load on startup
            return
        data = {"title": self.title_lbl.text(),
                "sync_pos": self.sync_pos_chk.isChecked(),
                "merge": self.merge_chk.isChecked(),
                "sync_db": self.sync_db_chk.isChecked(),
                "items": self.data["items"],
                "enabled": self.power_btn.isChecked(),
                "folded": self.fold_btn.isChecked(),
                }
        self.base.sync_groups[self.idx] = data
        self.data = data
        self.base.save_sync_groups()

    def load_group_items(self):
        """ Loads the group's items in the Books view
        """
        self.base.toolbar.reload_from_sync = True
        self.base.toolbar.books_view_btn.setChecked(True)
        self.base.toolbar.change_view()
        self.base.toolbar.loaded_btn.click()
        self.base.on_file_table_fileDropped([item["path"] for item in self.data["items"]])

    def archived_to_group(self):
        """ Copies the archived data to all the items of the group
        """
        path = self.data["items"][0]["path"]
        data = decode_data(path)
        idx = self.base.check4archive_merge({"path": path, "data": data})
        no_archive_txt = _("Could not find an archived version of the book's metadata")
        if idx is False:
            self.base.popup(_("Error"), no_archive_txt, icon=QMessageBox.Critical)
            return
        old_format_txt = _("The metadata file is of an older, not supported version.")
        if not self.new_format:
            self.base.popup(_("Error"), old_format_txt, icon=QMessageBox.Critical)
            return
        warn_txt = _("All the Group versions will be overwritten with the archived "
                     "version!\n\nAre you sure you want to continue?")
        popup = self.base.popup(_("Warning"), warn_txt, icon=QMessageBox.Warning,
                                buttons=2, button_text=(_("Yes"), _("Cancel")))
        if popup.buttonRole(popup.clickedButton()) == QMessageBox.RejectRole:
            return

        arch_data = self.base.books[idx]["data"]  # archived data
        arch_total = arch_data.get("doc_pages",
                                   arch_data.get("stats", {}).get("pages", 0))
        for item in self.data["items"]:
            item_data = item["data"]
            item_total = item_data.get("doc_pages",
                                       item_data.get("stats", {}).get("pages", 0))
            item_data["annotations"] = deepcopy(arch_data["annotations"])
            if arch_total != item_total:
                self.recalculate_pages(item_data, item_total, arch_total)
            item_data["annotations_externally_modified"] = True
            self.base.save_book_data(item["path"], item_data)

        self.base.reload_from_sync = True
        if not self.base.db_mode:
            self.base.db_mode = True  # need this to trigger the reload of the files
            self.base.books2reload = self.base.loaded_paths.copy()
            self.base.toolbar.update_loaded()

        self.base.popup(_("Info"), _("The metadata was successfully updated!"),
                        icon=QMessageBox.Information)

    @staticmethod
    def recalculate_pages(item_data, item_total, arch_total):
        """ Recalculates the page number of the annotations
        based on the total pages number

        :type item_data: dict
        :param item_data: The item's data
        :type item_total: int
        :param item_total: The total number of pages of the item
        :type arch_total: int
        :param arch_total: The total number of pages of the archived item
        """
        for annot in item_data["annotations"].values():
            percent = int(annot["pageno"]) / arch_total
            annot["pageno"] = int(round(percent * item_total))


class SyncItem(QWidget, Ui_SyncItem):

    def __init__(self, parent=None):
        """ Initializes the StatusBar

        :type parent: Base
        """
        super(SyncItem, self).__init__(parent)
        self.setupUi(self)
        self.base = parent
        self.group = SyncGroup(self.base)
        self.def_btn_icos = []
        self.buttons = [(self.add_btn, "+"),
                        (self.del_btn, "-")]
        self.setup_buttons()
        self.setup_icons()
        self.ok = True
        self.md5_diff = False
        self.md5_ignore_exists = False

        QTimer.singleShot(0, self.check_ignore_md5)

    def setup_buttons(self):
        for btn, char in self.buttons:
            self.def_btn_icos.append(btn.icon())
            size = btn.iconSize().toTuple()
            btn.xig = XIconGlyph(self, {"family": "XFont", "size": size, "char": char})

    def setup_icons(self):
        if self.base.theme in [THEME_NONE_NEW, THEME_DARK_NEW, THEME_LIGHT_NEW]:
            QTimer.singleShot(0, self.set_new_icons)
        else:
            self.set_old_icons()

    # noinspection DuplicatedCode
    def set_new_icons(self):
        """ Get the font icons with the new color palette
        """
        color = self.palette().text().color().name()
        for btn, _ in self.buttons:
            size = btn.iconSize().toTuple()
            btn.xig.color = color
            btn.setIcon(btn.xig.get_icon({"size": size}))

    def set_old_icons(self):
        """ Reload the old icons
        """
        for idx, item in enumerate(self.buttons):
            btn = item[0]
            btn.setIcon(self.def_btn_icos[idx])

    @Slot(QPoint)
    def on_sync_path_txt_customContextMenuRequested(self, point):
        """ When the context menu of the SyncGroup is requested

        :type point: QPoint
        :param point: The point of the click
        """
        if self.md5_diff or self.md5_ignore_exists:
            menu = QMenu(self)
            menu.setToolTipsVisible(True)
            if QT6:  # QT6 requires exec() instead of exec_()
                menu.exec_ = getattr(menu, "exec")

            action = QAction(_("Ignore MD5"), menu)
            action.setCheckable(True)
            is_active = isfile(join(dirname(self.sync_path_txt.text()), "ignore_md5"))
            action.setChecked(is_active)
            action.setToolTip(_("Ignore MD5 checksum comparisons for this file"))
            action.triggered.connect(self.create_ignore_md5)
            menu.addAction(action)

            menu.exec_(self.mapToGlobal(point))

    def create_ignore_md5(self):
        """ Creates the `ignore_md5` file
        """
        ignore_md5_path = join(dirname(self.sync_path_txt.text()), "ignore_md5")
        if not isfile(ignore_md5_path):
            open(ignore_md5_path, "w").close()
        else:
            os.remove(ignore_md5_path)
        self.group.on_refresh_btn_clicked()

    def check_ignore_md5(self):
        """ Checks if there is an md5_ignore file present
        """
        ignore_md5_path = join(dirname(self.sync_path_txt.text()), "ignore_md5")
        self.md5_ignore_exists = isfile(ignore_md5_path)

    @Slot()
    def on_sync_path_btn_clicked(self, ):
        """ The `Select` path button is pressed
        """
        last_dir = self.base.last_dir
        text = self.sync_path_txt.text().strip()
        if text:
            last_dir = dirname(text)
        path = QFileDialog.getOpenFileName(self.base, _("Select the metadata file"),
                                           last_dir, "metadata files (*.lua)")[0]
        if path:
            path = normpath(path)
            self.base.last_dir = dirname(path)
            for item in self.group.data["items"]:  # check existence
                if item["path"] == path:
                    self.base.popup(_("!"),
                                    _("This metadata file already exists in the group!"),)
                    return
            idx = self.group.sync_items.index(self)
            self.group.data["items"][idx]["path"] = path
            data = decode_data(path)
            self.group.data["items"][idx]["data"] = data
            if idx == 0:  # first item
                self.group.new_format = data.get("annotations") is not None
                if not self.group.title_lbl.text().strip():
                    title = data.get("doc_props", data.get("stats", {})).get("title", "")
                    self.group.title_lbl.setText(title)
            self.sync_path_txt.setText(path)
            self.group.update_data()
            self.group.check_data()

    @Slot()
    def on_add_btn_clicked(self, ):
        """ Add a new item to the group
        """
        first_item = self.group.sync_items.index(self) == 0
        if first_item and not self.sync_path_txt.text().strip():  # no first sync path
            self.base.error(_("The first metadata file path must not be empty!"))
            return
        item_data = {"path": "", "data": {}}
        self.group.add_item(item_data)
        self.group.data["items"].append(item_data)
        self.group.update_data()
        QTimer.singleShot(200, self.group.reset_group_height)

    @Slot()
    def on_del_btn_clicked(self, ):
        """ Delete this item from the group
        """
        if not self.idx:  # the first item can't be deleted
            self.base.error(_("Can't delete the first metadata file path!"))
            return
        self.group.remove_item(self)
        self.group.update_data()
        QTimer.singleShot(100, self.group.reset_group_height)

# if __name__ == "__main__":
#     with open("secondary.py", str("r")) as py_text:
#         import re
#         script = py_text.read()
#         result = tuple(re.findall(r"class (.+)\(", script))
#         print("__all__ = {}".format(result))
