# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui_filter.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFrame,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)
import images_rc

class Ui_Filter(object):
    def setupUi(self, Filter):
        if not Filter.objectName():
            Filter.setObjectName(u"Filter")
        Filter.resize(215, 66)
        Filter.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.verticalLayout = QVBoxLayout(Filter)
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.filter_frm1 = QFrame(Filter)
        self.filter_frm1.setObjectName(u"filter_frm1")
        self.filter_frm1.setFrameShape(QFrame.StyledPanel)
        self.filter_frm1.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.filter_frm1)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.filter_txt = QLineEdit(self.filter_frm1)
        self.filter_txt.setObjectName(u"filter_txt")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filter_txt.sizePolicy().hasHeightForWidth())
        self.filter_txt.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.filter_txt)

        self.filter_btn = QPushButton(self.filter_frm1)
        self.filter_btn.setObjectName(u"filter_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.filter_btn.sizePolicy().hasHeightForWidth())
        self.filter_btn.setSizePolicy(sizePolicy1)
        icon = QIcon()
        icon.addFile(u":/stuff/filter.png", QSize(), QIcon.Normal, QIcon.Off)
        self.filter_btn.setIcon(icon)

        self.horizontalLayout_4.addWidget(self.filter_btn)


        self.verticalLayout.addWidget(self.filter_frm1)

        self.filter_frm2 = QFrame(Filter)
        self.filter_frm2.setObjectName(u"filter_frm2")
        self.filter_frm2.setFrameShape(QFrame.StyledPanel)
        self.filter_frm2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.filter_frm2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.filter_box = QComboBox(self.filter_frm2)
        self.filter_box.addItem("")
        self.filter_box.addItem("")
        self.filter_box.addItem("")
        self.filter_box.addItem("")
        self.filter_box.setObjectName(u"filter_box")

        self.horizontalLayout.addWidget(self.filter_box)

        self.filtered_lbl = QLabel(self.filter_frm2)
        self.filtered_lbl.setObjectName(u"filtered_lbl")

        self.horizontalLayout.addWidget(self.filtered_lbl)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.clear_filter_btn = QPushButton(self.filter_frm2)
        self.clear_filter_btn.setObjectName(u"clear_filter_btn")
        sizePolicy1.setHeightForWidth(self.clear_filter_btn.sizePolicy().hasHeightForWidth())
        self.clear_filter_btn.setSizePolicy(sizePolicy1)
        icon1 = QIcon()
        icon1.addFile(u":/stuff/trash.png", QSize(), QIcon.Normal, QIcon.Off)
        self.clear_filter_btn.setIcon(icon1)

        self.horizontalLayout.addWidget(self.clear_filter_btn)


        self.verticalLayout.addWidget(self.filter_frm2)


        self.retranslateUi(Filter)

        self.filter_box.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Filter)
    # setupUi

    def retranslateUi(self, Filter):
#if QT_CONFIG(tooltip)
        self.filter_txt.setToolTip(QCoreApplication.translate("Filter", u"Type the keywords to filter the visible items", None))
#endif // QT_CONFIG(tooltip)
        self.filter_txt.setText("")
        self.filter_txt.setPlaceholderText(QCoreApplication.translate("Filter", u"Type here to filter...", None))
#if QT_CONFIG(tooltip)
        self.filter_btn.setToolTip(QCoreApplication.translate("Filter", u"Set filter", None))
#endif // QT_CONFIG(tooltip)
        self.filter_btn.setText(QCoreApplication.translate("Filter", u"Filter", None))
        self.filter_box.setItemText(0, QCoreApplication.translate("Filter", u"Filter All:", None))
        self.filter_box.setItemText(1, QCoreApplication.translate("Filter", u"Filter Highlights:", None))
        self.filter_box.setItemText(2, QCoreApplication.translate("Filter", u"Filter Comments:", None))
        self.filter_box.setItemText(3, QCoreApplication.translate("Filter", u"Filter Book Titles:", None))

#if QT_CONFIG(tooltip)
        self.filter_box.setToolTip(QCoreApplication.translate("Filter", u"Select where to search for the keywords", None))
#endif // QT_CONFIG(tooltip)
        self.filtered_lbl.setText("")
#if QT_CONFIG(tooltip)
        self.clear_filter_btn.setToolTip(QCoreApplication.translate("Filter", u"Clear the filter field", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.clear_filter_btn.setStatusTip(QCoreApplication.translate("Filter", u"Clears the filter field", None))
#endif // QT_CONFIG(statustip)
        self.clear_filter_btn.setText(QCoreApplication.translate("Filter", u"Clear", None))
        pass
    # retranslateUi

