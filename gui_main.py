# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui_main.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QSizePolicy,
    QSplitter, QStackedWidget, QStatusBar, QTableWidget,
    QTableWidgetItem, QToolBar, QToolButton, QVBoxLayout,
    QWidget)

from secondary import DropTableWidget
import images_rc

class Ui_Base(object):
    def setupUi(self, Base):
        if not Base.objectName():
            Base.setObjectName(u"Base")
        Base.resize(640, 512)
        icon = QIcon()
        icon.addFile(u":/stuff/logo64.png", QSize(), QIcon.Normal, QIcon.Off)
        Base.setWindowIcon(icon)
        Base.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        Base.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.act_english = QAction(Base)
        self.act_english.setObjectName(u"act_english")
        self.act_english.setCheckable(True)
        self.act_english.setChecked(False)
        self.act_greek = QAction(Base)
        self.act_greek.setObjectName(u"act_greek")
        self.act_greek.setCheckable(True)
        self.act_greek.setChecked(False)
        self.act_view_book = QAction(Base)
        self.act_view_book.setObjectName(u"act_view_book")
        icon1 = QIcon()
        icon1.addFile(u":/stuff/files_view.png", QSize(), QIcon.Normal, QIcon.Off)
        self.act_view_book.setIcon(icon1)
        self.centralwidget = QWidget(Base)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.views = QStackedWidget(self.centralwidget)
        self.views.setObjectName(u"views")
        self.books_pg = QWidget()
        self.books_pg.setObjectName(u"books_pg")
        self.verticalLayout_3 = QVBoxLayout(self.books_pg)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.splitter = QSplitter(self.books_pg)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.file_table = DropTableWidget(self.splitter)
        if (self.file_table.columnCount() < 8):
            self.file_table.setColumnCount(8)
        __qtablewidgetitem = QTableWidgetItem()
        self.file_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.file_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.file_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.file_table.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.file_table.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.file_table.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.file_table.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.file_table.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        self.file_table.setObjectName(u"file_table")
        self.file_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_table.setFrameShape(QFrame.WinPanel)
        self.file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.file_table.setDragDropMode(QAbstractItemView.DropOnly)
        self.file_table.setDefaultDropAction(Qt.CopyAction)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.file_table.setSortingEnabled(True)
        self.file_table.setWordWrap(False)
        self.file_table.setCornerButtonEnabled(False)
        self.file_table.setColumnCount(8)
        self.splitter.addWidget(self.file_table)
        self.file_table.horizontalHeader().setMinimumSectionSize(22)
        self.file_table.horizontalHeader().setDefaultSectionSize(22)
        self.file_table.horizontalHeader().setHighlightSections(False)
        self.file_table.horizontalHeader().setProperty("showSortIndicator", True)
        self.file_table.verticalHeader().setMinimumSectionSize(22)
        self.file_table.verticalHeader().setDefaultSectionSize(22)
        self.file_table.verticalHeader().setHighlightSections(True)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.WinPanel)
        self.frame.setFrameShadow(QFrame.Sunken)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.header = QWidget(self.frame)
        self.header.setObjectName(u"header")
        self.horizontalLayout = QHBoxLayout(self.header)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, -1, 0)
        self.fold_btn = QToolButton(self.header)
        self.fold_btn.setObjectName(u"fold_btn")
        self.fold_btn.setStyleSheet(u"QToolButton{border:none;}")
        self.fold_btn.setCheckable(True)
        self.fold_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.fold_btn.setArrowType(Qt.DownArrow)

        self.horizontalLayout.addWidget(self.fold_btn)

        self.frame_2 = QFrame(self.header)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QFrame.HLine)
        self.frame_2.setFrameShadow(QFrame.Sunken)
        self.frame_2.setLineWidth(1)

        self.horizontalLayout.addWidget(self.frame_2)


        self.verticalLayout.addWidget(self.header)

        self.book_info = QFrame(self.frame)
        self.book_info.setObjectName(u"book_info")
        self.book_info.setFrameShape(QFrame.StyledPanel)
        self.book_info.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.book_info)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(6, 0, 6, 0)
        self.title_lbl = QLabel(self.book_info)
        self.title_lbl.setObjectName(u"title_lbl")

        self.gridLayout.addWidget(self.title_lbl, 0, 0, 1, 1)

        self.series_lbl = QLabel(self.book_info)
        self.series_lbl.setObjectName(u"series_lbl")

        self.gridLayout.addWidget(self.series_lbl, 2, 0, 1, 1)

        self.author_lbl = QLabel(self.book_info)
        self.author_lbl.setObjectName(u"author_lbl")

        self.gridLayout.addWidget(self.author_lbl, 1, 0, 1, 1)

        self.lang_lbl = QLabel(self.book_info)
        self.lang_lbl.setObjectName(u"lang_lbl")

        self.gridLayout.addWidget(self.lang_lbl, 4, 0, 1, 1)

        self.pages_lbl = QLabel(self.book_info)
        self.pages_lbl.setObjectName(u"pages_lbl")

        self.gridLayout.addWidget(self.pages_lbl, 4, 2, 1, 1)

        self.lang_txt = QLineEdit(self.book_info)
        self.lang_txt.setObjectName(u"lang_txt")
        self.lang_txt.setReadOnly(True)

        self.gridLayout.addWidget(self.lang_txt, 4, 1, 1, 1)

        self.pages_txt = QLineEdit(self.book_info)
        self.pages_txt.setObjectName(u"pages_txt")
        self.pages_txt.setReadOnly(True)

        self.gridLayout.addWidget(self.pages_txt, 4, 3, 1, 1)

        self.tags_lbl = QLabel(self.book_info)
        self.tags_lbl.setObjectName(u"tags_lbl")

        self.gridLayout.addWidget(self.tags_lbl, 3, 0, 1, 1)

        self.description_btn = QToolButton(self.book_info)
        self.description_btn.setObjectName(u"description_btn")
        icon2 = QIcon()
        icon2.addFile(u":/stuff/description.png", QSize(), QIcon.Normal, QIcon.Off)
        self.description_btn.setIcon(icon2)
        self.description_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.gridLayout.addWidget(self.description_btn, 4, 4, 1, 1)

        self.tags_txt = QLineEdit(self.book_info)
        self.tags_txt.setObjectName(u"tags_txt")
        self.tags_txt.setReadOnly(True)

        self.gridLayout.addWidget(self.tags_txt, 3, 1, 1, 4)

        self.series_txt = QLineEdit(self.book_info)
        self.series_txt.setObjectName(u"series_txt")
        self.series_txt.setReadOnly(True)

        self.gridLayout.addWidget(self.series_txt, 2, 1, 1, 4)

        self.author_txt = QLineEdit(self.book_info)
        self.author_txt.setObjectName(u"author_txt")
        self.author_txt.setReadOnly(True)

        self.gridLayout.addWidget(self.author_txt, 1, 1, 1, 4)

        self.title_txt = QLineEdit(self.book_info)
        self.title_txt.setObjectName(u"title_txt")
        self.title_txt.setReadOnly(True)

        self.gridLayout.addWidget(self.title_txt, 0, 1, 1, 4)

        self.review_lbl = QLabel(self.book_info)
        self.review_lbl.setObjectName(u"review_lbl")
        self.review_lbl.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout.addWidget(self.review_lbl, 5, 0, 1, 1)

        self.review_txt = QLabel(self.book_info)
        self.review_txt.setObjectName(u"review_txt")
        self.review_txt.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.review_txt.setFrameShape(QFrame.NoFrame)
        self.review_txt.setWordWrap(True)

        self.gridLayout.addWidget(self.review_txt, 5, 1, 1, 4)


        self.verticalLayout.addWidget(self.book_info)

        self.high_list = QListWidget(self.frame)
        self.high_list.setObjectName(u"high_list")
        self.high_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.high_list.setFrameShape(QFrame.WinPanel)
        self.high_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.high_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.high_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.high_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.high_list.setWordWrap(True)

        self.verticalLayout.addWidget(self.high_list)

        self.splitter.addWidget(self.frame)

        self.verticalLayout_3.addWidget(self.splitter)

        self.views.addWidget(self.books_pg)
        self.highlights_pg = QWidget()
        self.highlights_pg.setObjectName(u"highlights_pg")
        self.verticalLayout_4 = QVBoxLayout(self.highlights_pg)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.high_table = QTableWidget(self.highlights_pg)
        if (self.high_table.columnCount() < 8):
            self.high_table.setColumnCount(8)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.high_table.setHorizontalHeaderItem(0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.high_table.setHorizontalHeaderItem(1, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.high_table.setHorizontalHeaderItem(2, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.high_table.setHorizontalHeaderItem(3, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.high_table.setHorizontalHeaderItem(4, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.high_table.setHorizontalHeaderItem(5, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.high_table.setHorizontalHeaderItem(6, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.high_table.setHorizontalHeaderItem(7, __qtablewidgetitem15)
        self.high_table.setObjectName(u"high_table")
        self.high_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.high_table.setFrameShape(QFrame.WinPanel)
        self.high_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.high_table.setDragDropMode(QAbstractItemView.DropOnly)
        self.high_table.setDefaultDropAction(Qt.CopyAction)
        self.high_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.high_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.high_table.setSortingEnabled(True)
        self.high_table.setWordWrap(False)
        self.high_table.setCornerButtonEnabled(False)
        self.high_table.setColumnCount(8)
        self.high_table.horizontalHeader().setMinimumSectionSize(22)
        self.high_table.horizontalHeader().setHighlightSections(False)
        self.high_table.horizontalHeader().setProperty("showSortIndicator", True)
        self.high_table.horizontalHeader().setStretchLastSection(True)
        self.high_table.verticalHeader().setMinimumSectionSize(22)
        self.high_table.verticalHeader().setDefaultSectionSize(22)
        self.high_table.verticalHeader().setHighlightSections(True)

        self.verticalLayout_4.addWidget(self.high_table)

        self.views.addWidget(self.highlights_pg)

        self.verticalLayout_2.addWidget(self.views)

        Base.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(Base)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setStyleSheet(u"QStatusBar{padding-left:8px;font-weight:bold;}")
        Base.setStatusBar(self.statusbar)
        self.tool_bar = QToolBar(Base)
        self.tool_bar.setObjectName(u"tool_bar")
        self.tool_bar.setWindowTitle(u"toolBar")
        self.tool_bar.setMovable(True)
        self.tool_bar.setAllowedAreas(Qt.BottomToolBarArea|Qt.TopToolBarArea)
        self.tool_bar.setIconSize(QSize(32, 32))
        self.tool_bar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        Base.addToolBar(Qt.TopToolBarArea, self.tool_bar)

        self.retranslateUi(Base)

        self.views.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Base)
    # setupUi

    def retranslateUi(self, Base):
        self.act_english.setText(QCoreApplication.translate("Base", u"English", None))
        self.act_greek.setText(QCoreApplication.translate("Base", u"Greek", None))
        self.act_view_book.setText(QCoreApplication.translate("Base", u"View Book", None))
#if QT_CONFIG(shortcut)
        self.act_view_book.setShortcut(QCoreApplication.translate("Base", u"Ctrl+B", None))
#endif // QT_CONFIG(shortcut)
        ___qtablewidgetitem = self.file_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Base", u"Title", None));
        ___qtablewidgetitem1 = self.file_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Base", u"Author", None));
        ___qtablewidgetitem2 = self.file_table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Base", u"Type", None));
        ___qtablewidgetitem3 = self.file_table.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Base", u"Percent", None));
        ___qtablewidgetitem4 = self.file_table.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Base", u"Rating", None));
        ___qtablewidgetitem5 = self.file_table.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Base", u"Highlights", None));
        ___qtablewidgetitem6 = self.file_table.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("Base", u"Modified", None));
        ___qtablewidgetitem7 = self.file_table.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("Base", u"Path", None));
        self.fold_btn.setText(QCoreApplication.translate("Base", u"Hide Book Info", None))
        self.title_lbl.setText(QCoreApplication.translate("Base", u"Title", None))
        self.series_lbl.setText(QCoreApplication.translate("Base", u"Series", None))
        self.author_lbl.setText(QCoreApplication.translate("Base", u"Author", None))
        self.lang_lbl.setText(QCoreApplication.translate("Base", u"Language", None))
        self.pages_lbl.setText(QCoreApplication.translate("Base", u"Pages", None))
        self.tags_lbl.setText(QCoreApplication.translate("Base", u"Tags", None))
        self.description_btn.setText(QCoreApplication.translate("Base", u"Description", None))
        self.review_lbl.setText(QCoreApplication.translate("Base", u"Review", None))
        self.review_txt.setText("")
        ___qtablewidgetitem8 = self.high_table.horizontalHeaderItem(0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("Base", u"Highlight", None));
        ___qtablewidgetitem9 = self.high_table.horizontalHeaderItem(1)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("Base", u"Comment", None));
        ___qtablewidgetitem10 = self.high_table.horizontalHeaderItem(2)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("Base", u"Date", None));
        ___qtablewidgetitem11 = self.high_table.horizontalHeaderItem(3)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("Base", u"Title", None));
        ___qtablewidgetitem12 = self.high_table.horizontalHeaderItem(4)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("Base", u"Author", None));
        ___qtablewidgetitem13 = self.high_table.horizontalHeaderItem(5)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("Base", u"Page", None));
        ___qtablewidgetitem14 = self.high_table.horizontalHeaderItem(6)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("Base", u"Chapter", None));
        ___qtablewidgetitem15 = self.high_table.horizontalHeaderItem(7)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("Base", u"Book path", None));
        pass
    # retranslateUi

