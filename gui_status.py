# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_status.ui',
# licensing of 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_status.ui' applies.
#
# Created: Mon Aug 26 13:41:16 2024
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Status(object):
    def setupUi(self, Status):
        Status.setObjectName("Status")
        Status.resize(286, 32)
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
        self.theme_box = QtWidgets.QComboBox(self.frame)
        self.theme_box.setObjectName("theme_box")
        self.theme_box.addItem("")
        self.theme_box.addItem("")
        self.theme_box.addItem("")
        self.theme_box.addItem("")
        self.theme_box.addItem("")
        self.theme_box.addItem("")
        self.horizontalLayout.addWidget(self.theme_box)
        self.show_items_btn = QtWidgets.QToolButton(self.frame)
        self.show_items_btn.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/stuff/show_pages.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.show_items_btn.setIcon(icon)
        self.show_items_btn.setIconSize(QtCore.QSize(24, 24))
        self.show_items_btn.setChecked(False)
        self.show_items_btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.show_items_btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.show_items_btn.setObjectName("show_items_btn")
        self.horizontalLayout.addWidget(self.show_items_btn)
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
        self.theme_box.setItemText(0, QtWidgets.QApplication.translate("Status", "No theme - Old icons", None, -1))
        self.theme_box.setItemText(1, QtWidgets.QApplication.translate("Status", "No theme - New icons", None, -1))
        self.theme_box.setItemText(2, QtWidgets.QApplication.translate("Status", "Dark theme - Old icons", None, -1))
        self.theme_box.setItemText(3, QtWidgets.QApplication.translate("Status", "Dark theme - New icons", None, -1))
        self.theme_box.setItemText(4, QtWidgets.QApplication.translate("Status", "Light theme - Old icons", None, -1))
        self.theme_box.setItemText(5, QtWidgets.QApplication.translate("Status", "Light theme - New icons", None, -1))
        self.show_items_btn.setToolTip(QtWidgets.QApplication.translate("Status", "Show/Hide elements of Highlights. Also affects\n"
"what will be saved to the text/html files.", None, -1))
        self.show_items_btn.setStatusTip(QtWidgets.QApplication.translate("Status", "Show/Hide elements of Highlights. Also affects what will be saved to the text/html files.", None, -1))
        self.show_items_btn.setText(QtWidgets.QApplication.translate("Status", "Show in Highlights", None, -1))
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
