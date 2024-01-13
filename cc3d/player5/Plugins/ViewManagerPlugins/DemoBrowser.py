import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from cc3d.player5.Plugins.ViewManagerPlugins import ui_demo_browser
import weakref
from pathlib import Path
from pathlib import Path

from cc3d.player5.styles.StyleManager import subscribeToStylesheet

            
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
        
        self.searchLineEdit.textChanged.connect(self.filterByKeyWord)

        self.filterByKeyWord() #TEMP

    def filterByKeyWord(self):
        searchText = str(self.searchLineEdit.text())
        # if not searchText:
        #     searchText = "tu" #TEMP
        searchText = searchText.strip().lower()
        print("searchText",searchText)

        rootPath = Path("C:\\Users\\Pete\\Documents\\cc3d\\CompuCell3D\\CompuCell3D\\core\\Demos")  

        demoList = list(getDemoList())

        if searchText:
            scores = [0] * len(demoList)
            for i in range(len(scores)):
                prettyName = formatDemoName(str(demoList[i].stem)).lower()
                for word in searchText.split():
                    if word in str(demoList[i]).lower() or word in prettyName:
                        scores[i] += 2

                if i < 2:
                    fullPath = rootPath.joinpath(demoList[i])
                    scores[i] += scanFileForKeyWords(searchText, fullPath)
                    print("Score",scores[i],"+++++++++++++++++++++++++++++++++++++++")
                
            relativePaths = [p for _, p in sorted(zip(scores, demoList), reverse=True)]
            self.absPaths = [rootPath.joinpath(p) for _, p in sorted(zip(scores, demoList), reverse=True)]
        else:
            #Default to alphabetical
            demoNames = [x.stem for x in demoList]
            
            relativePaths = [p for _, p in sorted(zip(demoNames, demoList))]
            self.absPaths = [rootPath.joinpath(p) for _, p in sorted(zip(demoNames, demoList))]

        print(relativePaths[:3], "------------------------------------------------------")
        
        model = QStringListModel()

        model.setStringList([formatDemoName(item.stem) for item in relativePaths])

        self.demoListView.setModel(model)
        self.model = model
        self.demoListView.selectionModel().selectionChanged.connect(self.selectDemo)

    
    def selectDemo(self, selected):
        treeIndex = selected.indexes()[0]
        demoPath = self.absPaths[treeIndex.row()]

        print("Clicked on ",demoPath)
        