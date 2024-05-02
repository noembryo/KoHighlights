# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_auto_info.ui',
# licensing of 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_auto_info.ui' applies.
#
# Created: Thu May  2 17:29:33 2024
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_AutoInfo(object):
    def setupUi(self, AutoInfo):
        AutoInfo.setObjectName("AutoInfo")
        AutoInfo.setWindowModality(QtCore.Qt.NonModal)
        AutoInfo.resize(300, 100)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AutoInfo.sizePolicy().hasHeightForWidth())
        AutoInfo.setSizePolicy(sizePolicy)
        AutoInfo.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        AutoInfo.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(AutoInfo)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(AutoInfo)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setFrameShape(QtWidgets.QFrame.Box)
        self.label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label.setText("")
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setMargin(6)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(AutoInfo)
        QtCore.QMetaObject.connectSlotsByName(AutoInfo)

    def retranslateUi(self, AutoInfo):
        AutoInfo.setWindowTitle(QtWidgets.QApplication.translate("AutoInfo", "Info", None, -1))

import images_rc
