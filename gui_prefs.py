# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_prefs.ui',
# licensing of 'D:\Apps\DEV\PROJECTS\KoHighlights\gui_prefs.ui' applies.
#
# Created: Mon Nov  4 00:35:07 2024
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Prefs(object):
    def setupUi(self, Prefs):
        Prefs.setObjectName("Prefs")
        Prefs.resize(232, 373)
        Prefs.setToolTip("")
        Prefs.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Prefs)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Prefs)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.frame = QtWidgets.QFrame(Prefs)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.theme_box = QtWidgets.QComboBox(self.frame)
        self.theme_box.setObjectName("theme_box")
        self.theme_box.addItem("")
        self.theme_box.addItem("")
        self.theme_box.addItem("")
        self.theme_box.addItem("")
        self.theme_box.addItem("")
        self.theme_box.addItem("")
        self.horizontalLayout.addWidget(self.theme_box)
        spacerItem = QtWidgets.QSpacerItem(9, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addWidget(self.frame, 0, 1, 1, 1)
        self.alt_title_sort_chk = QtWidgets.QCheckBox(Prefs)
        self.alt_title_sort_chk.setObjectName("alt_title_sort_chk")
        self.gridLayout.addWidget(self.alt_title_sort_chk, 1, 0, 1, 2)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.frame_4 = QtWidgets.QFrame(Prefs)
        self.frame_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_2.addWidget(self.frame_4)
        self.groupBox = QtWidgets.QGroupBox(Prefs)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.show_page_chk = QtWidgets.QCheckBox(self.groupBox)
        self.show_page_chk.setCheckable(True)
        self.show_page_chk.setChecked(True)
        self.show_page_chk.setObjectName("show_page_chk")
        self.verticalLayout.addWidget(self.show_page_chk)
        self.show_date_chk = QtWidgets.QCheckBox(self.groupBox)
        self.show_date_chk.setChecked(True)
        self.show_date_chk.setObjectName("show_date_chk")
        self.verticalLayout.addWidget(self.show_date_chk)
        self.show_high_chk = QtWidgets.QCheckBox(self.groupBox)
        self.show_high_chk.setChecked(True)
        self.show_high_chk.setObjectName("show_high_chk")
        self.verticalLayout.addWidget(self.show_high_chk)
        self.show_chap_chk = QtWidgets.QCheckBox(self.groupBox)
        self.show_chap_chk.setChecked(True)
        self.show_chap_chk.setObjectName("show_chap_chk")
        self.verticalLayout.addWidget(self.show_chap_chk)
        self.show_comm_chk = QtWidgets.QCheckBox(self.groupBox)
        self.show_comm_chk.setChecked(True)
        self.show_comm_chk.setObjectName("show_comm_chk")
        self.verticalLayout.addWidget(self.show_comm_chk)
        self.show_ref_pg_chk = QtWidgets.QCheckBox(self.groupBox)
        self.show_ref_pg_chk.setChecked(True)
        self.show_ref_pg_chk.setObjectName("show_ref_pg_chk")
        self.verticalLayout.addWidget(self.show_ref_pg_chk)
        self.custom_date_btn = QtWidgets.QToolButton(self.groupBox)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/stuff/calendar.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.custom_date_btn.setIcon(icon)
        self.custom_date_btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.custom_date_btn.setObjectName("custom_date_btn")
        self.verticalLayout.addWidget(self.custom_date_btn)
        self.frame_6 = QtWidgets.QFrame(self.groupBox)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.custom_template_chk = QtWidgets.QCheckBox(self.frame_6)
        self.custom_template_chk.setObjectName("custom_template_chk")
        self.horizontalLayout_3.addWidget(self.custom_template_chk)
        self.custom_template_btn = QtWidgets.QToolButton(self.frame_6)
        self.custom_template_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/stuff/file_edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.custom_template_btn.setIcon(icon1)
        self.custom_template_btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.custom_template_btn.setObjectName("custom_template_btn")
        self.horizontalLayout_3.addWidget(self.custom_template_btn)
        self.verticalLayout.addWidget(self.frame_6)
        self.frame_3 = QtWidgets.QFrame(self.groupBox)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.sort_box = QtWidgets.QComboBox(self.frame_3)
        self.sort_box.setObjectName("sort_box")
        self.sort_box.addItem("")
        self.sort_box.addItem("")
        self.horizontalLayout_4.addWidget(self.sort_box)
        spacerItem1 = QtWidgets.QSpacerItem(76, 9, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.frame_3)
        self.verticalLayout_2.addWidget(self.groupBox)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.frame_5 = QtWidgets.QFrame(Prefs)
        self.frame_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.verticalLayout_2.addWidget(self.frame_5)
        self.frame_2 = QtWidgets.QFrame(Prefs)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem3 = QtWidgets.QSpacerItem(79, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.close_btn = QtWidgets.QPushButton(self.frame_2)
        self.close_btn.setObjectName("close_btn")
        self.horizontalLayout_2.addWidget(self.close_btn)
        spacerItem4 = QtWidgets.QSpacerItem(79, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.verticalLayout_2.addWidget(self.frame_2)

        self.retranslateUi(Prefs)
        QtCore.QObject.connect(self.close_btn, QtCore.SIGNAL("clicked()"), Prefs.close)
        QtCore.QMetaObject.connectSlotsByName(Prefs)

    def retranslateUi(self, Prefs):
        Prefs.setWindowTitle(QtWidgets.QApplication.translate("Prefs", "Preferences", None, -1))
        self.label.setToolTip(QtWidgets.QApplication.translate("Prefs", "Change the application\'s appearance", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Prefs", "Appearance", None, -1))
        self.theme_box.setToolTip(QtWidgets.QApplication.translate("Prefs", "Change the application\'s appearance", None, -1))
        self.theme_box.setItemText(0, QtWidgets.QApplication.translate("Prefs", "No theme - Old icons", None, -1))
        self.theme_box.setItemText(1, QtWidgets.QApplication.translate("Prefs", "No theme - New icons", None, -1))
        self.theme_box.setItemText(2, QtWidgets.QApplication.translate("Prefs", "Dark theme - Old icons", None, -1))
        self.theme_box.setItemText(3, QtWidgets.QApplication.translate("Prefs", "Dark theme - New icons", None, -1))
        self.theme_box.setItemText(4, QtWidgets.QApplication.translate("Prefs", "Light theme - Old icons", None, -1))
        self.theme_box.setItemText(5, QtWidgets.QApplication.translate("Prefs", "Light theme - New icons", None, -1))
        self.alt_title_sort_chk.setToolTip(QtWidgets.QApplication.translate("Prefs", "Ignore the english articles \"A\" and \"The\" when sorting by Title", None, -1))
        self.alt_title_sort_chk.setText(QtWidgets.QApplication.translate("Prefs", "Ignore english articles", None, -1))
        self.groupBox.setTitle(QtWidgets.QApplication.translate("Prefs", "Highlight Options", None, -1))
        self.show_page_chk.setToolTip(QtWidgets.QApplication.translate("Prefs", "Show the highlight\'s page number", None, -1))
        self.show_page_chk.setText(QtWidgets.QApplication.translate("Prefs", "Show page", None, -1))
        self.show_date_chk.setToolTip(QtWidgets.QApplication.translate("Prefs", "Show the highlight\'s date", None, -1))
        self.show_date_chk.setText(QtWidgets.QApplication.translate("Prefs", "Show date", None, -1))
        self.show_high_chk.setToolTip(QtWidgets.QApplication.translate("Prefs", "Show the highlight\'s text", None, -1))
        self.show_high_chk.setText(QtWidgets.QApplication.translate("Prefs", "Show highlight", None, -1))
        self.show_chap_chk.setToolTip(QtWidgets.QApplication.translate("Prefs", "Show the highlight\'s chapter", None, -1))
        self.show_chap_chk.setText(QtWidgets.QApplication.translate("Prefs", "Show chapter", None, -1))
        self.show_comm_chk.setToolTip(QtWidgets.QApplication.translate("Prefs", "Show the highlight\'s comment", None, -1))
        self.show_comm_chk.setText(QtWidgets.QApplication.translate("Prefs", "Show comment", None, -1))
        self.show_ref_pg_chk.setToolTip(QtWidgets.QApplication.translate("Prefs", "Prefer reference page numbers if exists", None, -1))
        self.show_ref_pg_chk.setText(QtWidgets.QApplication.translate("Prefs", "Use Reference page numbers", None, -1))
        self.custom_date_btn.setToolTip(QtWidgets.QApplication.translate("Prefs", "Change the way date is displayed", None, -1))
        self.custom_date_btn.setText(QtWidgets.QApplication.translate("Prefs", "Custom Date format", None, -1))
        self.custom_template_chk.setToolTip(QtWidgets.QApplication.translate("Prefs", "Use a custom template for Markdown export", None, -1))
        self.custom_template_chk.setText(QtWidgets.QApplication.translate("Prefs", "Custom Markdown", None, -1))
        self.custom_template_btn.setToolTip(QtWidgets.QApplication.translate("Prefs", "Edit the Markdown export template", None, -1))
        self.custom_template_btn.setText(QtWidgets.QApplication.translate("Prefs", "Edit", None, -1))
        self.sort_box.setToolTip(QtWidgets.QApplication.translate("Prefs", "Change the sorting method of the highlights", None, -1))
        self.sort_box.setItemText(0, QtWidgets.QApplication.translate("Prefs", "Sort Highlights by Date", None, -1))
        self.sort_box.setItemText(1, QtWidgets.QApplication.translate("Prefs", "Sort Highlights by Page", None, -1))
        self.close_btn.setText(QtWidgets.QApplication.translate("Prefs", "Close", None, -1))

import images_rc
