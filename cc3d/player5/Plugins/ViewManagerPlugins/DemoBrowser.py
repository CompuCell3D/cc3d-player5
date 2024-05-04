import sys
from typing import Optional
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
DESCRIPTION_FNAME = "README.txt"
INDEX_FILE_NAME = ".demoindex"
DELIMITER = ","




class CreateIndexWorker(QThread):
    finished = pyqtSignal(dict)
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.searchIndex = None
        self.modified = True
        self.demo_root_path =  None

    def run(self):
        # Potentially long-ish running task
        self.searchIndex = createOrLoadSearchIndex(self.modified, self.demo_root_path)
        # Emit finished signal when task is done
        self.finished.emit(self.searchIndex)


class DemoBrowser(QDialog, ui_demo_browser.Ui_demoDialog):
    def on_create_index_finished(self, search_index:dict):
        self.searchIndex = search_index
        self.wait_popup.close()

    def __init__(self, parent=None):
        super(DemoBrowser, self).__init__(parent)
        # limiting number of times we call getDemoRootPath to just a single instance
        self.searchIndex = None
        self.demo_root_path = getDemoRootPath()


        self.modified = checkForDemoUpdates(demo_root_path=self.demo_root_path)
        self.wait_popup = CreateIndexWaitPopup(parent=self)


        try:
            # modified and demo_root_path access sqllite so to avid issues related to cross-thread access to the db
            # we are prefetching them here

            if self.demo_root_path is None:
                raise RuntimeError(f"self.demo_root_path is None. Exiting")

            create_index_worker = CreateIndexWorker()
            create_index_worker.modified = self.modified
            create_index_worker.demo_root_path = self.demo_root_path

            create_index_worker.finished.connect(self.on_create_index_finished)
            create_index_worker.start()
            # we need to execute the dialog after we start thread - otherwise the popup dialog may not
            # display properly. We also need to wait here before index creation finishes
            self.wait_popup.exec_()


            self.simpleTabView = weakref.ref(parent)
            self.view = None

            if sys.platform.startswith("win"):
                # Display dialog without context help - only close button exists
                self.setWindowFlags(Qt.Drawer)
                self.setupUi(self)
            if not self.demo_root_path:
                self.exitWithWarning()
                return

            self.openDemoButton.hide()
            self.demoTabView.hide()
            self.selectedDemoNameLabel.hide()
            self.noSelectionPlaceholder.show()
            # self.searchIndex = createOrLoadSearchIndex()

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
            self.filterByKeyWord()

        except Exception as ex:
            QMessageBox.warning(
                None,
                "Warning",
                "We could not open the Demo Browser. Please restart Player, then try again.",
                QMessageBox.Ok,
            )
            print(ex)
            QTimer.singleShot(10, self.close)
            # self.close()
        finally:
            pass

    def exitWithWarning(self):
        QMessageBox.warning(
            None,
            "Warning",
            "We could not find any Demos. " "Please specify the path to the Demos folder in Configuration → Setup.",
            QMessageBox.Ok,
        )
        self.close()

    def filterByKeyWord(self):
        search_text = str(self.searchLineEdit.text())
        search_text = search_text.strip().lower()

        demo_list = list(getDemoList(demo_root_path=self.demo_root_path))

        if not demo_list:
            self.exitWithWarning()
            return

        if search_text:
            search_keywords = [w for w in splitByUppercase(search_text)]
            search_keywords.extend(search_text.split())

            keyword_match_paths = []
            for word in search_keywords:
                if word in self.searchIndex:
                    keyword_match_paths.extend(self.searchIndex[word])

            keyword_match_paths = [Path(x) for x in keyword_match_paths]
            keyword_match_paths = Counter(keyword_match_paths)
            scores = dict(keyword_match_paths)

            # Promote demos in the search results
            # if a search key word partially matches one of
            # the keywords associated with that demo.
            for keyWord in self.searchIndex.keys():
                for searchWord in search_keywords:
                    if keyWord.startswith(searchWord):
                        for demoPath in self.searchIndex[keyWord]:
                            demoPath = Path(demoPath)
                            scores[demoPath] = scores.get(demoPath, 0) + 1

            # Promote demos in the search results
            # if their name matches a search key word
            for demoPath in demo_list:
                prettyName = formatDemoName(str(demoPath.stem)).lower()
                for word in search_keywords:
                    if word in str(demoPath).lower() or prettyName.startswith(word):
                        scores[demoPath] = scores.get(demoPath, 0) + 1

            self.bestDemoPaths = sorted(scores, key=scores.get, reverse=True)
        else:
            # Default to alphabetical
            demoNames = [x.stem for x in demo_list]
            self.bestDemoPaths = [p for _, p in sorted(zip(demoNames, demo_list))]

        # Render the filtered results
        model = QStringListModel()
        bestDemoNames = [formatDemoName(p.stem) for p in self.bestDemoPaths]

        model.setStringList(bestDemoNames)
        self.demoListView.setModel(model)
        self.demoListView.selectionModel().selectionChanged.connect(self.selectDemo)

    def getFilePreview(self, parentDir, globExtension) -> str:
        MAX_PREVIEW_BYTES = 16000
        for filePath in parentDir.rglob(globExtension):
            with open(filePath, "r") as fp:
                # Only use first glob result
                return fp.read(MAX_PREVIEW_BYTES)
        # Else...
        return MISSING_FILE_MESSAGE

    def selectDemo(self, selected):
        try:
            selectedIndex = selected.indexes()[0]
            relPath = self.bestDemoPaths[selectedIndex.row()]
            absPath = self.demo_root_path.joinpath(relPath)

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

            # itemData is a dictionary (for some reason), and the text is at key 0
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
        QMessageBox.warning(
            None,
            "Warning",
            "We could not select that demo because of an error. "
            + "Please close the Demo Browser, then try again. "
            + "If the issue persists, please delete the .demoindex "
            + "file inside of your demos folder. ",
            QMessageBox.Ok,
        )

    def openDemo(self):
        # Sanity check.
        # The button to trigger this should be invisible anyway.
        if not self.selectedPath or not self.selectedPath.exists():
            self.showDemoOpenError()
            print("Error: Could not open the demo with path", self.selectedPath)
            return

        if self.simpleTabView():
            self.simpleTabView().openSim(str(self.selectedPath))
            self.close()





class CreateIndexWaitPopup(QMessageBox):
    def __init__(self, parent=None):
        super(CreateIndexWaitPopup, self).__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle('Generating Demos Index - Please Wait')
        self.setText("Ensuring you have easy access to most up-to-date Demos")
        self.setIcon(QMessageBox.Information)
        # Set the standard OK button
        # self.setStandardButtons(QMessageBox.Ok)

    def showEvent(self, event):
        super().showEvent(event)
        # Calculate the width required to show the title fully
        font_metrics = QFontMetrics(self.font())
        # 50 is added for padding and icon space
        title_width = font_metrics.width(self.windowTitle()) + 50
        # Resize if necessary
        if title_width > self.width():
            self.setFixedWidth(title_width)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Calculate the required width to show the title fully
        font_metrics = QFontMetrics(self.font())
        title_width = font_metrics.width(self.windowTitle()) + 50  # Add extra space for padding and icon
        text_width = font_metrics.width(self.text()) + 50  # Calculate width required for the text

        # Determine the maximum necessary width
        required_width = max(title_width, text_width, self.width())

        # Resize if necessary to ensure both title and text are visible
        if required_width > self.width():
            self.setFixedWidth(required_width)

def getDemoRootPath() -> Path | None:
    """
    Credit to https://stackoverflow.com/a/74532549/16519580 user Chris.
    """

    if Configuration.check_if_setting_exists("DemosPath"):
        demosPath = Configuration.getSetting("DemosPath")
        demosPath = Path(demosPath)
        # Ensure path is not the root dir
        if len(list(demosPath.parents)) > 1 and demosPath.exists():
            return demosPath

    # Start at location of python.exe and check in every
    # parent directory for Demos until we hit the root.
    startDir = Path(__file__)

    for currPath in [startDir] + list(startDir.parents):
        demosPath = currPath.joinpath("CompuCell3D/Demos")
        if demosPath.exists():
            Configuration.setSetting("DemosPath", str(demosPath))
            return demosPath

    return None  # No demos here!


def getDemoList(demo_root_path:Optional[Path]=None) -> list[Path]:
    glob_results = demo_root_path.rglob("*.cc3d")
    glob_results = [p.relative_to(demo_root_path) for p in glob_results]

    return glob_results


def formatDemoName(name) -> str:
    outStr = name[0].upper()
    prev = "A"
    i = 1
    while i < len(name):
        c = name[i]
        if (c == "_" or c == "-") and prev != " ":
            c = " "
        elif c.islower() and prev == " ":
            c = c.upper()
        elif c.isupper():
            if prev.islower() or (i + 1 < len(name) and name[i + 1].islower()):
                outStr += " "

        outStr += c
        prev = c
        i += 1
    return outStr


def splitByUppercase(word):
    # Extract individual words from camel/pascal case tokens.
    # Example: "lambdaVolume" splits into "lambda" and "Volume".
    start = 0
    i = 1
    while i <= len(word):
        if word[i - 1].islower() and (i == len(word) or word[i].isupper()):
            if i - start < len(word):
                yield word[start:i]
            start = i
        i += 1


def tokenizeAllFiles(demoAbsPath):
    methods = (("*.py", tokenizePython), ("*.xml", tokenizeXml), (DESCRIPTION_FNAME, tokenizeText))
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
            word = re.sub("[^a-zA-Z \n\.]", ".", word)  # Remove numbers and special chars
            for varName in word.split("."):
                yield varName


def tokenizeXml(line):
    """
    Generates all the key words (XML tag names and parameter names)
    from a line of XML.
    """
    if "!--" in line:  # exclude comments, even if they have useful tags
        return
    for word in re.split("[^a-zA-Z]", line):
        yield word


def tokenizeText(line):
    for word in re.split("[^a-zA-Z]", line):
        yield word


def preIndexSearchResults(demo_root_path:Optional[Path]=None):
    """
    Creates and returns a map of keywords to lists of paths to demos.
    Each path is an absolute path and a string.
    """
    max_matches = 7  # how many demos each keyword can map to

    search_index = {}

    demo_list = list(getDemoList(demo_root_path))

    for demoPath in demo_list:
        full_path = demo_root_path.joinpath(demoPath)

        words_seen = set()
        for word in tokenizeAllFiles(full_path):
            if word not in words_seen:
                small_path = str(demoPath)  # conserve memory by converting object to str
                if word in search_index and len(search_index[word]) < max_matches:
                    search_index[word].append(small_path)
                else:
                    search_index[word] = [small_path]
                words_seen.add(word)
    return search_index


def checkForDemoUpdates(demo_root_path:Optional[Path]=None):
    """
    Returns true if any demo has been modified or created
    since the last time we indexed them.
    Returns false if everything is up-to-date.
    """
    if demo_root_path is None:
        return False

    last_edit_time = 0
    for file in demo_root_path.rglob("*"):
        if file.lstat().st_mtime > last_edit_time:
            last_edit_time = file.lstat().st_mtime

    modified = False
    if Configuration.check_if_setting_exists("LastDemoEditTime"):
        if last_edit_time > Configuration.getSetting("LastDemoEditTime"):
            modified = True
    else:
        modified = True

    if modified:
        Configuration.setSetting("LastDemoEditTime", last_edit_time)

    return modified


def loadSearchIndex(demo_root_path:Optional[Path]=None):
    index_file_path = demo_root_path.joinpath(INDEX_FILE_NAME)
    search_index = {}

    if not index_file_path.exists():
        return search_index

    with open(index_file_path, "r") as fp:
        for line in fp.readlines():
            parsed = line.split(DELIMITER)
            if len(parsed) >= 2:
                keyword = parsed[0]
                paths = parsed[1:]

                # Ensure the paths still exist, but keep them as string type
                paths = [p for p in paths if demo_root_path.joinpath(Path(p)).exists()]

                if paths:
                    search_index[keyword] = paths

    if not search_index:
        print("Warning: Failed to read any demos from", INDEX_FILE_NAME, "file. Maybe the files no longer exist?")

    return search_index


def createOrLoadSearchIndex(modified:bool, demo_root_path:Optional[Path]=None):
    """
    Returns a map of key words to lists of paths to demos.
    """
    if modified:
        idx = loadSearchIndex(demo_root_path=demo_root_path)
        if idx:
            return idx

    print("Please wait while we scan the demos for key words...")
    new_idx = preIndexSearchResults(demo_root_path=demo_root_path)
    print("Done indexing demos.")

    # Save newly indexed demos
    index_file_path = demo_root_path.joinpath(INDEX_FILE_NAME)
    with open(index_file_path, "w") as fp:
        fp.write("YOU DO NOT NEED TO MODIFY THIS FILE. CompuCell3D Player reads and writes to it on its own.\n")
        for keyWord, paths in new_idx.items():
            fp.write(keyWord + DELIMITER)
            fp.write(DELIMITER.join(paths))
            fp.write("\n")
    # Configuration.setSetting("LastDemoEditTime", time.time())

    return new_idx
