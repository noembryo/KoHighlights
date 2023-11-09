# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui_edit.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QPushButton, QSizePolicy, QSpacerItem, QTextEdit,
    QVBoxLayout, QWidget)
import images_rc

class Ui_TextDialog(object):
    def setupUi(self, TextDialog):
        if not TextDialog.objectName():
            TextDialog.setObjectName(u"TextDialog")
        TextDialog.setWindowModality(Qt.ApplicationModal)
        TextDialog.resize(360, 180)
        TextDialog.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        TextDialog.setModal(False)
        self.verticalLayout = QVBoxLayout(TextDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.high_edit_txt = QTextEdit(TextDialog)
        self.high_edit_txt.setObjectName(u"high_edit_txt")
        self.high_edit_txt.setFrameShape(QFrame.WinPanel)
        self.high_edit_txt.setAcceptRichText(False)

        self.verticalLayout.addWidget(self.high_edit_txt)

        self.btn_box = QFrame(TextDialog)
        self.btn_box.setObjectName(u"btn_box")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_box.sizePolicy().hasHeightForWidth())
        self.btn_box.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.btn_box)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(175, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.ok_btn = QPushButton(self.btn_box)
        self.ok_btn.setObjectName(u"ok_btn")

        self.horizontalLayout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self.btn_box)
        self.cancel_btn.setObjectName(u"cancel_btn")

        self.horizontalLayout.addWidget(self.cancel_btn)


        self.verticalLayout.addWidget(self.btn_box)


        self.retranslateUi(TextDialog)
        self.cancel_btn.clicked.connect(TextDialog.close)
        self.ok_btn.clicked.connect(TextDialog.close)

        QMetaObject.connectSlotsByName(TextDialog)
    # setupUi

    def retranslateUi(self, TextDialog):
#if QT_CONFIG(tooltip)
        self.ok_btn.setToolTip(QCoreApplication.translate("TextDialog", u"Check online for an updated version", None))
#endif // QT_CONFIG(tooltip)
        self.ok_btn.setText(QCoreApplication.translate("TextDialog", u"OK", None))
        self.cancel_btn.setText(QCoreApplication.translate("TextDialog", u"Cancel", None))
        pass
    # retranslateUi

