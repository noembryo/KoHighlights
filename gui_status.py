# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_status.ui',
# licensing of 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_status.ui' applies.
#
# Created: Fri Oct  4 21:42:43 2024
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Status(object):
    def setupUi(self, Status):
        Status.setObjectName("Status")
        Status.resize(188, 38)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(Status)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frame = QtWidgets.QFrame(Status)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.anim_lbl = QtWidgets.QLabel(self.frame)
        self.anim_lbl.setText("")
        self.anim_lbl.setObjectName("anim_lbl")
        self.horizontalLayout.addWidget(self.anim_lbl)
        self.horizontalLayout_2.addWidget(self.frame)
        self.act_page = QtWidgets.QAction(Status)
        self.act_page.setCheckable(True)
        self.act_page.setObjectName("act_page")
        self.act_date = QtWidgets.QAction(Status)
        self.act_date.setCheckable(True)
        self.act_date.setObjectName("act_date")
        self.act_text = QtWidgets.QAction(Status)
        self.act_text.setCheckable(True)
        self.act_text.setObjectName("act_text")
        self.act_comment = QtWidgets.QAction(Status)
        self.act_comment.setCheckable(True)
        self.act_comment.setObjectName("act_comment")
        self.act_chapter = QtWidgets.QAction(Status)
        self.act_chapter.setCheckable(True)
        self.act_chapter.setObjectName("act_chapter")

        self.retranslateUi(Status)
        QtCore.QMetaObject.connectSlotsByName(Status)

    def retranslateUi(self, Status):
        self.act_page.setText(QtWidgets.QApplication.translate("Status", "Page", None, -1))
        self.act_page.setToolTip(QtWidgets.QApplication.translate("Status", "Show the highlight\'s page number", None, -1))
        self.act_date.setText(QtWidgets.QApplication.translate("Status", "Date", None, -1))
        self.act_date.setToolTip(QtWidgets.QApplication.translate("Status", "Show the highlight\'s date", None, -1))
        self.act_text.setText(QtWidgets.QApplication.translate("Status", "Highlight", None, -1))
        self.act_text.setToolTip(QtWidgets.QApplication.translate("Status", "Show the highlight\'s text", None, -1))
        self.act_comment.setText(QtWidgets.QApplication.translate("Status", "Comment", None, -1))
        self.act_comment.setToolTip(QtWidgets.QApplication.translate("Status", "Show the highlight\'s comment", None, -1))
        self.act_chapter.setText(QtWidgets.QApplication.translate("Status", "Chapter", None, -1))
        self.act_chapter.setToolTip(QtWidgets.QApplication.translate("Status", "Show the highlight\'s chapter", None, -1))

import images_rc
