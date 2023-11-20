import os
import sys
import subprocess
import cc3d.player5.Configuration as Configuration
from PyQt5.QtWidgets import QMessageBox
from cc3d.core.GraphicsUtils.MovieCreator import makeMovie

def makeMovieWithSettings():
    # Choose the most recently modified subdir of the project dir
    projectPathRoot = Configuration.getSetting("OutputLocation")
    maxLastModifiedTime = 0
    simulationPath = None
    for dirName in os.listdir(projectPathRoot):
        dirPath = os.path.join(projectPathRoot, dirName)
        if os.path.isdir(dirPath):
            if os.path.getmtime(dirPath) > maxLastModifiedTime:
                maxLastModifiedTime = os.path.getmtime(dirPath)
                simulationPath = dirPath

    frameRate = Configuration.getSetting("FrameRate")
    quality = Configuration.getSetting("Quality")
    writeText = Configuration.getSetting("WriteMovieMCS")

    numMoviesMade, moviePath = makeMovie(simulationPath, frameRate, quality, writeText)

    Configuration.setSetting("RecentMoviePath", moviePath)

    return numMoviesMade, moviePath


def showMovieInFileExplorer(self):
    if Configuration.check_if_setting_exists("RecentMoviePath"):
        dirToOpen = Configuration.getSetting("RecentMoviePath")
    elif Configuration.check_if_setting_exists("OutputLocation"):
        dirToOpen = Configuration.getSetting("OutputLocation")

    if not os.path.exists(dirToOpen):
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
