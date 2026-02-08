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
from cc3d.player5.Utilities import safe_callback, open_folder_in_file_browser


class MovieGeneratorDialog(QDialog, Ui_MovieGeneratorDialog):
    moviesCreatedSignal = pyqtSignal(int)

    def __init__(self, parent=None):
        super(MovieGeneratorDialog, self).__init__(parent)

        if sys.platform.startswith("win"):
            # dialogs without context help - only close button exists
            self.setWindowFlags(Qt.Drawer)

        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.setupUi(self)

        self.moviesCreatedSignal.connect(self.display_movie_result)

        # Wire buttons
        self.pushButton.clicked.connect(self.on_detect_ffmpeg)
        self.generate_movies_PB.clicked.connect(self.on_generate_movies)
        self.generate_movies_PB.setEnabled(False)
        self.browse_PB.clicked.connect(self.on_browse)

        self.simulation_output_folder_LE.textChanged.connect(
            self.on_simulation_folder_text_changed
        )

        self.show_movies_folder_PB.clicked.connect(self.show_movies_folder)

        # initialize
        self.ffmpeg_path = Configuration.getSetting("FfmpegLocation")
        self.ffmpeg_path_LE.setText(self.ffmpeg_path)
        self.status_LB.setText("")

        self.simulation_path = None
        if Configuration.check_if_setting_exists("RecentMoviePath"):
            self.simulation_path = Configuration.getSetting("RecentMoviePath")
            self.set_up_simulation_output_folder()

        self.frame_rate = Configuration.getSetting("FrameRate")
        self.quality = Configuration.getSetting("Quality")

        self.quality_SB.setValue(int(self.quality))
        self.frame_rate_SB.setValue(int(self.frame_rate))

    @safe_callback
    def show_movies_folder(self, *args, **kwargs):

        folder_with_movies = Path("/").resolve().anchor
        if Path(self.simulation_path).exists() and Path(self.simulation_path).is_dir():
            folder_with_movies = self.simulation_path
        elif Configuration.check_if_setting_exists("RecentMoviePath"):
            folder_with_movies_tmp =  Configuration.getSetting("RecentMoviePath")
            if Path(folder_with_movies_tmp).exists() and Path(folder_with_movies_tmp).is_dir():
                folder_with_movies = Path(folder_with_movies_tmp)



        open_folder_in_file_browser(folder_with_movies, parent=self)

    @safe_callback
    def on_simulation_folder_text_changed(self, text):

        path = Path(text).expanduser()

        if path.exists() and path.is_dir():
            self.simulation_path = str(path)
            self.generate_movies_PB.setEnabled(True)
        else:
            self.generate_movies_PB.setEnabled(False)

    @safe_callback
    def on_detect_ffmpeg(self, *args, **kwargs):
        self.reset_ffmpeg_location()

    @safe_callback
    def on_generate_movies(self, *args, **kwargs):

        self.create_movie_button_clicked()

    @safe_callback
    def set_up_simulation_output_folder(self):
        if Path(self.simulation_path).exists() and Path(self.simulation_path).is_dir():
            self.simulation_output_folder_LE.setText(str(self.simulation_path))
            self.generate_movies_PB.setEnabled(True)

    @safe_callback
    def on_browse(self, *args, **kwargs):

        self.simulation_path = choose_movie_directory(parent=self)
        if self.simulation_path is None:
            return
        self.set_up_simulation_output_folder()

    def reset_ffmpeg_location(self):
        ffmpeg_location = find_ffmpeg()
        if not ffmpeg_location:
            self.show_ffmpeg_warning()
            return None

        self.ffmpeg_path_LE.setText(ffmpeg_location)
        label_styling("Successfully Detected FFMPEG", self.status_LB, "dodgerblue", 600)
        return ffmpeg_location

    def show_ffmpeg_warning(self):
        QMessageBox.warning(
            None,
            "WARN",
            "FFMPEG executable not found. "
            "Please install FFMPEG or, if you already have it, specify its path manually "
            "in the FFMPEG Executable box.",
            QMessageBox.Ok,
        )

    @safe_callback
    def create_movie_button_clicked(self):
        if not Path(self.ffmpeg_path).exists():
            self.show_ffmpeg_warning()
            return

        def display_movie_callback(future):
            try:
                movie_count, movie_path = future.result()
            except TypeError:
                label_styling(f"Failed to generate movies in folder {self.simulation_path}. Check if the folder exists", self.status_LB, "dodgerblue", 600)
                return

            self.moviesCreatedSignal.emit(movie_count)


        create_movies_runner(
            status_label_obj=self.status_LB,
            simulation_path=self.simulation_path,
            frame_rate=self.frame_rate_SB.value(),
            quality=self.quality_SB.value(),
            enable_drawing_mcs=self.mcs_on_frame_CB.isChecked(),
            display_movie_callback=display_movie_callback,
        )

    def closeEvent(self, a0, QCloseEvent=None):
        Configuration.setSetting("FrameRate", self.frame_rate_SB.value())
        Configuration.setSetting("Quality", self.quality_SB.value())

    def display_movie_result(self, movie_count):
        display_movie_creation_result(movie_count=movie_count, q_label_obj=self.status_LB)
        if movie_count > 0:
            Configuration.setSetting("RecentMoviePath", str(self.simulation_path))




