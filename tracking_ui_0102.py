# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'trackingmsILCG.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QTextBrowser, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(452, 700)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label_title = QLabel(self.centralwidget)
        self.label_title.setObjectName(u"label_title")
        self.label_title.setGeometry(QRect(110, 10, 261, 71))
        font = QFont()
        font.setPointSize(20)
        self.label_title.setFont(font)
        self.verticalLayoutWidget_4 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_4.setObjectName(u"verticalLayoutWidget_4")
        self.verticalLayoutWidget_4.setGeometry(QRect(50, 260, 351, 80))
        self.verticalLayout_4 = QVBoxLayout(self.verticalLayoutWidget_4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.lbl_subtitle2 = QLabel(self.verticalLayoutWidget_4)
        self.lbl_subtitle2.setObjectName(u"lbl_subtitle2")
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        self.lbl_subtitle2.setFont(font1)

        self.verticalLayout_4.addWidget(self.lbl_subtitle2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btn_fileopen = QPushButton(self.verticalLayoutWidget_4)
        self.btn_fileopen.setObjectName(u"btn_fileopen")
        font2 = QFont()
        font2.setPointSize(10)
        self.btn_fileopen.setFont(font2)

        self.horizontalLayout.addWidget(self.btn_fileopen)

        self.lineEdit_path = QLineEdit(self.verticalLayoutWidget_4)
        self.lineEdit_path.setObjectName(u"lineEdit_path")

        self.horizontalLayout.addWidget(self.lineEdit_path)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(50, 100, 199, 132))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.lbl_subTitle1 = QLabel(self.verticalLayoutWidget)
        self.lbl_subTitle1.setObjectName(u"lbl_subTitle1")
        self.lbl_subTitle1.setFont(font1)

        self.verticalLayout.addWidget(self.lbl_subTitle1)

        self.lbl_id = QLabel(self.verticalLayoutWidget)
        self.lbl_id.setObjectName(u"lbl_id")
        font3 = QFont()
        font3.setPointSize(10)
        font3.setBold(True)
        self.lbl_id.setFont(font3)

        self.verticalLayout.addWidget(self.lbl_id)

        self.lineEdit_id = QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_id.setObjectName(u"lineEdit_id")
        self.lineEdit_id.setFont(font2)

        self.verticalLayout.addWidget(self.lineEdit_id)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lbl_pw = QLabel(self.verticalLayoutWidget)
        self.lbl_pw.setObjectName(u"lbl_pw")
        self.lbl_pw.setFont(font3)

        self.verticalLayout_2.addWidget(self.lbl_pw)

        self.lineEdit_pw = QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_pw.setObjectName(u"lineEdit_pw")
        self.lineEdit_pw.setFont(font2)

        self.verticalLayout_2.addWidget(self.lineEdit_pw)


        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayoutWidget_3 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(50, 370, 351, 201))
        self.verticalLayout_3 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.lbl_subTitle3 = QLabel(self.verticalLayoutWidget_3)
        self.lbl_subTitle3.setObjectName(u"lbl_subTitle3")
        self.lbl_subTitle3.setFont(font1)

        self.verticalLayout_3.addWidget(self.lbl_subTitle3)

        self.textBrowser = QTextBrowser(self.verticalLayoutWidget_3)
        self.textBrowser.setObjectName(u"textBrowser")

        self.verticalLayout_3.addWidget(self.textBrowser)

        self.btn_start = QPushButton(self.centralwidget)
        self.btn_start.setObjectName(u"btn_start")
        self.btn_start.setGeometry(QRect(150, 600, 131, 41))
        self.btn_start.setFont(font1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 452, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.btn_fileopen.clicked.connect(MainWindow.filedialog_open)
        self.btn_start.clicked.connect(MainWindow.start)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_title.setText(QCoreApplication.translate("MainWindow", u"\uc54c\ub9ac \ubc30\uc1a1 \uc9c4\ud589 \uc0c1\ud669", None))
        self.lbl_subtitle2.setText(QCoreApplication.translate("MainWindow", u"\ud574\uc678\uc8fc\ubb38\ubc88\ud638 \uc5d1\uc140\ud30c\uc77c \uc120\ud0dd", None))
        self.btn_fileopen.setText(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c\uc5f4\uae30", None))
        self.lbl_subTitle1.setText(QCoreApplication.translate("MainWindow", u"\uc54c\ub9ac \ub85c\uadf8\uc778 \uc815\ubcf4", None))
        self.lbl_id.setText(QCoreApplication.translate("MainWindow", u"ID", None))
        self.lineEdit_id.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\uc54c\ub9ac \ub85c\uadf8\uc778 \uc544\uc774\ub514", None))
        self.lbl_pw.setText(QCoreApplication.translate("MainWindow", u"PW", None))
        self.lineEdit_pw.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\uc54c\ub9ac \ub85c\uadf8\uc778 \ud328\uc2a4\uc6cc\ub4dc", None))
        self.lbl_subTitle3.setText(QCoreApplication.translate("MainWindow", u"\uc9c4\ud589 \uc815\ubcf4", None))
        self.btn_start.setText(QCoreApplication.translate("MainWindow", u"\uc870\ud68c\ud558\uae30", None))
    # retranslateUi

