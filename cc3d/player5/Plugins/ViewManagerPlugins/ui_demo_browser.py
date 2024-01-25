# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Pete\Documents\cc3d\cc3d-player5\cc3d\player5\Plugins\ViewManagerPlugins\ui_demo_browser.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_demoDialog(object):
    def setupUi(self, demoDialog):
        demoDialog.setObjectName("demoDialog")
        demoDialog.setWindowModality(QtCore.Qt.NonModal)
        demoDialog.resize(716, 494)
        self.verticalLayout = QtWidgets.QVBoxLayout(demoDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.v_layout = QtWidgets.QVBoxLayout()
        self.v_layout.setObjectName("v_layout")
        self.searchLineEdit = QtWidgets.QLineEdit(demoDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchLineEdit.sizePolicy().hasHeightForWidth())
        self.searchLineEdit.setSizePolicy(sizePolicy)
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.v_layout.addWidget(self.searchLineEdit)
        self.demoResultsScrollArea = QtWidgets.QScrollArea(demoDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.demoResultsScrollArea.sizePolicy().hasHeightForWidth())
        self.demoResultsScrollArea.setSizePolicy(sizePolicy)
        self.demoResultsScrollArea.setWidgetResizable(True)
        self.demoResultsScrollArea.setObjectName("demoResultsScrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 694, 109))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.demoListView = QtWidgets.QListView(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.demoListView.sizePolicy().hasHeightForWidth())
        self.demoListView.setSizePolicy(sizePolicy)
        self.demoListView.setObjectName("demoListView")
        self.horizontalLayout_2.addWidget(self.demoListView)
        self.demoResultsScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.v_layout.addWidget(self.demoResultsScrollArea)
        self.line = QtWidgets.QFrame(demoDialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.v_layout.addWidget(self.line)
        self.demoTabView = QtWidgets.QTabWidget(demoDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(7)
        sizePolicy.setHeightForWidth(self.demoTabView.sizePolicy().hasHeightForWidth())
        self.demoTabView.setSizePolicy(sizePolicy)
        self.demoTabView.setObjectName("demoTabView")
        self.descriptionTab = QtWidgets.QWidget()
        self.descriptionTab.setObjectName("descriptionTab")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.descriptionTab)
        self.horizontalLayout_4.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.descriptionLabel = QtWidgets.QLabel(self.descriptionTab)
        self.descriptionLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.horizontalLayout_4.addWidget(self.descriptionLabel)
        self.demoTabView.addTab(self.descriptionTab, "")
        self.pythonPreviewTab = QtWidgets.QWidget()
        self.pythonPreviewTab.setObjectName("pythonPreviewTab")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.pythonPreviewTab)
        self.horizontalLayout_5.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pythonPreviewText = QtWidgets.QPlainTextEdit(self.pythonPreviewTab)
        self.pythonPreviewText.setObjectName("pythonPreviewText")
        self.horizontalLayout_5.addWidget(self.pythonPreviewText)
        self.demoTabView.addTab(self.pythonPreviewTab, "")
        self.xmlPreviewTab = QtWidgets.QWidget()
        self.xmlPreviewTab.setObjectName("xmlPreviewTab")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.xmlPreviewTab)
        self.horizontalLayout_6.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.xmlPreviewText = QtWidgets.QPlainTextEdit(self.xmlPreviewTab)
        self.xmlPreviewText.setObjectName("xmlPreviewText")
        self.horizontalLayout_6.addWidget(self.xmlPreviewText)
        self.demoTabView.addTab(self.xmlPreviewTab, "")
        self.v_layout.addWidget(self.demoTabView)
        self.verticalLayout.addLayout(self.v_layout)
        self.noSelectionPlaceholder = QtWidgets.QFrame(demoDialog)
        self.noSelectionPlaceholder.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.noSelectionPlaceholder.setFrameShadow(QtWidgets.QFrame.Raised)
        self.noSelectionPlaceholder.setObjectName("noSelectionPlaceholder")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.noSelectionPlaceholder)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(20, 65, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.verticalLayout.addWidget(self.noSelectionPlaceholder)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.selectedDemoNameLabel = QtWidgets.QLabel(demoDialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.selectedDemoNameLabel.setFont(font)
        self.selectedDemoNameLabel.setText("")
        self.selectedDemoNameLabel.setObjectName("selectedDemoNameLabel")
        self.horizontalLayout_3.addWidget(self.selectedDemoNameLabel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.openDemoButton = QtWidgets.QPushButton(demoDialog)
        self.openDemoButton.setObjectName("openDemoButton")
        self.horizontalLayout_3.addWidget(self.openDemoButton)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(demoDialog)
        self.demoTabView.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(demoDialog)

    def retranslateUi(self, demoDialog):
        _translate = QtCore.QCoreApplication.translate
        demoDialog.setWindowTitle(_translate("demoDialog", "Demo Browser"))
        self.searchLineEdit.setPlaceholderText(_translate("demoDialog", "Search..."))
        self.descriptionLabel.setText(_translate("demoDialog", "We\'re still working on the description for this demo. Thanks for your patience."))
        self.demoTabView.setTabText(self.demoTabView.indexOf(self.descriptionTab), _translate("demoDialog", "Description"))
        self.pythonPreviewText.setPlainText(_translate("demoDialog", "This demo has no Python Steppables file."))
        self.demoTabView.setTabText(self.demoTabView.indexOf(self.pythonPreviewTab), _translate("demoDialog", "Python"))
        self.xmlPreviewText.setPlainText(_translate("demoDialog", "This demo has no XML files."))
        self.demoTabView.setTabText(self.demoTabView.indexOf(self.xmlPreviewTab), _translate("demoDialog", "XML"))
        self.openDemoButton.setText(_translate("demoDialog", "Open this demo"))
