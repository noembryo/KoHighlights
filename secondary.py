# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
from boot_config import *

import re
import webbrowser
from functools import partial
from distutils.version import LooseVersion
from os.path import join, basename, splitext, isfile

# ___ _____________ DEPENDENCIES ____________________________________
import mechanize
from bs4 import BeautifulSoup
from PySide.QtCore import Qt, Slot, QObject, Signal, QSize, QPoint, QThread
from PySide.QtGui import (QApplication, QMessageBox, QIcon, QFileDialog, QTableWidgetItem,
                          QDialog, QWidget, QMovie, QFont, QMenu, QAction, QTableWidget,
                          QCheckBox, QToolButton, QActionGroup)

from gui_about import Ui_About  # ___ ______ GUI STUFF ______________
from gui_auto_info import Ui_AutoInfo
from gui_toolbar import Ui_ToolBar
from gui_status import Ui_Status
from gui_edit import Ui_TextDialog


# ___ _____________ PYTHON 2/3 COMPATIBILITY ________________________
if not PYTHON2:
    # noinspection PyShadowingBuiltins
    unicode = str
from future.moves.urllib.request import Request
from pprint import pprint


def _(text):  # for future gettext support
    return text


__all__ = ("About", "AutoInfo", "ToolBar", "TextDialog", "Status", "XTableWidgetItem",
           "LogStream", "Scanner", "HighlightScanner", "DropTableWidget", "XMessageBox",
           "ReLoader", "DBLoader")


# ___ _______________________ SUBCLASSING ___________________________


class XTableWidgetItem(QTableWidgetItem):
    def __lt__(self, value):
        return self.data(Qt.UserRole) < value.data(Qt.UserRole)


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
                    text4check = data["highlight"][page][page_id]["text"]
                    text = text4check.replace("\\\n", "\n")
                    comment = ""
                    for idx in data["bookmarks"]:  # check for comment text
                        if text4check == data["bookmarks"][idx]["notes"]:
                            bkm_text = data["bookmarks"][idx].get("text", "")
                            if not bkm_text:
                                break
                            bkm_text = re.sub(r"Page \d+ "
                                              r"(.+?) @ \d+-\d+-\d+ \d+:\d+:\d+", r"\1",
                                              bkm_text, 1, re.DOTALL | re.MULTILINE)
                            if text4check != bkm_text:  # there is a comment
                                comment = bkm_text.replace("\\\n", "\n")
                            break
                    highlight["text"] = text
                    highlight["comment"] = comment
                    highlight["page"] = str(page)
                except KeyError:  # blank highlight
                    continue
                self.found.emit(highlight)


# ___ _______________________ GUI STUFF _____________________________


class ToolBar(QWidget, Ui_ToolBar):

    def __init__(self, parent=None):
        super(ToolBar, self).__init__(parent)
        self.setupUi(self)
        self.base = parent

        self.buttons = (self.check_btn, self.scan_btn, self.export_btn, self.open_btn,
                        self.merge_btn, self.delete_btn, self.clear_btn, self.books_btn,
                        self.highlights_btn, self.db_btn, self.about_btn)
        # for button in buttons:
        #     button.installEventFilter(TextSizer(button))
        self.size_menu = self.create_size_menu()

        self.books_btn.clicked.connect(partial(self.change_view, 0))
        self.highlights_btn.clicked.connect(partial(self.change_view, 1))
        self.db_btn.clicked.connect(partial(self.change_view, 2))

        self.check_btn.clicked.connect(parent.on_check_btn)
        self.check_btn.hide()
        # self.view_selector.hide()
        # self.view_selector_2.hide()

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

        for btn in self.buttons:
            btn.setMinimumWidth(size + 10)
            btn.setIconSize(button_size)
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
            if self.base.current_view == 1:  # highlights view
                if self.base.db_view:
                    self.base.db_view = False  # we loading books, use to Books mode
                    self.on_clear_btn_clicked()
            text = _("Scanning for KoReader metadata files")
            self.base.loading_thread(Scanner, path, text, clear=False)

    @Slot()
    def on_export_btn_clicked(self):
        """ The `Export` button is pressed
        """
        if self.base.current_view in [0, 2]:  # books/archive view
            self.base.save_actions(MANY_TEXT)
        elif self.base.current_view == 1:  # highlights view
            self.base.save_actions(MERGED_HIGH)

    @Slot()
    def on_open_btn_clicked(self):
        """ The `Open Book` button is pressed
        """
        if self.base.current_view in [0, 2]:  # books/archive view
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
            data = self.base.high_table.item(idx.row(), HIGHLIGHT_H).data(Qt.UserRole)
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
        if self.base.current_view == 1:  # highlights view
            (self.base.high_table.model()
             .removeRows(0, self.base.high_table.rowCount()))
        self.base.loaded_paths.clear()
        self.base.reload_highlights = True
        self.base.file_table.model().removeRows(0, self.base.file_table.rowCount())
        self.activate_buttons()

    def change_view(self, idx):
        """ Changes what is shown in the app

        :type idx: int
        :param idx: The view index
        """
        self.base.current_view = idx
        if idx == 0:  # Books view
            for btn in [self.base.toolbar.export_btn, self.base.toolbar.delete_btn]:
                self.add_btn_menu(btn)
            if self.base.sel_idx:
                item = self.base.file_table.item(self.base.sel_idx.row(),
                                                 self.base.sel_idx.column())
                self.base.on_file_table_itemClicked(item, reset=False)
            if self.base.db_view:
                self.base.db_view = False
                self.base.reload_highlights = True
                text = "Scanning for KoReader metadata files"
                self.base.loading_thread(ReLoader, self.base.books2reload, text)
        elif idx == 1:  # Highlights view
            for btn in [self.base.toolbar.export_btn, self.base.toolbar.delete_btn]:
                self.remove_btn_menu(btn)
            if self.base.reload_highlights:
                self.base.scan_highlights_thread()
        elif idx == 2:  # Database view
            self.add_btn_menu(self.base.toolbar.export_btn)
            self.remove_btn_menu(self.base.toolbar.delete_btn)
            if not self.base.db_view:
                self.base.books2reload = self.base.loaded_paths.copy()
                self.base.db_view = True
                self.base.reload_highlights = True
                self.base.read_books_from_db()
                text = "Loading KoHighlights database"
                self.base.loading_thread(DBLoader, self.base.books, text)
                if not len(self.base.books):  # no books in the db
                    text = _('There are no books currently in the archive.\nTo add/update'
                             ' one or more books, select them in the "Books" view and '
                             'in their right-click menu, press "Archive".')
                    self.base.popup(_("Info"), text, icon=QMessageBox.Question)
        self.base.views.setCurrentIndex(1 if idx == 1 else 0)
        self.setup_buttons(idx)
        self.activate_buttons()

    def setup_buttons(self, idx):
        """ Shows/Hides toolbar's buttons based on the view selected

        :type idx: int
        :param idx: The view index
        """
        self.scan_btn.setVisible(idx in [0, 1])
        # self.export_btn.setVisible(idx in [0, 1, 2])
        # self.open_btn.setVisible(idx in [0, 1, 3])
        self.merge_btn.setVisible(not idx)
        self.delete_btn.setVisible(idx in [0, 2])
        self.clear_btn.setVisible(not self.base.db_view)

        self.base.status.setVisible(not idx)

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
        self.merge_btn.setEnabled(self.base.check4merge())
        self.delete_btn.setEnabled(bool(idx))
        self.clear_btn.setEnabled(bool(count))

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
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:14.0) "
                                "Gecko/20100101 Firefox/24.0.1",
                  "Referer": "http://whateveritis.com"}
        url = "http://www.noembryo.com/apps.php?kohighlights"

        browser = mechanize.Browser()
        browser.set_handle_robots(False)
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


# if __name__ == "__main__":
#     with open("secondary.py", str("r")) as py_text:
#         import re
#         script = py_text.read()
#         result = tuple(re.findall(r"class (.+)\(", script))
#         print("__all__ = {}".format(result))
