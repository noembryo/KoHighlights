# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_status.ui'
#
# Created: Tue Sep 19 17:26:06 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Status(object):
    def setupUi(self, Status):
        Status.setObjectName("Status")
        Status.resize(277, 55)
        Status.setWindowTitle("")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(Status)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frame = QtGui.QFrame(Status)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.anim_lbl = QtGui.QLabel(self.frame)
        self.anim_lbl.setText("")
        self.anim_lbl.setObjectName("anim_lbl")
        self.horizontalLayout.addWidget(self.anim_lbl)
        self.show_items_btn = QtGui.QToolButton(self.frame)
        self.show_items_btn.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/stuff/show_pages.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.show_items_btn.setIcon(icon)
        self.show_items_btn.setIconSize(QtCore.QSize(24, 24))
        self.show_items_btn.setChecked(False)
        self.show_items_btn.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.show_items_btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.show_items_btn.setObjectName("show_items_btn")
        self.horizontalLayout.addWidget(self.show_items_btn)
        self.horizontalLayout_2.addWidget(self.frame)
        self.act_page = QtGui.QAction(Status)
        self.act_page.setCheckable(True)
        self.act_page.setObjectName("act_page")
        self.act_date = QtGui.QAction(Status)
        self.act_date.setCheckable(True)
        self.act_date.setObjectName("act_date")
        self.act_text = QtGui.QAction(Status)
        self.act_text.setCheckable(True)
        self.act_text.setObjectName("act_text")

        self.retranslateUi(Status)
        QtCore.QMetaObject.connectSlotsByName(Status)

    def retranslateUi(self, Status):
        self.show_items_btn.setToolTip(QtGui.QApplication.translate("Status", "Show/Hide elements of Highlights.\n"
"It also affects the saved text files.", None, QtGui.QApplication.UnicodeUTF8))
        self.show_items_btn.setStatusTip(QtGui.QApplication.translate("Status", "Show/Hide elements of Highlights.\\nIt also affects the saved text files.", None, QtGui.QApplication.UnicodeUTF8))
        self.show_items_btn.setText(QtGui.QApplication.translate("Status", "Show in Highlights", None, QtGui.QApplication.UnicodeUTF8))
        self.act_page.setText(QtGui.QApplication.translate("Status", "Page", None, QtGui.QApplication.UnicodeUTF8))
        self.act_date.setText(QtGui.QApplication.translate("Status", "Date", None, QtGui.QApplication.UnicodeUTF8))
        self.act_text.setText(QtGui.QApplication.translate("Status", "Highlight", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
