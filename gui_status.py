# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui_status.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QSizePolicy, QToolButton, QWidget)
import images_rc

class Ui_Status(object):
    def setupUi(self, Status):
        if not Status.objectName():
            Status.setObjectName(u"Status")
        Status.resize(277, 55)
        self.act_page = QAction(Status)
        self.act_page.setObjectName(u"act_page")
        self.act_page.setCheckable(True)
        self.act_date = QAction(Status)
        self.act_date.setObjectName(u"act_date")
        self.act_date.setCheckable(True)
        self.act_text = QAction(Status)
        self.act_text.setObjectName(u"act_text")
        self.act_text.setCheckable(True)
        self.act_comment = QAction(Status)
        self.act_comment.setObjectName(u"act_comment")
        self.act_comment.setCheckable(True)
        self.act_chapter = QAction(Status)
        self.act_chapter.setObjectName(u"act_chapter")
        self.act_chapter.setCheckable(True)
        self.horizontalLayout_2 = QHBoxLayout(Status)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame = QFrame(Status)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.anim_lbl = QLabel(self.frame)
        self.anim_lbl.setObjectName(u"anim_lbl")

        self.horizontalLayout.addWidget(self.anim_lbl)

        self.show_items_btn = QToolButton(self.frame)
        self.show_items_btn.setObjectName(u"show_items_btn")
        self.show_items_btn.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        icon = QIcon()
        icon.addFile(u":/stuff/show_pages.png", QSize(), QIcon.Normal, QIcon.Off)
        self.show_items_btn.setIcon(icon)
        self.show_items_btn.setIconSize(QSize(24, 24))
        self.show_items_btn.setChecked(False)
        self.show_items_btn.setPopupMode(QToolButton.InstantPopup)
        self.show_items_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.show_items_btn)


        self.horizontalLayout_2.addWidget(self.frame)


        self.retranslateUi(Status)

        QMetaObject.connectSlotsByName(Status)
    # setupUi

    def retranslateUi(self, Status):
        Status.setWindowTitle("")
        self.act_page.setText(QCoreApplication.translate("Status", u"Page", None))
        self.act_date.setText(QCoreApplication.translate("Status", u"Date", None))
        self.act_text.setText(QCoreApplication.translate("Status", u"Highlight", None))
        self.act_comment.setText(QCoreApplication.translate("Status", u"Comment", None))
        self.act_chapter.setText(QCoreApplication.translate("Status", u"Chapter", None))
#if QT_CONFIG(tooltip)
        self.act_chapter.setToolTip(QCoreApplication.translate("Status", u"Chapter", None))
#endif // QT_CONFIG(tooltip)
        self.anim_lbl.setText("")
#if QT_CONFIG(tooltip)
        self.show_items_btn.setToolTip(QCoreApplication.translate("Status", u"Show/Hide elements of Highlights. Also affects\n"
"what will be saved to the text/html files.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.show_items_btn.setStatusTip(QCoreApplication.translate("Status", u"Show/Hide elements of Highlights. Also affects what will be saved to the text/html files.", None))
#endif // QT_CONFIG(statustip)
        self.show_items_btn.setText(QCoreApplication.translate("Status", u"Show in Highlights", None))
    # retranslateUi

