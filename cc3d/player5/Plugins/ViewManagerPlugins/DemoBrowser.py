from queue import Queue
import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from cc3d.player5.Plugins.ViewManagerPlugins import ui_demo_browser
from cc3d.player5.Plugins.ViewManagerPlugins.QJsonBrowser import QJsonModel, QJsonTreeView
import weakref
import cc3d
from cc3d import CompuCellSetup
from typing import Optional
from pathlib import Path
import shutil
import glob
from pathlib import Path

from cc3d.player5.styles.StyleManager import subscribeToStylesheet

# class CustomItem:
#     def __init__(self, demoPath):
#         self.displayText = formatDemoName(demoPath.stem)
#         rootPath = Path("C:\\Users\\Pete\\Documents\\cc3d\\CompuCell3D\\CompuCell3D\\core\\Demos") #FIXME/TODO/TEMP
#         self.path = rootPath.joinpath(demoPath)

def editDistance(str1, str2):
    m, n = len(str1), len(str2)
    m = min(m, n)
    n = m
    dp = [[0] * (n + 1) for _ in range(m + 1)]  
    for i in range(m + 1):  
        for j in range(n + 1):  
            if i == 0:  
                dp[i][j] = j  
            elif j == 0:  
                dp[i][j] = i  
            elif str1[i - 1] == str2[j - 1]:  
                dp[i][j] = dp[i - 1][j - 1]  
            else:  
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])  
    
    return dp[m][n]

# def getDemoList():
#     rootPath = Path("C:\\Users\\Pete\\Documents\\cc3d\\CompuCell3D\\CompuCell3D\\core\\Demos") #FIXME/TODO/TEMP
    # demoPath = Path(__file__).parents[0]
    
    # from queue import Queue
    # q = Queue()
    # q.put(rootPath)

    # while not q.empty():
    #     demoPath = q.get()
    #     for subPath in [f for f in demoPath.iterdir() if f.is_dir()]:
    #         q.put(subPath)
    #     print("demoPath",demoPath)

    #Method 2
    # for p in rootPath.rglob('*.cc3d'):
    #     print(p.name, p.relative_to(rootPath))

def getDemoTree():
    rootPath = Path("C:\\Users\\Pete\\Documents\\cc3d\\CompuCell3D\\CompuCell3D\\core\\Demos") #FIXME/TODO/TEMP
    
    from queue import Queue
    q = Queue()
    q.put(rootPath)

    while not q.empty():
        demoPath = q.get()
        for subPath in [f for f in demoPath.iterdir() if f.is_dir()]:
            q.put(subPath)
        # print("demoPath",demoPath)
        for cc3dFile in subPath.rglob('*.cc3d'):
            yield cc3dFile
            
            
def getDemoList():
    rootPath = Path("C:\\Users\\Pete\\Documents\\cc3d\\CompuCell3D\\CompuCell3D\\core\\Demos") #FIXME/TODO/TEMP
    globResults = rootPath.rglob('*.cc3d')
    globResults = [p.relative_to(rootPath) for p in globResults]

    return globResults

def formatDemoName(name):
    outStr = name[0].upper()
    prev = 'A'
    i = 1
    while i < len(name):
        c = name[i]
        if (c == '_' or c == '-') and prev != ' ':
            c = ' '
        elif c.islower() and prev == ' ':
            c = c.upper()
        elif c.isupper():
            if prev.islower() or (i+1 < len(name) and name[i+1].islower()):
                outStr += ' '
        
        outStr += c
        prev = c
        i += 1
    return outStr

def scanFileForKeyWords(searchTerm, filePath):
    score = 0
    print("filePath",filePath)
    with open(filePath) as fp:
        for ln in fp.readlines():
            ln = ln.lower()
            if searchTerm in ln:
                score += 1

    return score


class DemoBrowser(QDialog, ui_demo_browser.Ui_demoDialog):

    def __init__(self, parent=None):
        super(DemoBrowser, self).__init__(parent)
        self.stv = weakref.ref(parent)
        self.model = None
        self.view = None

        if sys.platform.startswith('win'):
            # dialogs without context help - only close button exists
            self.setWindowFlags(Qt.Drawer)

        self.projectPath = ""

        subscribeToStylesheet(self)
        self.setupUi(self)
        
        self.demoTreeView.setAnimated(False)
        self.demoTreeView.setIndentation(20)
        self.demoTreeView.setSortingEnabled(False)

        self.searchLineEdit.textChanged.connect(self.filterByKeyWord)

        self.filterByKeyWord() #TEMP
        # self.populateDemoList() #TEMP

        self.updateUi()

    def filterByKeyWord(self):
        searchText = str(self.searchLineEdit.text())
        if not searchText:
            # self.populateDemoList()
            # return
            searchText = "tu" #TEMP
        searchText = searchText.strip().lower()
        print("searchText",searchText)

        rootPath = Path("C:\\Users\\Pete\\Documents\\cc3d\\CompuCell3D\\CompuCell3D\\core\\Demos")  

        demoList = list(getDemoList())
        scores = [0] * len(demoList)
        for i in range(len(scores)):
            # scores[i] = editDistance(searchText, demoList[i].stem.lower())

            # if searchText in str(demoList[i]).lower():
            #     scores[i] += 3
            if i < 2:
                fullPath = rootPath.joinpath(demoList[i])
                scores[i] += scanFileForKeyWords(searchText, fullPath)
                # print("Score",scores[i],"+++++++++++++++++++++++++++++++++++++++")


        relativePaths = [p for _, p in sorted(zip(scores, demoList), reverse=True)]
        self.absPaths = [rootPath.joinpath(p) for _, p in sorted(zip(scores, demoList), reverse=True)]
        
        print(relativePaths[:3], "------------------------------------------------------")
        
        self.demoResultsScrollArea.hide()
        self.demoTreeView.show()

        model = QStringListModel()

        model.setStringList([formatDemoName(item.stem) for item in relativePaths])

        self.demoTreeView.setModel(model)
        self.model = model
        self.demoTreeView.selectionModel().selectionChanged.connect(self.selectDemo)


    def updateUi(self):
        """

        :return:
        """
        # self.clear_screenshots_PB.clicked.connect(self.clear_screenshots)

    def populateDemoList(self):
        self.demoResultsScrollArea.hide()
        self.demoTreeView.show()

        # self.model = QFileSystemModel()
        # rootPathStr = "C:\\CompuCell3D\\Demos" #FIXME/TODO/TEMP
        # self.model.setRootPath(rootPathStr)
        # self.demoTreeView.setModel(self.model)

        
        # tree_data = [
        # ("Alice", [
        #     ("Keys", []),
        # ("Purse", [
        #     ("Cellphone", [])
        #     ])
        #     ]),
        # ("Bob", [
        #     ("Wallet", [
        #     ("Credit card", []),
        #     ("Money", [])
        #         ])
        #     ])
        # ]
        # self.model = QStandardItemModel()
        # # self.demoTreeView.addTreeItems(model, tree_data)
        # self.addTreeItems(self.model, tree_data)
        # self.demoTreeView.setModel(self.model)

        
        model = QStandardItemModel()

        for demoPath in getDemoList():
            item = QStandardItem(demoPath.name)
            model.appendRow(item)

        self.demoTreeView.setModel(model)
        self.model = model
        self.demoTreeView.selectionModel().selectionChanged.connect(self.selectDemo)

    
    # def addTreeItems(self, parent, elements):
    
    #     for text, children in elements:
    #         item = QStandardItem(text)
    #         parent.appendRow(item)
    #         if children:
    #             self.addTreeItems(item, children)
    
    def selectDemo(self, selected):
    
        # Find the top-level item in the tree.
        treeIndex = selected.indexes()[0]

        print("Clicked on ",self.absPaths[treeIndex.row()])
        

    # def buttonBoxClicked(self, btn):
    #     """
    #     handling of primary buttons (Cancel/OK) at the bottom of the dialog
    #     """

    #     if str(btn.text()) == 'Apply':
    #         if self.outputImagesCheckBox.isChecked() and (
    #                 self.saveImageSpinBox.value() < self.updateScreenSpinBox.value()):
    #             save_img_str = str(self.saveImageSpinBox.value())
    #             QMessageBox.warning(None, "WARN",
    #                                 "If saving images, you need to Update screen at least "
    #                                 "as frequently as Save image (e.g. Update screen = " + save_img_str + ')',
    #                                 QMessageBox.Ok)
    #             return
    #     self.updatePreferences()
        
        
    def filterDemos(self):
        self.demoResultsScrollArea.show()
        self.demoTreeView.hide()