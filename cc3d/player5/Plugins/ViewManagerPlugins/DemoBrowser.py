import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from cc3d.player5.Plugins.ViewManagerPlugins import ui_demo_browser
import weakref
import re
from pathlib import Path
import time

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


def tokenizeAllFiles(demoAbsPath):
    methods = (
        ('*.py', tokenizePython), 
        # ('*.xml', tokenizeXml)
    )
    for fileType, tokenizer in methods:
        for filePath in demoAbsPath.parent.rglob(fileType):
            with open(filePath) as fp:
                for line in fp.readlines():
                    for word in tokenizer(line):
                        if word:
                            yield word.lower()

def tokenizePython(line):
    for word in line.split():
        if "." in word:
            word = re.sub('[^a-zA-Z \n\.]', '', word) #Remove numbers and special chars
            for varName in word.split("."):
                yield varName

def tokenizeXml(line):
    for word in re.split('[^a-zA-Z]', line):
        # word = re.sub('[^a-zA-Z0-9 \n\.]', '', word) #Remove special chars
        yield word


searchIndex = {} #maps key words to lists of paths to demos

def preIndexSearchResults():
    allFreq = {}

    rootPath = Path("C:\\Users\\Pete\\Documents\\cc3d\\CompuCell3D\\CompuCell3D\\core\\Demos")  
    demoList = list(getDemoList())

    for demoPath in demoList:
        fullPath = rootPath.joinpath(demoPath)

        for word in tokenizeAllFiles(fullPath):
            if word not in allFreq:
                allFreq[word] = 1
            else:
                allFreq[word] += 1
                
    for demoPath in demoList:
        fullPath = rootPath.joinpath(demoPath)
        
        freqByFile = {}
        for word in tokenizeAllFiles(fullPath):
            if word not in freqByFile:
                freqByFile[word] = 1
            else:
                freqByFile[word] += 1
        
        #Find how frequently each word in `freqByFile` occurred across all files (allFreq).
        keywords = [(word, allFreq[word]) for word in freqByFile.keys()]
        keywords = sorted(keywords, key=lambda x: x[1])
        keywords = [row[0] for row in keywords]
                
        # keywords = list(freqByFile.keys())

        searchIndex[fullPath] = keywords

for i in range(10):
    start_time = time.time()
    preIndexSearchResults()
    print("--- %s seconds ---" % (time.time() - start_time))

k = 0
for entry in searchIndex.keys():
    # print(entry, searchIndex[entry][:10])
    print(entry, searchIndex[entry])
    print("----------------------------------------------\n\n")
    k += 1
    if k > 13:
        break
import sys




import sys
from types import ModuleType, FunctionType
from gc import get_referents

# Custom objects know their class.
# Function objects seem to know way too much, including modules.
# Exclude modules as well.
BLACKLIST = type, ModuleType, FunctionType


def getsize(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size
print("SIZEOF: ",getsize(searchIndex)) #139342

exit(0)








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

                fullPath = rootPath.joinpath(demoList[i])
                globResult = [fullPath]
                for fileType in ('*.py', '*.xml'):
                    globResult.extend(fullPath.parent.rglob(fileType))

                for filePath in globResult:
                    scores[i] += scanFileForKeyWords(searchText, filePath)
                
                print("Score",scores[i],"+++++++++++++++++++++++++++++++++++++++")

                print(fullPath.joinpath("Simulation`"))
                
            relativePaths = [p for _, p in sorted(zip(scores, demoList), reverse=True)]
            self.absPaths = [rootPath.joinpath(p) for _, p in sorted(zip(scores, demoList), reverse=True)]
        else:
            #Default to alphabetical
            demoNames = [x.stem for x in demoList]
            
            relativePaths = [p for _, p in sorted(zip(demoNames, demoList))]
            self.absPaths = [rootPath.joinpath(p) for _, p in sorted(zip(demoNames, demoList))]

        #Render the filtered results
        model = QStringListModel()
        model.setStringList([formatDemoName(item.stem) for item in relativePaths])

        self.demoListView.setModel(model)
        self.model = model
        self.demoListView.selectionModel().selectionChanged.connect(self.selectDemo)

    
    def selectDemo(self, selected):
        treeIndex = selected.indexes()[0]
        demoPath = self.absPaths[treeIndex.row()]

        print("Clicked on ",demoPath)
        