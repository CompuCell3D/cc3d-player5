import os
import cc3d.player5.Configuration as Configuration
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

    return makeMovie(simulationPath, frameRate, quality, writeText)
