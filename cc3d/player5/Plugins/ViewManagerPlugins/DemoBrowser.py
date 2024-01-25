import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from cc3d.player5 import Configuration
from cc3d.player5.Plugins.ViewManagerPlugins import ui_demo_browser
import weakref
import re
from pathlib import Path
from collections import Counter
from cc3d.player5.styles.SyntaxHighligher import *


def getDemoRootPath():
    return Path(r"C:\Users\Pete\Documents\cc3d\CompuCell3D\CompuCell3D\core\Demos")
    # out = Path(__file__).joinpath('Demos')
    # print("DEMO ROOT PATH:",out)
    # exit(0)
    return out

def getDemoList():
    rootPath = getDemoRootPath()
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


def splitByUppercase(word):
    #Extract individual words from camel/pascal case tokens.
    #Example: "lambdaVolume" splits into "lambda" and "Volume".
    start = 0
    i = 1
    while i <= len(word):
        if word[i-1].islower() and (i == len(word) or word[i].isupper()):
            if i - start < len(word):
                yield word[start:i]
            start = i
        i += 1


def tokenizeAllFiles(demoAbsPath):
    methods = (
        ('*.py', tokenizePython), 
        ('*.xml', tokenizeXml),
    )
    for fileType, tokenizer in methods:
        for filePath in demoAbsPath.parent.rglob(fileType):
            with open(filePath, "r") as fp:
                for line in fp.readlines():
                    for word in tokenizer(line):
                        if word:
                            yield word.lower()
                            for subword in splitByUppercase(word):
                                yield subword.lower()


def tokenizePython(line):
    for word in line.split():
        if "." in word:
            word = re.sub('[^a-zA-Z \n\.]', '.', word) #Remove numbers and special chars
            for varName in word.split("."):
                yield varName

def tokenizeXml(line):
    if "!--" in line: #exclude comments, even if they have useful tags
        return
    for word in re.split('[^a-zA-Z]', line):
        yield word


searchIndex = {} #maps key words to lists of paths to demos

def preIndexSearchResults():
    MAX_MATCHES = 7 #how many demos each keyword can map to

    rootPath = getDemoRootPath()  
    demoList = list(getDemoList())
                
    for demoPath in demoList:
        fullPath = rootPath.joinpath(demoPath)
        
        wordsSeen = set()
        for word in tokenizeAllFiles(fullPath):
            if word not in wordsSeen:
                smallPath = str(demoPath) #conserve memory by converting object to str
                if word in searchIndex and len(searchIndex[word]) < MAX_MATCHES:
                    searchIndex[word].append(smallPath)
                else:
                    searchIndex[word] = [smallPath]
                wordsSeen.add(word)


def checkForDemoUpdates():
    rootPath = getDemoRootPath()
    lastEditTime = 0
    for file in rootPath.rglob():
        if file.lstat().st_mtime > lastEditTime:
            lastEditTime = file.lstat().st_mtime
    
    modified = False
    if Configuration.check_if_setting_exists("LastDemoEditTime"):
        if lastEditTime > Configuration.getSetting("LastDemoEditTime"):
            modified = True
    else:
        modified = True
    
    if modified:
        Configuration.setSetting("LastDemoEditTime", lastEditTime)
    
    return modified


preIndexSearchResults()
print("Done indexing demos.")




class DemoBrowser(QDialog, ui_demo_browser.Ui_demoDialog):

    def __init__(self, parent=None):
        super(DemoBrowser, self).__init__(parent)
        self.simpleTabView = weakref.ref(parent)
        self.view = None

        if sys.platform.startswith('win'):
            #Display dialog without context help - only close button exists
            self.setWindowFlags(Qt.Drawer)

        self.projectPath = ""

        self.setupUi(self)

        self.openDemoButton.hide()
        self.demoTabView.hide()
        self.selectedDemoNameLabel.hide()
        self.noSelectionPlaceholder.show()
        
        self.searchLineEdit.textChanged.connect(self.filterByKeyWord)
        self.openDemoButton.clicked.connect(self.openDemo)

        self.pythonHighlighter = PythonHighlighter(self.plainTextEdit.document())

        self.descriptionLabel.setStyleSheet("QLabel { background-color: rgb(30, 30, 40); }")
        self.plainTextEdit.setStyleSheet("QPlainTextEdit { background-color: rgb(30, 30, 40); font-family: Courier; }")
        self.xmlPreviewLabel.setStyleSheet("QLabel { background-color: rgb(30, 30, 40); font-family: Courier; }")

        self.filterByKeyWord()

    def filterByKeyWord(self):
        searchText = str(self.searchLineEdit.text())
        # if not searchText:
        #     searchText = "chemotaxis" #TEMP
        searchText = searchText.strip().lower()

        demoList = list(getDemoList())

        if searchText:
            searchKeywords = [w for w in splitByUppercase(searchText)]
            searchKeywords.extend(searchText.split())

            keywordMatchPaths = []
            for word in searchKeywords:
                if word in searchIndex:
                    keywordMatchPaths.extend(searchIndex[word])
            
            keywordMatchPaths = [Path(x) for x in keywordMatchPaths]
            keywordMatchPaths = Counter(keywordMatchPaths)
            scores = dict(keywordMatchPaths)

            for demoPath in demoList:
                prettyName = formatDemoName(str(demoPath.stem)).lower()
                for word in searchKeywords:
                    if word in str(demoPath).lower() or prettyName.startswith(word):
                        if demoPath in scores:
                            scores[demoPath] += 1
                        else:
                            scores[demoPath] = 1
            
            self.bestDemoPaths = sorted(scores, key=scores.get, reverse=True)
        else:
            #Default to alphabetical
            demoNames = [x.stem for x in demoList]
            self.bestDemoPaths = [p for _, p in sorted(zip(demoNames, demoList))]
            

        #Render the filtered results
        model = QStringListModel()
        bestDemoNames = [formatDemoName(p.stem) for p in self.bestDemoPaths]
        model.setStringList(bestDemoNames)

        self.demoListView.setModel(model)
        self.demoListView.selectionModel().selectionChanged.connect(self.selectDemo)

    def getFilePreview(self, parentDir, globExtension) -> str:
        MAX_PREVIEW_BYTES = 16000
        for filePath in parentDir.rglob(globExtension):
            with open(filePath, "r") as fp:
                #Only use first glob result
                return fp.read(MAX_PREVIEW_BYTES)
        #Else...
        return "This demo doesn't have that kind of file available to preview."

    def selectDemo(self, selected):
        try:
            selectedIndex = selected.indexes()[0]
            relPath = self.bestDemoPaths[selectedIndex.row()]
            absPath = getDemoRootPath().joinpath(relPath)

            self.selectedPath = absPath

            parentDir = absPath.parent

            self.plainTextEdit.setPlainText(self.getFilePreview(parentDir, "*Steppables.py"))
            self.pythonHighlighter.highlightBlock(self.plainTextEdit.toPlainText())
            
            self.xmlPreviewLabel.setText(self.getFilePreview(parentDir, "*.xml"))

            self.openDemoButton.show()
            self.demoTabView.show()

            #itemData is a dictionary (for some reason), and the text is at key 0
            demoName = self.demoListView.model().itemData(selectedIndex)[0]
            self.selectedDemoNameLabel.setText(demoName)
            self.selectedDemoNameLabel.show()

            self.noSelectionPlaceholder.hide()
        except KeyError:
            print("Error: Could not select that demo")

    def openDemo(self):
        #Sanity check. 
        #The button to trigger this should be invisible anyway.
        if not self.selectedPath or not self.selectedPath.exists():
            print("Error: Could not open the demo with path", self.selectedPath)
            return
        
        if self.simpleTabView():
            self.simpleTabView().openSim(str(self.selectedPath))
            self.close()
        