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
        self.mywidget.setGeometry(QtCore.QRect(0, 0, 196, 125))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mywidget.sizePolicy().hasHeightForWidth())
        self.mywidget.setSizePolicy(sizePolicy)
        self.mywidget.setMinimumSize(QtCore.QSize(196, 125))
        self.mywidget.setMaximumSize(QtCore.QSize(196, 125))
        self.mywidget.setObjectName("mywidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.mywidget)
        self.horizontalLayout.setContentsMargins(6, 6, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.content = QtWidgets.QWidget(self.mywidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.content.sizePolicy().hasHeightForWidth())
        self.content.setSizePolicy(sizePolicy)
        self.content.setStyleSheet("border-width: 1px; border-style: solid; border-color: #EAEAEA; margin: 5x 2px;")
        self.content.setObjectName("content")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.content)
        self.horizontalLayout_2.setContentsMargins(8, 5, 8, 5)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.image = QtWidgets.QLabel(self.content)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())
        self.image.setSizePolicy(sizePolicy)
        self.image.setMinimumSize(QtCore.QSize(180, 101))
        self.image.setMaximumSize(QtCore.QSize(180, 101))
        self.image.setStyleSheet("padding:0;margin:0;border:0;background-color: #ffff00;")
        self.image.setText("")
        self.image.setScaledContents(False)
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.image.setObjectName("image")
        self.verticalLayout.addWidget(self.image)
        self.info = QtWidgets.QLabel(self.content)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.info.sizePolicy().hasHeightForWidth())
        self.info.setSizePolicy(sizePolicy)
        self.info.setMinimumSize(QtCore.QSize(0, 14))
        self.info.setMaximumSize(QtCore.QSize(16777215, 14))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.info.setFont(font)
        self.info.setStyleSheet("padding:0;margin:0;border:0;")
        self.info.setAlignment(QtCore.Qt.AlignCenter)
        self.info.setObjectName("info")
        self.verticalLayout.addWidget(self.info)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout.addWidget(self.content)
        self.dontUseLabel = QtWidgets.QLabel(Form)
        self.dontUseLabel.setGeometry(QtCore.QRect(30, 160, 321, 81))
        self.dontUseLabel.setWordWrap(True)
        self.dontUseLabel.setObjectName("dontUseLabel")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.info.setText(_translate("Form", "TextLabel"))
        self.dontUseLabel.setText(_translate("Form", "<html><head/><body><p>myWidgetGröße = </p><p>Breite: Image Größe + 16 (ausgetestet)</p><p>Höhe: Image Größe + 18 + 6 (ausgetestet)</p></body></html>"))
