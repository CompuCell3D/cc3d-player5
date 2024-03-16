from pathlib import Path
import sys
import subprocess
import cc3d.player5.Configuration as Configuration
from PyQt5.QtWidgets import QMessageBox
from cc3d.core.GraphicsUtils.MovieCreator import makeMovie

def makeMovieWithSettings():
    try:
        # Choose the most recently modified subdir of the project dir
        projectPathRoot = Configuration.getSetting("OutputLocation")
        projectPathRoot = Path(projectPathRoot)
        maxLastModifiedTime = 0
        simulationPath = None
        for dirName in projectPathRoot.glob('*'):
            dirPath = projectPathRoot.joinpath(dirName)
            if dirPath.is_dir():
                if dirPath.lstat().st_mtime > maxLastModifiedTime:
                    maxLastModifiedTime = dirPath.lstat().st_mtime
                    simulationPath = dirPath

        frameRate = Configuration.getSetting("FrameRate")
        quality = Configuration.getSetting("Quality")
        writeText = Configuration.getSetting("WriteMovieMCS")

        numMoviesMade, moviePath = makeMovie(simulationPath, frameRate, quality, writeText)

        if numMoviesMade > 0 and moviePath:
            Configuration.setSetting("RecentMoviePath", str(moviePath.resolve()))

        return numMoviesMade, moviePath
    except:
        print("There was a problem generating the movie. You can try generating another one from the Configuration menu.")


def showMovieInFileExplorer(self):
    try:
        if Configuration.check_if_setting_exists("RecentMoviePath"):
            dirToOpen = Configuration.getSetting("RecentMoviePath")
        elif Configuration.check_if_setting_exists("OutputLocation"):
            dirToOpen = Configuration.getSetting("OutputLocation")

        if not Path(dirToOpen).exists():
            dirToOpen = "/"

        if sys.platform.startswith('win'):
            subprocess.run(['explorer', '/select,', dirToOpen], shell=True)
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', '-R', dirToOpen])
        elif sys.platform.startswith('linux'):
            QMessageBox.warning(None, "WARN",
                                "Linux is not supported.",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(None, "WARN",
                                "Your operating system is not supported.",
                                QMessageBox.Ok)
    except:
        QMessageBox.warning(None, "WARN",
                            "Sorry, opening your file explorer failed.",
                            QMessageBox.Ok)
