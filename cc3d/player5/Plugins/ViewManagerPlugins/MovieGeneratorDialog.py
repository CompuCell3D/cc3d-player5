from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cc3d.player5.Configuration as Configuration

from cc3d.player5.Plugins.ViewManagerPlugins.ui_movie_generator_dialog import Ui_MovieGeneratorDialog

import sys
from pathlib import Path

from cc3d.player5.Plugins.ViewManagerPlugins.movies.utils import (
    create_movies_runner,
    choose_movie_directory,
    find_ffmpeg,
    label_styling,
    display_movie_creation_result,
)


class MovieGeneratorDialog(QDialog, Ui_MovieGeneratorDialog):
    moviesCreatedSignal = pyqtSignal(int)

    def __init__(self, parent=None):
        super(MovieGeneratorDialog, self).__init__(parent)

        if sys.platform.startswith("win"):
            # dialogs without context help - only close button exists
            self.setWindowFlags(Qt.Drawer)

        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.setupUi(self)

        self.moviesCreatedSignal.connect(self.displayMovieResult)

        # Wire buttons
        self.pushButton.clicked.connect(self.on_detect_ffmpeg)
        self.generate_movies_PB.clicked.connect(self.on_generate_movies)
        self.generate_movies_PB.setEnabled(False)
        self.browse_PB.clicked.connect(self.on_browse)

        # initialize
        self.ffmpeg_path = Configuration.getSetting("FfmpegLocation")
        self.ffmpeg_path_LE.setText(self.ffmpeg_path)
        self.status_LB.setText("")

        self.simulation_path = None
        self.frame_rate = Configuration.getSetting("FrameRate")
        self.quality = Configuration.getSetting("Quality")

        self.quality_SB.setValue(int(self.quality))
        self.frame_rate_SB.setValue(int(self.frame_rate))

    def on_detect_ffmpeg(self):
        self.resetFfmpegLocation()

    def on_generate_movies(self):

        self.createMovieButtonClicked()

    def on_browse(self):

        self.simulation_path = choose_movie_directory(parent=self)
        if self.simulation_path is None:
            return
        if Path(self.simulation_path).exists() and Path(self.simulation_path).is_dir():
            self.simulation_output_folder_LE.setText(str(self.simulation_path))
            self.generate_movies_PB.setEnabled(True)

    def resetFfmpegLocation(self):
        ffmpegLocation = find_ffmpeg()

        if not ffmpegLocation:
            self.showFfmpegWarning()
            return None

        self.ffmpeg_path_LE.setText(ffmpegLocation)
        label_styling("Successfully Detected FFMPEG", self.status_LB, "dodgerblue", 600)
        return ffmpegLocation

    def showFfmpegWarning(self):
        QMessageBox.warning(
            None,
            "WARN",
            "FFMPEG executable not found. "
            "Please install FFMPEG or, if you already have it, specify its path manually "
            "in the FFMPEG Executable box.",
            QMessageBox.Ok,
        )

    def createMovieButtonClicked(self):
        if not Path(self.ffmpeg_path).exists():
            self.showFfmpegWarning()
            return

        def display_movie_callback(future):
            movieCount, moviePath = future.result()
            self.moviesCreatedSignal.emit(movieCount)

        create_movies_runner(
            status_label_obj=self.status_LB,
            simulation_path=self.simulation_path,
            ffmpeg_path=self.ffmpeg_path,
            frame_rate=self.frame_rate_SB.value(),
            quality=self.quality_SB.value(),
            enable_drawing_mcs=self.mcs_on_frame_CB.isChecked(),
            display_movie_callback=display_movie_callback,
        )

    def closeEvent(self, a0, QCloseEvent=None):
        Configuration.setSetting("FrameRate", self.frame_rate_SB.value())
        Configuration.setSetting("Quality", self.quality_SB.value())

    def displayMovieResult(self, movieCount):
        display_movie_creation_result(movie_count=movieCount, q_label_obj=self.status_LB)


