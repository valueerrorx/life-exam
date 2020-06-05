# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MyCustomWidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.mywidget = QtWidgets.QWidget(Form)
        self.mywidget.setGeometry(QtCore.QRect(70, 20, 182, 116))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mywidget.sizePolicy().hasHeightForWidth())
        self.mywidget.setSizePolicy(sizePolicy)
        self.mywidget.setStyleSheet("border-width: 1px; border-style: solid; border-color: #AAA; margin-top: 4px; margin-left:4px;")
        self.mywidget.setObjectName("mywidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.mywidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.image = QtWidgets.QLabel(self.mywidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())
        self.image.setSizePolicy(sizePolicy)
        self.image.setMinimumSize(QtCore.QSize(180, 100))
        self.image.setMaximumSize(QtCore.QSize(180, 100))
        self.image.setStyleSheet("padding:0;margin:0;border:0;")
        self.image.setText("")
        self.image.setPixmap(QtGui.QPixmap("../../../../../../../../../LIFE-Dev/life-exam/pixmaps/original/Test.jpg"))
        self.image.setScaledContents(False)
        self.image.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.image.setObjectName("image")
        self.verticalLayout.addWidget(self.image)
        self.info = QtWidgets.QLabel(self.mywidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.info.sizePolicy().hasHeightForWidth())
        self.info.setSizePolicy(sizePolicy)
        self.info.setMinimumSize(QtCore.QSize(180, 14))
        self.info.setMaximumSize(QtCore.QSize(180, 14))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.info.setFont(font)
        self.info.setStyleSheet("padding:0;margin:0;border:0;")
        self.info.setAlignment(QtCore.Qt.AlignCenter)
        self.info.setObjectName("info")
        self.verticalLayout.addWidget(self.info)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(100, 170, 221, 18))
        self.label.setObjectName("label")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.info.setText(_translate("Form", "TextLabel"))
        self.label.setText(_translate("Form", "Margin ist per Css top und left"))
