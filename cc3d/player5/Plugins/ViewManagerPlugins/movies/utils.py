from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cc3d.player5.Configuration as Configuration
from cc3d.core.GraphicsUtils.MovieCreator import makeMovieAsync
import os
import sys
import shutil
import subprocess
from pathlib import Path


def choose_movie_directory(parent=None):
    current_project_dir = Configuration.getSetting("OutputLocation")
    if not current_project_dir or not Path(current_project_dir).exists():
        current_project_dir = "/"
    dir_name = QFileDialog.getExistingDirectory(
        parent, "Specify CC3D Project Directory", current_project_dir, QFileDialog.ShowDirsOnly
    )
    dir_name = str(dir_name)
    dir_name.rstrip()
    if dir_name == "":
        return None

    simulation_path = Path(dir_name).resolve()

    has_project_file = False
    has_simulation_dir = False

    for p in simulation_path.glob("*"):
        if p.is_dir():
            if p.stem.lower() == "simulation":
                has_simulation_dir = True
        else:
            if p.suffix.lower() == ".cc3d":
                has_project_file = True

    if not has_simulation_dir or not has_project_file:
        QMessageBox.warning(
            None,
            "WARN",
            "This does not look like a simulation directory. "
            "Please choose a folder inside your CompuCell3D Workspace that "
            "contains a .cc3d file, a Simulation sub-directory, and at least "
            "one sub-directory with .png files created from screenshots.",
            QMessageBox.Ok,
        )
        return None

    return simulation_path


def display_movie_creation_result(movie_count, q_label_obj):
    if movie_count < 1:
        label_styling("No movies were made", q_label_obj, "red", 600)
    elif movie_count == 1:
        label_styling("1 movie successfully made", q_label_obj, "green", 600)
    else:
        label_styling(f"{movie_count} movies successfully made", q_label_obj, "green", 600)
    q_label_obj.setVisible(True)


def label_styling(text, q_label_obj, color="#000000", font_weight=400):
    """
    Apply rich-text styling to a QLabel.

    color may be:
      - Hex: "#FF0000"
      - Qt name: "darkRed", "royalblue", "green"
      - Qt.GlobalColor (Qt.red, Qt.green, etc.)
    """

    # Convert color to QColor safely
    if isinstance(color, QColor):
        qcolor = color
    else:
        qcolor = QColor(color)

    if not qcolor.isValid():
        print(f"WARNING: Invalid color '{color}', falling back to black")
        qcolor = QColor("black")

    css_color = qcolor.name()  # always "#RRGGBB"

    q_label_obj.setTextFormat(Qt.RichText)
    q_label_obj.setText(f'<span style="color:{css_color}; font-weight:{font_weight};">{text}</span>')
    q_label_obj.setVisible(True)


def create_movies_runner(
    status_label_obj, simulation_path,  frame_rate, quality, enable_drawing_mcs, display_movie_callback
):
    try:
        label_styling("", status_label_obj, "black", 600)

        label_styling(f"Generating movies...", status_label_obj, "#007AFF", 600)

        quality = max(quality, 1)
        # Convert from 1-10 domain to 0-51 domain
        quality = int((1.0 - (quality / 10.0)) * 52.0) - 1

        makeMovieAsync(simulation_path, frame_rate, quality, enable_drawing_mcs, display_movie_callback)
        Configuration.setSetting("RecentMoviePath", str(simulation_path))

    except Exception as e:
        print(e)
        QMessageBox.warning(
            None,
            "WARN",
            "There was a problem creating the movie. "
            "Please reach out to us on Reddit or GitHub Issues if this problem persists.",
            QMessageBox.Ok,
        )


def find_ffmpeg():
    """
    Robust cross-platform ffmpeg locator.
    Returns absolute path to ffmpeg executable or None.
    """

    candidates = []

    # 1) PATH lookup (safe: always pass str)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        candidates.append(ffmpeg)

    # 2) Conda / virtualenv
    env_prefix = os.environ.get("CONDA_PREFIX") or sys.prefix
    if env_prefix:
        bin_dir = Path(env_prefix) / ("Scripts" if sys.platform.startswith("win") else "bin")
        candidates.append(str(bin_dir / ("ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg")))

    # 3) Homebrew (macOS)
    if sys.platform.startswith("darwin"):
        candidates += [
            "/opt/homebrew/bin/ffmpeg",  # Apple Silicon
            "/usr/local/bin/ffmpeg",  # Intel Homebrew
        ]

    # 4) Windows common locations
    if sys.platform.startswith("win"):
        candidates += [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        ]

    # 5) Remove duplicates and non-existing
    candidates = list(dict.fromkeys(candidates))

    for path in candidates:
        if not path:
            continue
        path = str(Path(path).resolve())
        if not os.path.isfile(path):
            continue
        if not os.access(path, os.X_OK):
            continue

        # Verify it actually runs
        try:
            subprocess.run(
                [path, "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2,
            )
            return path
        except Exception:
            continue

    return None
