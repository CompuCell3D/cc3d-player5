from pathlib import Path
import sys
import subprocess
import cc3d.player5.Configuration as Configuration
from PyQt5.QtWidgets import QMessageBox
from cc3d.core.GraphicsUtils.MovieCreator import makeMovieAsync
from os import startfile

def getLastSimulationDir() -> Path:
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

        return simulationPath

    except Exception as ex:
        print("There was a problem finding the last simulation directory.")
        raise ex


def makeMovieWithSettings() -> None:
    """
    Asynchronously creates movie(s) of the last-run simulation using the settings already set for movie generation.
    """
    try:
        simulationPath = getLastSimulationDir()
        if simulationPath:
            Configuration.setSetting("RecentMoviePath", str(simulationPath))
        else:
            return
        frameRate = Configuration.getSetting("FrameRate")
        quality = Configuration.getSetting("Quality")
        writeText = Configuration.getSetting("WriteMovieMCS")

        makeMovieAsync(simulationPath, frameRate, quality, writeText)

    except Exception as ex:
        print("There was a problem generating the movie. You can try generating another one from the Configuration menu.", ex)


def showMovieInFileExplorer(self) -> None:
    try:
        dirToOpen = None
        if Configuration.check_if_setting_exists("RecentMoviePath"):
            dirToOpen = Configuration.getSetting("RecentMoviePath")
        
        if not Path(dirToOpen).exists():
            if Configuration.check_if_setting_exists("OutputLocation"):
                dirToOpen = Configuration.getSetting("OutputLocation")
                print("chose OutputLocation",dirToOpen)

        if not dirToOpen or not Path(dirToOpen).exists():
            QMessageBox.warning(None, "WARN",
                                "No simulation output folder could be found. Check your settings and try again." + dirToOpen,
                                QMessageBox.Ok)
            return

        if sys.platform.startswith('win'):
            startfile(dirToOpen)
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
    except Exception as ex:
        print(ex)
        QMessageBox.warning(None, "WARN",
                            "Sorry, opening your file explorer failed.",
                            QMessageBox.Ok)
