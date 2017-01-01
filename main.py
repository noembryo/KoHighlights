# coding=utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os, sys, re
import codecs
import gzip
import json
import traceback
import cPickle
import time
import mechanize
import urllib2
import webbrowser
from os.path import (isdir, join, basename, splitext, dirname)
from pprint import pprint

from bs4 import BeautifulSoup  # __ ###########   DEPENDENCIES   ############
from slpp import slpp as lua
from PySide.QtCore import (Qt, QTimer, Slot, QObject, Signal, QThread)
from PySide.QtGui import (QMainWindow, QApplication, QMessageBox, QIcon,
                          QFileDialog, QTableWidgetItem, QTextCursor, QDialog,
                          QWidget, QLabel, QMovie, QFont, QMenu, QAction,
                          QTableWidget, QCheckBox, QHeaderView)

from gui_main import Ui_Base  # __ ###########   GUI STUFF   ############
from gui_about import Ui_About
from gui_auto_info import Ui_AutoInfo
from gui_toolbar import Ui_ToolBar


__author__ = 'noEmbryo'
__version__ = '0.2.0.1'


def _(text):
    return text

try:
    with gzip.GzipFile('settings.json.gz', 'rb') as settings:
        app_config = json.loads(settings.read())
except IOError:  # first run
    app_config = {}

FIRST_RUN = not bool(app_config)


# noinspection PyCallByClass
class Base(QMainWindow, Ui_Base):
    def __init__(self, parent=None):
        super(Base, self).__init__(parent)
        self.scan_thread = QThread()
        self.setupUi(self)
        self.version = __version__

        self.skip_version = 0
        self.last_dir = os.getcwd()
        self.exit_msg = False

        self.file_table.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.header_main = self.file_table.horizontalHeader()
        self.header_main.setMovable(True)
        self.header_main.setDefaultAlignment(Qt.AlignLeft)

        self.about = About(self)
        self.auto_info = AutoInfo(self)

        self.toolbar = ToolBar(self)
        self.tool_bar.addWidget(self.toolbar)

        self.anim_lbl = QLabel(self)
        self.statusbar.addPermanentWidget(self.anim_lbl)
        self.wait_anim = QMovie(':/stuff/wait.gif')
        self.anim_lbl.setMovie(self.wait_anim)
        self.anim_lbl.hide()

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        # noinspection PyTypeChecker
        QTimer.singleShot(0, self.on_load)

        # noinspection PyTypeChecker
        QTimer.singleShot(200000, self.auto_check4update)  # check for updates

        # self.threads4process = []
        # thread_cleanup_timer = QTimer(self)  # cleanup threads for ever
        # thread_cleanup_timer.timeout.connect(self.thread_cleanup)
        # thread_cleanup_timer.start(2000)

    def on_load(self):
        """ Things that must be done after the initialization
        """
        self.settings_load()
        if FIRST_RUN:  # on first run
            pass
        self.toolbar.save_btn.setMenu(self.save_menu())  # assign/create menu
        self.connect_gui()
        self.show()

    ########################################################
    # __                   EVENTS STUFF                    #
    ########################################################

    # noinspection PyUnresolvedReferences
    def connect_gui(self):
        """ Make all the signal/slots connections
        """
        self.file_table.fileDropped.connect(self.items_dropped)
        self.file_table.itemClicked.connect(self.on_item_clicked)
        self.file_table.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.toolbar.save_btn.clicked.connect(lambda: self.save_actions(0))

        sys.stdout = LogStream()
        sys.stdout.setObjectName('out')
        sys.stdout.append_to_log.connect(self.write_to_log)
        sys.stderr = LogStream()
        sys.stderr.setObjectName('err')
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
                print('control + D')
                return True
            if key == Qt.Key_Delete:  # ctrl+Del
                self.toolbar.on_clear_btn_clicked()
                return True
            if key == Qt.Key_O:  # ctrl+O
                self.toolbar.on_select_btn_clicked()
                return True
            if key == Qt.Key_S:  # ctrl+S
                self.save_actions(0)
                return True
            if key == Qt.Key_I:  # ctrl+I
                self.toolbar.on_info_btn_clicked()
                return True
            if key == Qt.Key_Q:  # ctrl+Q
                self.close()
        if key == Qt.Key_Escape:
            self.close()

        if key == Qt.Key_Delete:  # Delete
            for idx in sorted(self.file_table.selectionModel().selectedRows(),
                              reverse=True):
                self.file_table.removeRow(idx.row())
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
        popup = self.popup(_('Confirmation'), _("Exit KoHighlights?"),
                           buttons=2)
        # if popup.clickedButton().text() == _('OK'):
        if popup.buttonRole(popup.clickedButton()) == QMessageBox.AcceptRole:
            self.bye_bye_stuff()
            event.accept()  # let the window close
        else:
            event.ignore()

    def bye_bye_stuff(self):
        """ Things to do before exit
        """
        self.settings_save()

    ########################################################
    # __                  SETTINGS STUFF                   #
    ########################################################

    def settings_load(self):
        """ Loads the jason based configuration settings
        """
        if app_config:
            self.restoreGeometry(self.unpickle('geometry'))
            self.restoreState(self.unpickle('state'))
            self.splitter.restoreState(self.unpickle('splitter'))
            self.about.restoreGeometry(self.unpickle('about_geometry'))
            # window = app_config.get('window', None)
            # if window:
            #     self.move(*window[0])
            #     self.resize(*window[1])
            self.last_dir = app_config.get('last_dir', os.getcwd())
            self.skip_version = app_config.get('skip_version', None)

    def settings_save(self):
        """ Saves the jason based configuration settings
        """
        # window = self.pos().toTuple(), self.size().toTuple()

        config = {'geometry': cPickle.dumps(self.saveGeometry()),
                  'state': cPickle.dumps(self.saveState()),
                  'splitter': cPickle.dumps(self.splitter.saveState()),
                  'about_geometry': cPickle.dumps(self.about.saveGeometry()),
                  # 'window': window,
                  'last_dir': self.last_dir,
                  'skip_version': self.skip_version,
                  }
        try:
            with gzip.GzipFile('settings.json.gz', 'w+') as gz_file:
                gz_file.write(json.dumps(config, sort_keys=True, indent=4))
        except IOError as error:
            print('On saving settings:', error)

    @staticmethod
    def unpickle(key):
        """ Un-serialize some binary settings
        :type key: str|unicode
        :param key: The dict key to be un-pickled
        """
        try:
            value = cPickle.loads(str(app_config.get(key)))
        except cPickle.UnpicklingError:
            return
        return value

    ########################################################
    # __                    MAIN STUFF                     #
    ########################################################

    def items_dropped(self, dropped):
        """ When some items are dropped to the TableWidget
        :type dropped: list
        :param dropped: The items dropped
        """
        files = [i for i in dropped if splitext(i)[1] == '.lua']
        self.create_items(files)
        folders = [j for j in dropped if isdir(j)]
        for folder in folders:
            self.scan_files_thread(folder)

    def on_item_clicked(self, item):
        """ When an item of the FileTable is clicked
        :type item: QTableWidgetItem
        :param item: The item (cell) that is clicked
        """
        row = item.row()
        data = self.file_table.item(row, 0).data(Qt.UserRole)

        self.text_box.clear()
        for i in data['highlight']:
            try:
                self.text_box.appendPlainText(data['highlight'][i][1]['text'] + '\n')
            except KeyError:  # blank highlight
                continue

    def on_item_double_clicked(self, item):
        """ When an item of the FileTable is double-clicked
        :type item: QTableWidgetItem
        :param item: The item (cell) that is double-clicked
        """
        row = item.row()
        data = self.file_table.item(row, 0).data(Qt.UserRole)
        items = ['title', 'authors', 'series', 'language',
                 'pages', 'total_time_in_sec']
        text = ''
        for item in items:
            try:
                value = data['stats'][item]
                if item == 'title' and not value:
                    break
                if item == 'total_time_in_sec':
                    value = self.get_time_str(data['stats'][item])
                    item = 'total time'
                text += '{}: {}\n'.format(item.capitalize(), value)
            except KeyError:  # old type history file
                break
        else:
            self.popup('Book Info', text.rstrip(), icon=QMessageBox.Information)
            return

        path = self.file_table.item(row, 2).data(0)
        stats = self.get_item_stats(path, data)
        text += 'Title: {}\n'.format(stats[1])
        text += 'Authors: {}'.format(stats[2])
        self.popup('Book Info', text, icon=QMessageBox.Information)

    def scan_files_thread(self, path):
        """ Gets all the history files that are inside
        this path and its sub-directories
        :type path: str|unicode
        :param path: The root path
        """
        scanner = Scanner(path)
        scanner.moveToThread(self.scan_thread)
        scanner.found.connect(self.create_items)
        scanner.finished.connect(self.scan_finished)
        scanner.finished.connect(self.scan_thread.quit)
        self.scan_thread.downer = scanner
        self.scan_thread.started.connect(scanner.process)
        self.scan_thread.start(QThread.IdlePriority)

        self.status_animation('start')

        self.auto_info.set_text(_("Scanning for KoReader history files.\n"
                                  "Please Wait..."))
        self.auto_info.show()

    def scan_finished(self):
        self.status_animation('stop')
        self.auto_info.hide()

    def create_items(self, files):
        """ Creates table items out of the files given
        :type files: list
        :param files: The files given
        """
        for idx, filename in enumerate(files):
            if os.path.exists(filename) and splitext(filename)[1].lower() == '.lua':
                self.file_table.insertRow(idx)
                data = self.convert_data(filename)
                if not data:
                    print('No data here!', filename)
                    continue
                icon, title, authors = self.get_item_stats(filename, data)

                title_item = QTableWidgetItem(icon, title)
                title_item.setToolTip(title)
                title_item.setData(Qt.UserRole, data)
                self.file_table.setItem(idx, 0, title_item)

                author_item = QTableWidgetItem(authors)
                author_item.setToolTip(authors)
                self.file_table.setItem(idx, 1, author_item)

                path_item = QTableWidgetItem(filename)
                path_item.setToolTip(filename)
                self.file_table.setItem(idx, 2, path_item)
        self.file_table.resizeColumnsToContents()

    @staticmethod
    def convert_data(path):
        """ Converts the lua table to Python dict
        :type path: str|unicode
        :param path: The path to the lua file
        """
        with codecs.open(path, 'r', encoding='utf8') as txt_file:
            txt = txt_file.read()
            data = lua.decode(txt[39:])  # offset the first words of the file
            if type(data) == dict:
                return data

    @staticmethod
    def get_item_stats(filename, data):
        """ Returns the title and authors of a history file
        :type filename: str|unicode
        :param filename: The filename to get the stats for
        :type data: dict
        :param data: The dict converted lua file
        """
        if data['highlight']:
            icon = QIcon(':/stuff/check.png')
        else:
            icon = QIcon(':/stuff/trans32.png')

        try:
            title = data['stats']['title']
            authors = data['stats']['authors']
        except KeyError:  # older type file
            title = splitext(basename(filename))[0]
            try:
                name = title.split('#] ')[1]
                title = splitext(name)[0]
            except IndexError:  # no '#] ' in filename
                pass
            authors = 'OLD TYPE FILE'
        if not title:
            try:
                name = filename.split('#] ')[1]
                title = splitext(name)[0]
            except IndexError:  # no '#] ' in filename
                title = 'NO TITLE FOUND'
        # title = title if title else 'NO TITLE'
        authors = authors if authors else 'NO AUTHOR FOUND'
        return icon, title, authors

    ########################################################
    # __                  SAVING STUFF                     #
    ########################################################

    def save_menu(self):
        """ Creates the `Save Files` button menu
        """
        menu = QMenu(self)
        icon = QIcon(':/stuff/file_save.png')
        for idx, item in enumerate([_("... to individual text files"),
                                    _("... combined to one text file")]):
            action = QAction(item, menu)
            action.triggered.connect(self.on_save_actions)
            action.setData(idx)
            action.setIcon(icon)
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
        title_counter = 0
        saved = 0
        if not self.file_table.selectionModel().selectedRows():
            return
        if idx == 0:  # save to different text files
            path = QFileDialog.getExistingDirectory(self,
                                                    _("Select destination folder for the "
                                                      "saved file(s)"), self.last_dir,
                                                    QFileDialog.ShowDirsOnly)
            if path:
                self.last_dir = path
                self.status_animation('start')
            else:
                return
            for i in self.file_table.selectionModel().selectedRows():
                row = i.row()
                data = self.file_table.item(row, 0).data(Qt.UserRole)
                highlights = []
                for j in data['highlight']:
                    try:
                        highlights.append(data['highlight'][j][1]['text'])
                    except KeyError:  # blank highlight
                        continue
                if not highlights:  # no highlights
                    continue
                title = self.file_table.item(row, 0).data(0)
                if title == 'NO TITLE FOUND':
                    title += str(title_counter)
                    title_counter += 1
                authors = self.file_table.item(row, 1).data(0)
                if authors in ['OLD TYPE FILE', 'NO AUTHOR FOUND']:
                    authors = ''
                name = title
                if authors:
                    name = '{} - {}'.format(authors, title)
                filename = join(path, self.sanitize_filename(name) + '.txt')
                with codecs.open(filename, 'w+', encoding='utf-8') as text_file:
                    for highlight in highlights:
                        text_file.write(highlight + '\n\n')
                    saved += 1
        if idx == 1:  # save combined text to one file
            filename = QFileDialog.getSaveFileName(self, "Save to Text file",
                                                   self.last_dir,
                                                   "text files (*.txt);;all files (*.*)")
            if filename[0]:
                filename = filename[0]
                self.last_dir = dirname(filename[0])
            else:
                return
            blocks = []
            for i in self.file_table.selectionModel().selectedRows():
                row = i.row()
                data = self.file_table.item(row, 0).data(Qt.UserRole)
                highlights = []
                for j in data['highlight']:
                    try:
                        highlights.append(data['highlight'][j][1]['text'])
                    except KeyError:  # blank highlight
                        continue
                if not highlights:  # no highlights
                    continue
                title = self.file_table.item(row, 0).data(0)
                if title == 'NO TITLE FOUND':
                    title += str(title_counter)
                    title_counter += 1
                authors = self.file_table.item(row, 1).data(0)
                if authors in ['OLD TYPE FILE', 'NO AUTHOR FOUND']:
                    authors = ''
                name = title
                if authors:
                    name = '{} - {}'.format(authors, title)
                blocks.append((name, '\n\n'.join(highlights)))
                saved += 1
            line = '-' * 80
            with codecs.open(filename, 'w+', encoding='utf-8') as text_file:
                for block in blocks:
                    text_file.write('{0}\n{1}\n{0}\n{2}\n\n'.format(line, block[0],
                                                                    block[1]))

        self.status_animation('stop')
        all_files = len(self.file_table.selectionModel().selectedRows())
        self.popup('Finished!', '{} texts were saved from the {} processed.\n'
                                '{} files with no highlights.'
                   .format(saved, all_files, all_files - saved),
                   icon=QMessageBox.Information)

    ########################################################
    # __                  UTILITY STUFF                    #
    ########################################################

    @staticmethod
    def passed_files():
        """ Command line parameters that are passed to the program.
        """
        # args = QApplication.instance().arguments()
        try:
            if sys.argv[1]:
                for filename in sys.argv[1:]:
                    print(filename.decode('mbcs'))
        except IndexError:
            pass

    def popup(self, title, text, icon=QMessageBox.Warning, buttons=1,
              extra_text='', check_text=''):
        """ Creates and returns a Popup dialog
        :type title: str|unicode
        :param title: The Popup's title
        :type text: str|unicode
        :param text: The Popup's text
        :type icon: int
        :param icon: The Popup's icon
        :type buttons: int
        :param buttons: The number of the Popup's buttons
        :type extra_text: str|unicode
        :param extra_text: The extra button's text (omitted if '')
        :type check_text: str|unicode
        :param check_text: The checkbox's text (omitted if '')
        """
        popup = XMessageBox(self)
        popup.setWindowIcon(QIcon(":/stuff/icon.png"))
        popup.setIcon(icon)
        popup.setWindowTitle(title)
        popup.setText(text + '\n' if check_text else text)
        if buttons == 1:
            popup.addButton(_('Close'), QMessageBox.RejectRole)
        elif buttons == 2:
            popup.addButton(_('OK'), QMessageBox.AcceptRole)
            popup.addButton(_('Cancel'), QMessageBox.RejectRole)
        elif buttons == 3:
            popup.addButton(_('Yes'), QMessageBox.AcceptRole)
            popup.addButton(_('No'), QMessageBox.RejectRole)
        if extra_text:  # add an extra button
            popup.addButton(extra_text, QMessageBox.ApplyRole)

        if check_text:  # hide check_box if no text for it
            popup.check_box.setText(check_text)
        else:
            popup.check_box.hide()
        popup.checked = popup.exec_()[1]

        return popup

    def status_animation(self, action):
        """ Creates or deletes temporary files and folders
        :type action: str|unicode
        :param action: The action that must be done
        """
        if action == 'start':
            self.anim_lbl.show()
            self.wait_anim.start()
        elif action == 'stop':
            self.anim_lbl.hide()
            self.wait_anim.stop()

    @staticmethod
    def sanitize_filename(filename):
        """ Creates a safe filename.
        :type filename: str|unicode
        :param filename: The filename to be sanitized
        """
        filename = re.sub(r'[/:*?"<>|\\]', "_", filename)
        return filename

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
        try:
            version_new = self.about.get_online_version()
        except urllib2.URLError:  # can not connect
            return
        if not version_new:
            return
        if version_new > self.version and version_new != self.skip_version:
            popup = self.popup(_('Newer version exists!'),
                               _('There is a newer version (v.{}) online.\n'
                                 'Open the site to download it now?')
                               .format(version_new),
                               icon=QMessageBox.Information, buttons=2,
                               check_text=_('Don\'t alert me for this version again'))
            if popup.checked:
                self.skip_version = version_new
            if popup.clickedButton().text() == 'OK':
                webbrowser.open('http://www.noembryo.com/apps.php?kohighlights')

    def write_to_log(self, text):
        """ Append text to the QTextEdit.
        """
        # self.about.log_txt.appendPlainText(text)

        cursor = self.about.log_txt.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.about.log_txt.setTextCursor(cursor)
        self.about.log_txt.ensureCursorVisible()

        if self.sender().objectName() == 'err':
            text = '\033[91m' + text + '\033[0m'
        sys.__stdout__.write(text)

    def on_check_btn(self):
        QMessageBox.information(self, _('Info'), _('Tool button is pressed'))
        # QMessageBox.aboutQt(self, title="")


class About(QDialog, Ui_About):

    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        self.setupUi(self)
        # Remove the question mark widget from dialog
        self.setWindowFlags(self.windowFlags() ^
                            Qt.WindowContextHelpButtonHint)
        self.base = parent

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
            self.base.popup(_('No response!'), _('Version info is unreachable!\n'
                                                 'Please, try again later...'), buttons=1)
            return
        version = self.base.version
        if version_new > version:
            popup = self.base.popup(_('Newer version exists!'),
                                    _('There is a newer version (v.{}) online.\n'
                                      'Open the site to download it now?')
                                    .format(version_new),
                                    icon=QMessageBox.Information, buttons=2)
            if popup.clickedButton().text() == 'OK':
                webbrowser.open('http://www.noembryo.com/apps.php?katalib')
                self.close()
        elif version_new == version:
            self.base.popup(_('No newer version exists!'),
                            _('This is the latest version (v.{})').format(version),
                            icon=QMessageBox.Information, buttons=1)
        elif version_new < version:
            self.base.popup(_('No newer version exists!'),
                            _('It seems that you are using a newer version ({0})\n'
                              'than the one online ({1})!').format(version, version_new),
                            icon=QMessageBox.Question, buttons=1)

    @staticmethod
    def get_online_version():
        browser = mechanize.Browser()
        browser.set_handle_robots(False)

        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:14.0) '
                                'Gecko/20100101 Firefox/24.0.1',
                  'Referer': 'http://whateveritis.com'}
        url = "http://www.noembryo.com/apps.php?kohighlights"

        request = urllib2.Request(url, None, header)
        html_text = browser.open(request)
        soup_text = BeautifulSoup(html_text, "html5lib")
        results = soup_text.findAll(name='p')
        results = ''.join([str(i) for i in results])
        match = re.search(r"\d+\.\d+\.\d+\.\d+", results, re.DOTALL)
        try:
            version_new = match.group(0)
        except AttributeError:  # no match found
            return
        return version_new

    def create_text(self):
        # color = self.palette().color(QPalette.WindowText).name()  # for links
        splash = ":/stuff/logo.png"
        paypal = ":/stuff/paypal.png"
        info = """<body style="font-size:10pt; font-weight:400; font-style:normal">
        <center>
          <table width="100%" border="0">
            <tr>
                <p align="center"><img src="{0}" width="256" height ="212"></p>
                <p align="center">&nbsp;&nbsp;<b>KoHighlights</b> is a utility for
                viewing and converting<br/>the Koreader's history files to simple
                 text&nbsp;&nbsp;</p>
                <p align="center">Version {1}</p>
                <p align="center"><a href="https://github.com/noEmbryo/KoHighlights">
                 Visit  KoHighlights page at GitHub</a></p>
                <p align="center">Use it and if you like it, consider to
                <p align="center"><a href="https://www.paypal.com/cgi-bin/webscr?
                cmd=_s-xclick &hosted_button_id=RBYLVRYG9RU2S">
                <img src="{2}" alt="PayPal Button"
                width="142" height="27" border="0"></a></p>
                <p align="center">&nbsp;</p></td>
            </tr>
          </table>
        </center>
        </body>""".format(splash, self.base.version, paypal)
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

        self.check_btn.clicked.connect(parent.on_check_btn)
        self.check_btn.hide()

    @Slot()
    def on_select_btn_clicked(self):
        path = QFileDialog.getExistingDirectory(self.base,
                                                _("Select a directory with books"),
                                                self.base.last_dir,
                                                QFileDialog.ShowDirsOnly)
        if path:
            self.base.last_dir = path
            self.base.scan_files_thread(path)

    @Slot()
    def on_info_btn_clicked(self):
        """ The `Book Info` button is pressed
        """
        try:
            idx = self.base.file_table.selectionModel().selectedRows()[-1]
        except IndexError:  # nothing selected
            return
        item = self.base.file_table.item(idx.row(), 0)
        self.base.on_item_double_clicked(item)

    @Slot()
    def on_clear_btn_clicked(self):
        """ The `Clear` button is pressed
        """
        self.base.file_table.setRowCount(0)

    @Slot()
    def on_about_btn_clicked(self):
        """ The `About` button is pressed
        """
        self.base.about.create_text()
        self.base.about.show()

    @Slot()
    def on_exit_btn_clicked(self):
        """ The `Exit` button is pressed
        """
        self.base.close()


class LogStream(QObject):
    append_to_log = Signal(str)

    # def __init__(self):
    #     super(LogStream, self).__init__()
    #     # noinspection PyArgumentList
    #     self.base = QtGui.QApplication.instance().base

    def write(self, text):
        self.append_to_log.emit(text)


class Scanner(QObject):
    found = Signal(list)
    finished = Signal()

    def __init__(self, path):
        super(Scanner, self).__init__()
        self.path = path
        self.timer = QTimer(self)

    def process(self):
        self.start_scan()
        self.finished.emit()

    def start_scan(self):
        for i in os.walk(self.path):
            dir_path = i[0].lower()
            if dir_path.endswith('koreader\\history'):
                for j in i[2]:
                    if splitext(j)[1].lower() == '.lua':
                        filename = join(dir_path, j)
                        self.found.emit([filename])
                continue
            elif dir_path.endswith('.sdr'):
                if dir_path.endswith('evernote.sdr'):
                    continue
                filename = join(dir_path, i[2][0])
                if splitext(filename)[1] == '.lua':
                    self.found.emit([filename])


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


def print_error():
    with open("err_log.txt", "a") as log:
        log.write('\nCrash@{}\n'.format(time.strftime("%Y-%m-%d %H:%M:%S")))
    traceback.print_exc(file=open("err_log.txt", "a"))
    traceback.print_exc()


class KoHighlights(QApplication):
    def __init__(self, *args, **kwargs):
        super(KoHighlights, self).__init__(*args, **kwargs)

        # Change the current working directory to the directory of the module
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

        self.base = Base()
        self.base.passed_files()
        self.exec_()


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        app = KoHighlights(sys.argv)
    except:
        print_error()
