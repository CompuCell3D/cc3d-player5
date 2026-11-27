"""PyQt6 window with VTK imports, but no VTK widget yet.

This is the first incremental step after ``qt6_window_only.py``.  It checks
that importing the VTK modules used by the cone demo does not affect Qt
startup before a render window or QVTK widget is created.
"""

from __future__ import annotations

import sys

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QTextEdit

# Select the Qt-owned OpenGL surface before importing QVTK.  The VTK 9.7
# wrapper reads this setting from vtkmodules.qt, not from an environment
# variable.
import vtkmodules.qt

vtkmodules.qt.QVTKRWIBase = "QOpenGLWidget"

# VTK imports copied from the cone demo.
from vtkmodules import vtkInteractionStyle, vtkRenderingOpenGL2  # noqa: F401
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor  # noqa: F401
from vtkmodules.vtkFiltersSources import vtkConeSource  # noqa: F401
from vtkmodules.vtkRenderingCore import (  # noqa: F401
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
)


def main() -> int:
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("PyQt6 window with VTK imports")
    window.resize(900, 700)

    text_edit = QTextEdit()
    text_edit.setPlainText(
        "PyQt6 window is working with the VTK modules imported.\n\n"
        "The VTK cone should appear on the right."
    )

    vtk_widget = QVTKRenderWindowInteractor(window)
    renderer = vtkRenderer()
    renderer.SetBackground(0.08, 0.10, 0.14)
    vtk_widget.GetRenderWindow().AddRenderer(renderer)

    cone = vtkConeSource()
    cone.SetResolution(32)
    cone.SetHeight(3.0)
    cone.SetRadius(1.25)

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(cone.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.2, 0.65, 0.95)
    renderer.AddActor(actor)

    splitter = QSplitter(Qt.Orientation.Horizontal, window)
    splitter.addWidget(text_edit)
    splitter.addWidget(vtk_widget)
    splitter.setSizes([450, 700])
    window.setCentralWidget(splitter)

    window.show()
    window.raise_()
    window.activateWindow()

    def initialize_vtk() -> None:
        vtk_widget.Initialize()
        renderer.ResetCamera()
        vtk_widget.GetRenderWindow().Render()

    QTimer.singleShot(100, initialize_vtk)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
