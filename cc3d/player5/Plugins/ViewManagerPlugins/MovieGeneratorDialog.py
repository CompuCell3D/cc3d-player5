from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
import shutil
import cc3d.player5.Configuration as Configuration
from cc3d.player5.Plugins.ViewManagerPlugins.ui_movie_generator_dialog import Ui_MovieGeneratorDialog
import sys

class MovieGeneratorDialog(QDialog, Ui_MovieGeneratorDialog):
    def __init__(self, parent=None):
        super(MovieGeneratorDialog, self).__init__(parent)

        if sys.platform.startswith('win'):
            # dialogs without context help - only close button exists
            self.setWindowFlags(Qt.Drawer)


        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.setupUi(self)


        # Wire buttons
        self.pushButton.clicked.connect(self.on_detect_ffmpeg)
        self.generate_movies_PB.clicked.connect(self.on_generate_movies)



        # initialize
        self.ffmpeg_path = Configuration.getSetting("FfmpegLocation")
        self.ffmpeg_path_LE.setText(self.ffmpeg_path)
        self.status_LB.setText("Frame Rate, and Quality are set in the configuration dialog")
        # self.frame_rate = Configuration.getSetting("FrameRate")
        # self.quality = Configuration.getSetting("Quality")

        # self.frame_rate_LB.setTextFormat(Qt.RichText)
        # self.quality_LB.setTextFormat(Qt.RichText)
        #
        # self.frame_rate_LB.setText(f"<b>Frame Rate:</b> {self.frame_rate}")
        # self.quality_LB.setText(f"<b>Quality:</b> {self.quality}")

    # -----------------------
    # Button callbacks
    # -----------------------

    def on_detect_ffmpeg(self):
        print("Detect FFMPEG clicked")
        print("quality=", self.quality_SB.value())
        print("frame rate=", self.frame_rate_SB.value())
        self.resetFfmpegLocation()
        
    def on_generate_movies(self):
        print("Generate Movies clicked")

    def resetFfmpegLocation(self):
        ffmpegLocation = shutil.which("ffmpeg")
        if not ffmpegLocation:
            self.showFfmpegWarning()
            return

        self.ffmpeg_path_LE.setText(ffmpegLocation)
        self.status_LB.setText(
            '<span style="color:#007AFF; font-weight:600;">Successfully Detected FFMPEG</span>'
        )
        return ffmpegLocation

    def showFfmpegWarning(self):
        QMessageBox.warning(None, "WARN",
                            "FFMPEG executable not found. "
                            "Please install FFMPEG or, if you already have it, specify its path manually "
                            "in the FFMPEG Executable box.",
                            QMessageBox.Ok)



    def chooseMovieDirectory(self):
        currentProjectDir = Configuration.getSetting('OutputLocation')
        if not currentProjectDir or not Path(currentProjectDir).exists():
            currentProjectDir = "/"
        dirName = QFileDialog.getExistingDirectory(self, "Specify CC3D Project Directory", currentProjectDir,
                                                    QFileDialog.ShowDirsOnly)
        dirName = str(dirName)
        dirName.rstrip()
        if dirName == "":
            return None

        simulationPath = Path(dirName).resolve()

        hasProjectFile = False
        hasSimulationDir = False

        for p in simulationPath.glob('*'):
            if p.is_dir():
                if p.stem.lower() == "simulation":
                    hasSimulationDir = True
            else:
                if p.suffix.lower() == ".cc3d":
                    hasProjectFile = True

        if not hasSimulationDir or not hasProjectFile:
            QMessageBox.warning(None, "WARN",
                                "This does not look like a simulation directory. "
                                "Please choose a folder inside your CompuCell3D Workspace that "
                                "contains a .cc3d file, a Simulation sub-directory, and at least "
                                "one sub-directory with .png files created from screenshots.",
                                QMessageBox.Ok)
            return None

        return simulationPath


    def createMovieButtonClicked(self):
        try:
            self.createMovieResultLabel.setText("")
            if not Path(self.ffmpeg_path).exists():
                self.showFfmpegWarning()
                return

            simulationPath = self.chooseMovieDirectory()
            if not simulationPath:
                return

            self.status_LB.setText('<span style="color:#007AFF; font-weight:600;">Generating movies...</span>')

            frameRate = max(self.frame_rate_SB.value(), 1)
            quality = float(self.quality_SB.value())
            quality = max(quality, 1)
            # Convert from 1-10 domain to 0-51 domain
            quality = int((1.0 - (quality / 10.0)) * 52.0) - 1
            enableDrawingMCS = self.mcs_on_frame_CB.isChecked()

            # def displayMovieCallback(future):
            #     movieCount, moviePath = future.result()
            #     self.moviesCreatedSignal.emit(movieCount)
            #
            # makeMovieAsync(simulationPath, frameRate, quality, enableDrawingMCS, displayMovieCallback)
            # Configuration.setSetting("RecentMoviePath", str(simulationPath))

        except Exception as e:
            print(e)
            QMessageBox.warning(None, "WARN",
                            "There was a problem creating the movie. "
                            "Please reach out to us on Reddit or GitHub Issues if this problem persists.",
                            QMessageBox.Ok)


    # def displayMovieResult(self, movieCount):
    #     if movieCount < 1:
    #         self.createMovieResultLabel.setText("No movies were made")
    #     elif movieCount == 1:
    #         self.createMovieResultLabel.setText("Movie successfully made")
    #     else:
    #         self.createMovieResultLabel.setText(str(movieCount) + " movies successfully made")
    #     self.createMovieResultLabel.setVisible(True)
