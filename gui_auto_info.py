# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui_auto_info.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QLabel,
    QSizePolicy, QVBoxLayout, QWidget)
import images_rc

class Ui_AutoInfo(object):
    def setupUi(self, AutoInfo):
        if not AutoInfo.objectName():
            AutoInfo.setObjectName(u"AutoInfo")
        AutoInfo.setWindowModality(Qt.NonModal)
        AutoInfo.resize(300, 100)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AutoInfo.sizePolicy().hasHeightForWidth())
        AutoInfo.setSizePolicy(sizePolicy)
        AutoInfo.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        AutoInfo.setModal(True)
        self.verticalLayout = QVBoxLayout(AutoInfo)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(AutoInfo)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setFrameShape(QFrame.Box)
        self.label.setFrameShadow(QFrame.Raised)
        self.label.setTextFormat(Qt.AutoText)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMargin(6)

        self.verticalLayout.addWidget(self.label)


        self.retranslateUi(AutoInfo)

        QMetaObject.connectSlotsByName(AutoInfo)
    # setupUi

    def retranslateUi(self, AutoInfo):
        AutoInfo.setWindowTitle(QCoreApplication.translate("AutoInfo", u"Info", None))
        self.label.setText("")
    # retranslateUi

