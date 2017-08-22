# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_status.ui'
#
# Created: Tue Aug 22 13:11:14 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Status(object):
    def setupUi(self, Status):
        Status.setObjectName("Status")
        Status.resize(266, 60)
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
        self.show_pages_btn = QtGui.QToolButton(self.frame)
        self.show_pages_btn.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/stuff/show_pages.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.show_pages_btn.setIcon(icon)
        self.show_pages_btn.setIconSize(QtCore.QSize(24, 24))
        self.show_pages_btn.setCheckable(True)
        self.show_pages_btn.setChecked(True)
        self.show_pages_btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.show_pages_btn.setObjectName("show_pages_btn")
        self.horizontalLayout.addWidget(self.show_pages_btn)
        self.horizontalLayout_2.addWidget(self.frame)

        self.retranslateUi(Status)
        QtCore.QMetaObject.connectSlotsByName(Status)

    def retranslateUi(self, Status):
        self.show_pages_btn.setToolTip(QtGui.QApplication.translate("Status", "Show/Hide the Page and the Date of each Highlight.\n"
"It also affects the saved text files.", None, QtGui.QApplication.UnicodeUTF8))
        self.show_pages_btn.setStatusTip(QtGui.QApplication.translate("Status", "Show/Hide the Page and the Date of each Highlight. It also affects the saved text files.", None, QtGui.QApplication.UnicodeUTF8))
        self.show_pages_btn.setText(QtGui.QApplication.translate("Status", "Show Pages/Dates", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
