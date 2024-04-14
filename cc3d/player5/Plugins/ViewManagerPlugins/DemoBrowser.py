import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from cc3d.player5 import Configuration
from cc3d.player5.Plugins.ViewManagerPlugins import ui_demo_browser
import weakref
import re
import time
from pathlib import Path
from collections import Counter
from cc3d.player5.styles.SyntaxHighligher import *

MISSING_FILE_MESSAGE = "This demo doesn't have that kind of file available to preview."
DESCRIPTION_FNAME = 'README.txt'
INDEX_FILE_NAME = '.demoindex'
DELIMITER = ','


def getDemoRootPath() -> Path | None:
    """
    Credit to https://stackoverflow.com/a/74532549/16519580 user Chris.
    """

    if Configuration.check_if_setting_exists("DemosPath"):
        demosPath = Configuration.getSetting("DemosPath")
        demosPath = Path(demosPath)
        #Ensure path is not the root dir
        if len(list(demosPath.parents)) > 1 and demosPath.exists():
            return demosPath

    #Start at location of python.exe and check in every
    #parent directory for Demos until we hit the root.
    startDir = Path(__file__)

    for currPath in [startDir] + list(startDir.parents):
        demosPath = currPath.joinpath('CompuCell3D/Demos')
        if demosPath.exists():
            Configuration.setSetting("DemosPath", str(demosPath))
            return demosPath

    return None #No demos here!

def getDemoList() -> list[Path]:
    rootPath = getDemoRootPath()
    globResults = rootPath.rglob('*.cc3d')
    globResults = [p.relative_to(rootPath) for p in globResults]

    return globResults

def formatDemoName(name) -> str:
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
        (DESCRIPTION_FNAME, tokenizeText)
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
    """
    Generates each variable or method name from a line of Python code.
    It is not perfect. 
    """
    for word in line.split():
        if "." in word:
            word = re.sub('[^a-zA-Z \n\.]', '.', word) #Remove numbers and special chars
            for varName in word.split("."):
                yield varName

def tokenizeXml(line):
    """
    Generates all the key words (XML tag names and parameter names) 
    from a line of XML. 
    """
    if "!--" in line: #exclude comments, even if they have useful tags
        return
    for word in re.split('[^a-zA-Z]', line):
        yield word

def tokenizeText(line):
    for word in re.split('[^a-zA-Z]', line):
        yield word



def preIndexSearchResults():
    """
    Creates and returns a map of key words to lists of paths to demos.
    Each path is an absolute path and a string.
    """
    MAX_MATCHES = 7 #how many demos each keyword can map to
    
    searchIndex = {}

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
    return searchIndex

def checkForDemoUpdates():
    """
    Returns true if any demo has been modified or created
    since the last time we indexed them.
    Returns false if everything is up-to-date.
    """
    rootPath = getDemoRootPath()
    lastEditTime = 0
    for file in rootPath.rglob('*'):
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

def loadSearchIndex():
    rootPath = getDemoRootPath()
    indexFilePath = rootPath.joinpath(INDEX_FILE_NAME)
    searchIndex = {}

    if not indexFilePath.exists():
        return searchIndex

    with open(indexFilePath, "r") as fp:
        for line in fp.readlines():
            parsed = line.split(DELIMITER)
            if len(parsed) >= 2:
                keyWord = parsed[0]
                paths = parsed[1:]
                
                #Ensure the paths still exist, but keep them as string type
                paths = [p for p in paths if rootPath.joinpath(Path(p)).exists()]

                if paths:
                    searchIndex[keyWord] = paths

    if not searchIndex:
        print("Warning: Failed to read any demos from", INDEX_FILE_NAME, 
              "file. Maybe the files no longer exist?")

    return searchIndex



def createOrLoadSearchIndex():
    """
    Returns a map of key words to lists of paths to demos.
    """
    if not checkForDemoUpdates():
        idx = loadSearchIndex()
        if idx:
            return idx
        
    print("Please wait while we scan the demos for key words...")
    newIdx = preIndexSearchResults()
    print("Done indexing demos.")

    #Save newly indexed demos
    rootPath = getDemoRootPath()
    indexFilePath = rootPath.joinpath(INDEX_FILE_NAME)
    with open(indexFilePath, "w") as fp:
        fp.write("YOU DO NOT NEED TO MODIFY THIS FILE. CompuCell3D Player reads and writes to it on its own.\n")
        for (keyWord, paths) in newIdx.items():
            fp.write(keyWord + DELIMITER)
            fp.write(DELIMITER.join(paths))
            fp.write("\n")
    Configuration.setSetting("LastDemoEditTime", time.time())

    return newIdx



class DemoBrowser(QDialog, ui_demo_browser.Ui_demoDialog):

    def __init__(self, parent=None):
        super(DemoBrowser, self).__init__(parent)
        try:
            self.simpleTabView = weakref.ref(parent)
            self.view = None

            if sys.platform.startswith('win'):
                #Display dialog without context help - only close button exists
                self.setWindowFlags(Qt.Drawer)

            self.setupUi(self)

            if not getDemoRootPath():
                self.exitWithWarning()
                return

            self.openDemoButton.hide()
            self.demoTabView.hide()
            self.selectedDemoNameLabel.hide()
            self.noSelectionPlaceholder.show()
            
            self.searchLineEdit.textChanged.connect(self.filterByKeyWord)
            self.openDemoButton.clicked.connect(self.openDemo)

            self.pythonHighlighter = PythonHighlighter(self.pythonPreviewText.document())

            CODE_STYLES = """
                QPlainTextEdit { 
                    background-color: rgb(30, 30, 40); 
                    color: white; 
                    font-family: Courier, monospace; 
                }      
            """
            self.pythonPreviewText.setStyleSheet(CODE_STYLES)
            self.xmlPreviewText.setStyleSheet(CODE_STYLES)

            self.searchIndex = createOrLoadSearchIndex()

            self.filterByKeyWord()
            
        except Exception as ex:
            QMessageBox.warning(None, "Warning",
                        "We could not open the Demo Browser. Please restart Player, then try again.",
                        QMessageBox.Ok)
            print(ex)
            self.close()

    def exitWithWarning(self):
        QMessageBox.warning(None, "Warning",
                        "We could not find any Demos. "
                        "Please specify the path to the Demos folder in Configuration → Setup.",
                        QMessageBox.Ok)
        self.close()

    def filterByKeyWord(self):
        searchText = str(self.searchLineEdit.text())
        searchText = searchText.strip().lower()

        demoList = list(getDemoList())

        if not demoList:
            self.exitWithWarning()
            return

        if searchText:
            searchKeywords = [w for w in splitByUppercase(searchText)]
            searchKeywords.extend(searchText.split())

            keywordMatchPaths = []
            for word in searchKeywords:
                if word in self.searchIndex:
                    keywordMatchPaths.extend(self.searchIndex[word])
            
            keywordMatchPaths = [Path(x) for x in keywordMatchPaths]
            keywordMatchPaths = Counter(keywordMatchPaths)
            scores = dict(keywordMatchPaths)

            #Promote demos in the search results 
            #if a search key word partially matches one of 
            #the key words associated with that demo.
            for keyWord in self.searchIndex.keys():
                for searchWord in searchKeywords:
                    if keyWord.startswith(searchWord):
                        for demoPath in self.searchIndex[keyWord]:
                            demoPath = Path(demoPath)
                            scores[demoPath] = scores.get(demoPath, 0) + 1

            #Promote demos in the search results 
            #if their name matches a search key word
            for demoPath in demoList:
                prettyName = formatDemoName(str(demoPath.stem)).lower()
                for word in searchKeywords:
                    if word in str(demoPath).lower() or prettyName.startswith(word):
                        scores[demoPath] = scores.get(demoPath, 0) + 1
            
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
        return MISSING_FILE_MESSAGE

    def selectDemo(self, selected):
        try:
            selectedIndex = selected.indexes()[0]
            relPath = self.bestDemoPaths[selectedIndex.row()]
            absPath = getDemoRootPath().joinpath(relPath)

            self.selectedPath = absPath

            parentDir = absPath.parent

            description = self.getFilePreview(parentDir, DESCRIPTION_FNAME)
            if description == MISSING_FILE_MESSAGE:
                self.descriptionText.setPlainText(str(absPath))
            else:
                self.descriptionText.setPlainText(str(absPath) + "\n\n" + description)

            self.pythonPreviewText.setPlainText(self.getFilePreview(parentDir, "*Steppables.py"))
            self.pythonHighlighter.highlightBlock(self.pythonPreviewText.toPlainText())
            
            self.xmlPreviewText.setPlainText(self.getFilePreview(parentDir, "*.xml"))

            self.openDemoButton.show()
            self.demoTabView.show()

            #itemData is a dictionary (for some reason), and the text is at key 0
            demoName = self.demoListView.model().itemData(selectedIndex)[0]
            self.selectedDemoNameLabel.setText(demoName)
            self.selectedDemoNameLabel.show()

            self.noSelectionPlaceholder.hide()
        except KeyError:
            self.showDemoOpenError()
            print("KeyError occurred while choosing a demo.")
        except Exception as ex:
            self.showDemoOpenError()
            print("Error: Could not select that demo. Exception:\n", ex)

    def showDemoOpenError(self):
        QMessageBox.warning(None, "Warning",
                    "We could not select that demo because of an error. " +
                    "Please close the Demo Browser, then try again. " +
                    "If the issue persists, please delete the .demoindex " +
                    "file inside of your demos folder. ",
                    QMessageBox.Ok)

    def openDemo(self):
        #Sanity check. 
        #The button to trigger this should be invisible anyway.
        if not self.selectedPath or not self.selectedPath.exists():
            self.showDemoOpenError()
            print("Error: Could not open the demo with path", self.selectedPath)
            return
        
        if self.simpleTabView():
            self.simpleTabView().openSim(str(self.selectedPath))
            self.close()
        