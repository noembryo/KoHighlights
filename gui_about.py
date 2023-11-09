# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui_about.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QPlainTextEdit, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QTabWidget, QVBoxLayout,
    QWidget)
import images_rc

class Ui_About(object):
    def setupUi(self, About):
        if not About.objectName():
            About.setObjectName(u"About")
        About.setWindowModality(Qt.ApplicationModal)
        About.resize(480, 560)
        About.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        About.setModal(False)
        self.verticalLayout = QVBoxLayout(About)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.about_tabs = QTabWidget(About)
        self.about_tabs.setObjectName(u"about_tabs")
        self.about_tabs.setTabShape(QTabWidget.Rounded)
        self.info_tab = QWidget()
        self.info_tab.setObjectName(u"info_tab")
        self.verticalLayout_2 = QVBoxLayout(self.info_tab)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea_2 = QScrollArea(self.info_tab)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setStyleSheet(u"QScrollArea {background-color:transparent;}")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 454, 485))
        self.scrollAreaWidgetContents_2.setStyleSheet(u"background-color:transparent;")
        self.verticalLayout_6 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(6, 0, 6, 0)
        self.text_lbl = QLabel(self.scrollAreaWidgetContents_2)
        self.text_lbl.setObjectName(u"text_lbl")
        self.text_lbl.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.text_lbl.setWordWrap(True)
        self.text_lbl.setOpenExternalLinks(True)

        self.verticalLayout_6.addWidget(self.text_lbl)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_2.addWidget(self.scrollArea_2)

        self.about_tabs.addTab(self.info_tab, "")
        self.log_tab = QWidget()
        self.log_tab.setObjectName(u"log_tab")
        self.verticalLayout_8 = QVBoxLayout(self.log_tab)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.log_txt = QPlainTextEdit(self.log_tab)
        self.log_txt.setObjectName(u"log_txt")
        self.log_txt.setFrameShape(QFrame.WinPanel)
        self.log_txt.setDocumentTitle(u"")
        self.log_txt.setUndoRedoEnabled(False)
        self.log_txt.setReadOnly(True)
        self.log_txt.setPlainText(u"")

        self.verticalLayout_8.addWidget(self.log_txt)

        self.about_tabs.addTab(self.log_tab, "")

        self.verticalLayout.addWidget(self.about_tabs)

        self.btn_box = QFrame(About)
        self.btn_box.setObjectName(u"btn_box")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_box.sizePolicy().hasHeightForWidth())
        self.btn_box.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.btn_box)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.about_qt_btn = QPushButton(self.btn_box)
        self.about_qt_btn.setObjectName(u"about_qt_btn")

        self.horizontalLayout.addWidget(self.about_qt_btn)

        self.horizontalSpacer_2 = QSpacerItem(92, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.updates_btn = QPushButton(self.btn_box)
        self.updates_btn.setObjectName(u"updates_btn")

        self.horizontalLayout.addWidget(self.updates_btn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.close_btn = QPushButton(self.btn_box)
        self.close_btn.setObjectName(u"close_btn")

        self.horizontalLayout.addWidget(self.close_btn)


        self.verticalLayout.addWidget(self.btn_box)


        self.retranslateUi(About)
        self.close_btn.clicked.connect(About.close)

        self.about_tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(About)
    # setupUi

    def retranslateUi(self, About):
        self.text_lbl.setText("")
        self.about_tabs.setTabText(self.about_tabs.indexOf(self.info_tab), QCoreApplication.translate("About", u"Information", None))
        self.about_tabs.setTabText(self.about_tabs.indexOf(self.log_tab), QCoreApplication.translate("About", u"Log", None))
        self.about_qt_btn.setText(QCoreApplication.translate("About", u"About Qt", None))
#if QT_CONFIG(tooltip)
        self.updates_btn.setToolTip(QCoreApplication.translate("About", u"Check online for an updated version", None))
#endif // QT_CONFIG(tooltip)
        self.updates_btn.setText(QCoreApplication.translate("About", u"Check for Updates", None))
        self.close_btn.setText(QCoreApplication.translate("About", u"Close", None))
        pass
    # retranslateUi

