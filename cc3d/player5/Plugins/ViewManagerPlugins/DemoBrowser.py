import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from cc3d.player5.Plugins.ViewManagerPlugins import ui_demo_browser
import weakref
import re
from pathlib import Path
from collections import Counter

from cc3d.player5.styles.StyleManager import subscribeToStylesheet


def getDemoRootPath():
    return Path("C:\\Users\\Pete\\Documents\\cc3d\\CompuCell3D\\CompuCell3D\\core\\Demos")

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
            with open(filePath) as fp:
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
            

preIndexSearchResults()
print("Done indexing demos.")




class DemoBrowser(QDialog, ui_demo_browser.Ui_demoDialog):

    def __init__(self, parent=None):
        super(DemoBrowser, self).__init__(parent)
        self.simpleTabView = weakref.ref(parent)
        self.model = None
        self.view = None

        if sys.platform.startswith('win'):
            #Display dialog without context help - only close button exists
            self.setWindowFlags(Qt.Drawer)

        self.projectPath = ""

        subscribeToStylesheet(self)
        self.setupUi(self)
        
        self.searchLineEdit.textChanged.connect(self.filterByKeyWord)

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
        self.model = model
        self.demoListView.selectionModel().selectionChanged.connect(self.selectDemo)

    
    def selectDemo(self, selected):
        try:
            treeIndex = selected.indexes()[0]
            relPath = self.bestDemoPaths[treeIndex.row()]
            absPath = getDemoRootPath().joinpath(relPath)
            absPath = str(absPath)
            
            if self.simpleTabView():
                self.simpleTabView().openSim(absPath)
                self.close()
        except KeyError:
            print("Error: Could not select that demo")