import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from cc3d.player5.Plugins.ViewManagerPlugins import ui_demo_browser
import weakref
import re
from pathlib import Path
import time
from collections import Counter

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
    allFreq = {}

    rootPath = Path("C:\\Users\\Pete\\Documents\\cc3d\\CompuCell3D\\CompuCell3D\\core\\Demos")  
    demoList = list(getDemoList())
                
    for demoPath in demoList:
        fullPath = rootPath.joinpath(demoPath)
        
        # freqByFile = {}
        # for word in tokenizeAllFiles(fullPath):
        #     if word not in freqByFile:
        #         freqByFile[word] = 1
        #     else:
        #         freqByFile[word] += 1
            
        # for (word, freq) in freqByFile:
        #     if word not in allFreq:
        #         allFreq[word] = 1
        #     else:
        #         allFreq[word] += 1
        
        #Find how frequently each word in `freqByFile` occurred across all files (allFreq).
        # keywords = [(word, allFreq[word]) for word in freqByFile.keys()]
        # keywords = sorted(keywords, key=lambda x: x[1])
        # keywords = [row[0] for row in keywords]
                
        # keywords = list(freqByFile.keys())

        wordsSeen = set()

        for word in tokenizeAllFiles(fullPath):
            if word not in wordsSeen:
                smallPath = str(demoPath) #conserve memory by converting object to str
                if word in searchIndex and len(searchIndex[word]) < 5:
                    searchIndex[word].append(smallPath)
                else:
                    searchIndex[word] = [smallPath]
                wordsSeen.add(word)
            

# for i in range(1):
#     start_time = time.time()
#     preIndexSearchResults()
#     print("--- %s seconds ---" % (time.time() - start_time))

preIndexSearchResults()
print("Done indexing demos.")

# for keyword in sorted(list(searchIndex.keys())):
#     print(keyword)




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









class DemoBrowser(QDialog, ui_demo_browser.Ui_demoDialog):

    def __init__(self, parent=None):
        super(DemoBrowser, self).__init__(parent)
        self.stv = weakref.ref(parent)
        self.model = None
        self.view = None

        print("init")
        if sys.platform.startswith('win'):
            #Display dialog without context help - only close button exists
            self.setWindowFlags(Qt.Drawer)

        self.projectPath = ""

        subscribeToStylesheet(self)
        self.setupUi(self)
        
        self.searchLineEdit.textChanged.connect(self.filterByKeyWord)

        print("Registering")
        self.filterByKeyWord() #TEMP
        print("Registered")

    def filterByKeyWord(self):
        searchText = str(self.searchLineEdit.text())
        if not searchText:
            searchText = "cartesian" #TEMP
        searchText = searchText.strip().lower()
        print("searchText",searchText)

        rootPath = Path("C:\\Users\\Pete\\Documents\\cc3d\\CompuCell3D\\CompuCell3D\\core\\Demos")  

        demoList = list(getDemoList())

        if searchText:
            searchKeywords = [w for w in splitByUppercase(searchText)]
            searchKeywords.extend(searchText.split())
            #list(dict.fromkeys(mylist))
            print("searchKeywords ------>",searchKeywords)

            goodPaths = []
            for word in searchKeywords:
                if word in searchIndex:
                    print("found via searchIndex:",searchIndex[word])
                    goodPaths.extend(searchIndex[word])
            print('goodPaths',goodPaths)
            goodPaths = Counter(goodPaths)
            scores = dict(goodPaths)

            for demoName in demoList:
                prettyName = formatDemoName(str(demoName.stem)).lower()
                for word in searchKeywords:
                    if word in str(demoName).lower() or prettyName.startswith(word):
                        if demoName in scores:
                            scores[demoName] += 1
                        else:
                            scores[demoName] = 1
                
            print("scores",scores)
        else:
            #Default to alphabetical
            demoNames = [x.stem for x in demoList]
            
            #FIXME
            relativePaths = [p for _, p in sorted(zip(demoNames, demoList))]
            self.absPaths = [rootPath.joinpath(p) for _, p in sorted(zip(demoNames, demoList))]

        #Render the filtered results
        model = QStringListModel()
        # model.setStringList([formatDemoName(item.stem) for item in relativePaths])
        stringModel = [formatDemoName(Path(key).stem) for key, value in scores.items() if value > 0]
        print(stringModel)
        model.setStringList(stringModel)

        self.demoListView.setModel(model)
        self.model = model
        self.demoListView.selectionModel().selectionChanged.connect(self.selectDemo)

    
    def selectDemo(self, selected):
        treeIndex = selected.indexes()[0]
        demoPath = self.absPaths[treeIndex.row()]

        print("Clicked on ",demoPath)
        