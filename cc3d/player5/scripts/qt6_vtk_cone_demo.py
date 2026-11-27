"""Minimal PyQt6 + VTK Qt interactor smoke test.

Run with the CC3D environment, for example:

    python -m cc3d.player5.scripts.qt6_vtk_cone_demo

The demo intentionally uses Qt's event loop and does not call
``QVTKRenderWindowInteractor.Start()``.  The VTK interactor is embedded in a
normal Qt window and Qt drives repaint and timer events.
"""

from __future__ import annotations

import sys
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow

# VTK 9.7 reads the QVTK base class from vtkmodules.qt.  Select the Qt-owned
# OpenGL surface before importing QVTKRenderWindowInteractor.
import vtkmodules.qt

vtkmodules.qt.QVTKRWIBase = "QOpenGLWidget"

# Register the VTK rendering and interaction backends before creating objects.
from vtkmodules import vtkInteractionStyle, vtkRenderingOpenGL2  # noqa: F401
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
)


class ConeGraphicsWindow(QMainWindow):
    """Top-level graphics window, matching the macOS Player layout."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Graphics 0")
        self.resize(520, 520)

        vtk_widget = QVTKRenderWindowInteractor()
        self.vtk_widget = vtk_widget
        self.setCentralWidget(vtk_widget)
        self._setup_scene()

    def initialize_vtk(self) -> None:
        # The window must already be visible so Cocoa has created the native
        # QOpenGLWidget surface. Qt owns the event loop; never call Start().
        self.vtk_widget.Initialize()
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

    def _setup_scene(self) -> None:
        cone = vtkConeSource()
        cone.SetResolution(48)
        cone.SetHeight(3.0)
        cone.SetRadius(1.25)
        cone.Update()

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(cone.GetOutputPort())

        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.2, 0.65, 0.95)

        renderer = vtkRenderer()
        renderer.SetBackground(0.08, 0.10, 0.14)
        renderer.AddActor(actor)
        self.renderer = renderer
        self.vtk_widget.GetRenderWindow().AddRenderer(renderer)


def main() -> int:
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("PyQt6 + VTK cone demo")
    main_window.resize(900, 700)
    main_window.setCentralWidget(QLabel("Main CC3D-style window"))

    graphics_window = ConeGraphicsWindow()
    main_window.show()
    graphics_window.show()
    graphics_window.move(main_window.x() + main_window.width() + 20, main_window.y())

    # Let Cocoa/Qt create the native OpenGL surface before initializing VTK.
    QTimer.singleShot(100, graphics_window.initialize_vtk)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
