# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_sync_item.ui',
# licensing of 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_sync_item.ui' applies.
#
# Created: Fri Oct  4 21:42:42 2024
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_SyncItem(object):
    def setupUi(self, SyncItem):
        SyncItem.setObjectName("SyncItem")
        SyncItem.resize(446, 25)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(SyncItem)
        self.horizontalLayout_2.setContentsMargins(4, 0, 2, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(SyncItem)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.sync_path_txt = QtWidgets.QLineEdit(SyncItem)
        self.sync_path_txt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sync_path_txt.setReadOnly(True)
        self.sync_path_txt.setObjectName("sync_path_txt")
        self.horizontalLayout_2.addWidget(self.sync_path_txt)
        self.sync_path_btn = QtWidgets.QPushButton(SyncItem)
        self.sync_path_btn.setObjectName("sync_path_btn")
        self.horizontalLayout_2.addWidget(self.sync_path_btn)
        self.frame = QtWidgets.QFrame(SyncItem)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.add_btn = QtWidgets.QToolButton(self.frame)
        self.add_btn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/stuff/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_btn.setIcon(icon)
        self.add_btn.setIconSize(QtCore.QSize(10, 10))
        self.add_btn.setObjectName("add_btn")
        self.horizontalLayout.addWidget(self.add_btn)
        self.del_btn = QtWidgets.QToolButton(self.frame)
        self.del_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/stuff/del.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.del_btn.setIcon(icon1)
        self.del_btn.setIconSize(QtCore.QSize(10, 10))
        self.del_btn.setObjectName("del_btn")
        self.horizontalLayout.addWidget(self.del_btn)
        self.horizontalLayout_2.addWidget(self.frame)

        self.retranslateUi(SyncItem)
        QtCore.QMetaObject.connectSlotsByName(SyncItem)

    def retranslateUi(self, SyncItem):
        self.label.setText(QtWidgets.QApplication.translate("SyncItem", "Sync path", None, -1))
        self.sync_path_txt.setToolTip(QtWidgets.QApplication.translate("SyncItem", "The path to the  book\'s metadata file", None, -1))
        self.sync_path_txt.setStatusTip(QtWidgets.QApplication.translate("SyncItem", "The path to the  book\'s metadata file", None, -1))
        self.sync_path_txt.setPlaceholderText(QtWidgets.QApplication.translate("SyncItem", "Select metadata file to sync", None, -1))
        self.sync_path_btn.setToolTip(QtWidgets.QApplication.translate("SyncItem", "Select/Change the metadata file path", None, -1))
        self.sync_path_btn.setStatusTip(QtWidgets.QApplication.translate("SyncItem", "Select/Change the metadata file path", None, -1))
        self.sync_path_btn.setText(QtWidgets.QApplication.translate("SyncItem", "Select", None, -1))
        self.add_btn.setToolTip(QtWidgets.QApplication.translate("SyncItem", "Add a new Sync path", None, -1))
        self.add_btn.setStatusTip(QtWidgets.QApplication.translate("SyncItem", "Add a new Sync path", None, -1))
        self.del_btn.setToolTip(QtWidgets.QApplication.translate("SyncItem", "Remove this Sync path", None, -1))
        self.del_btn.setStatusTip(QtWidgets.QApplication.translate("SyncItem", "Remove this Sync path", None, -1))

import images_rc
