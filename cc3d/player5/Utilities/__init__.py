"""pyQt widgets for VTK."""

# The old local QVTK implementations are PyQt5/QGLWidget-era code and are not
# part of the Qt6 player API. Graphics code must use the VTK 9.7 wrapper after
# cc3d.player5.Graphics.vtk_qt_setup has configured QOpenGLWidget.
__all__ = []

from cc3d.player5.Utilities.utils import *
