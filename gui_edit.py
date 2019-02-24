# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_edit.ui'
#
# Created: Sun Feb 24 17:33:31 2019
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_TextDialog(object):
    def setupUi(self, TextDialog):
        TextDialog.setObjectName("TextDialog")
        TextDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        TextDialog.resize(360, 180)
        TextDialog.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        TextDialog.setModal(False)
        self.verticalLayout = QtGui.QVBoxLayout(TextDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.high_edit_txt = QtGui.QTextEdit(TextDialog)
        self.high_edit_txt.setFrameShape(QtGui.QFrame.WinPanel)
        self.high_edit_txt.setAcceptRichText(False)
        self.high_edit_txt.setObjectName("high_edit_txt")
        self.verticalLayout.addWidget(self.high_edit_txt)
        self.btn_box = QtGui.QFrame(TextDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_box.sizePolicy().hasHeightForWidth())
        self.btn_box.setSizePolicy(sizePolicy)
        self.btn_box.setFrameShape(QtGui.QFrame.StyledPanel)
        self.btn_box.setFrameShadow(QtGui.QFrame.Raised)
        self.btn_box.setObjectName("btn_box")
        self.horizontalLayout = QtGui.QHBoxLayout(self.btn_box)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(175, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.ok_btn = QtGui.QPushButton(self.btn_box)
        self.ok_btn.setObjectName("ok_btn")
        self.horizontalLayout.addWidget(self.ok_btn)
        self.cancel_btn = QtGui.QPushButton(self.btn_box)
        self.cancel_btn.setObjectName("cancel_btn")
        self.horizontalLayout.addWidget(self.cancel_btn)
        self.verticalLayout.addWidget(self.btn_box)

        self.retranslateUi(TextDialog)
        QtCore.QObject.connect(self.cancel_btn, QtCore.SIGNAL("clicked()"), TextDialog.close)
        QtCore.QObject.connect(self.ok_btn, QtCore.SIGNAL("clicked()"), TextDialog.close)
        QtCore.QMetaObject.connectSlotsByName(TextDialog)

    def retranslateUi(self, TextDialog):
        self.ok_btn.setToolTip(QtGui.QApplication.translate("TextDialog", "Check online for an updated version", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("TextDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("TextDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

import images_rc
