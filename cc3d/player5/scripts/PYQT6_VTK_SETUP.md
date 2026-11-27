# PyQt6 and VTK 9.7 setup on macOS

This guide records the working configuration tested in the CC3D player
environment on Apple Silicon with Python 3.12, PyQt6, and VTK 9.7.

## Working configuration

The important details are:

1. Register the VTK OpenGL and interaction backends.
2. Select `QOpenGLWidget` through `vtkmodules.qt.QVTKRWIBase`.
3. Set that value before importing `QVTKRenderWindowInteractor`.
4. Create the Qt window and show it first.
5. Initialize and render the VTK widget from a short Qt timer.
6. Do not call `QVTKRenderWindowInteractor.Start()`; Qt owns the event loop.

```python
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow

# This must happen before importing QVTKRenderWindowInteractor.
import vtkmodules.qt

vtkmodules.qt.QVTKRWIBase = "QOpenGLWidget"

# Register VTK backends before creating VTK rendering objects.
from vtkmodules import vtkInteractionStyle, vtkRenderingOpenGL2  # noqa: F401
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.setCentralWidget(self.vtk_widget)

        renderer = vtkRenderer()
        renderer.SetBackground(0.08, 0.10, 0.14)
        self.vtk_widget.GetRenderWindow().AddRenderer(renderer)

        cone = vtkConeSource()
        cone.SetResolution(32)

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(cone.GetOutputPort())

        actor = vtkActor()
        actor.SetMapper(mapper)
        renderer.AddActor(actor)
        self.renderer = renderer

    def initialize_vtk(self):
        self.vtk_widget.Initialize()
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()


app = QApplication(sys.argv)
window = MainWindow()
window.resize(800, 700)
window.show()

# Give Qt time to create the native QOpenGLWidget surface first.
QTimer.singleShot(100, window.initialize_vtk)

raise SystemExit(app.exec())
```

The working incremental test is [qt6_window_only_1.py](qt6_window_only.py).

## Why the ordering matters

With VTK 9.7, the QVTK wrapper reads the base Qt widget class from
`vtkmodules.qt.QVTKRWIBase`. Setting an operating-system environment variable
was ineffective in this environment. The setting must be made directly on the
module before importing `QVTKRenderWindowInteractor`:

```python
import vtkmodules.qt
vtkmodules.qt.QVTKRWIBase = "QOpenGLWidget"
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
```

The default `QWidget` backend caused `Initialize()` to block the Qt GUI thread
on macOS. The window became unresponsive and produced repeated
`QPainter::begin: Paint device returned engine == 0` messages. The
`QOpenGLWidget` backend creates a Qt-owned OpenGL surface and remains
responsive.

Initialization also must not happen while the main window is being
constructed. Showing the window and then initializing from `QTimer.singleShot`
allows Cocoa and Qt to create the native OpenGL surface before VTK renders.

## Event-loop ownership

For a QVTK widget embedded in PyQt6:

```python
self.vtk_widget.Initialize()
self.vtk_widget.GetRenderWindow().Render()
app.exec()
```

Do not call:

```python
self.vtk_widget.Start()
```

`Start()` belongs to standalone VTK applications. Calling it from a Qt
application can create a nested event loop or block the player thread.

## Standalone VTK versus Qt-embedded VTK

The standalone test [vtk_cone_minimal.py](vtk_cone_minimal.py) uses VTK's
Cocoa/OpenGL path directly. It is useful for proving that VTK rendering and
the graphics driver work independently of Qt.

The Qt-embedded test [qt6_window_only_1.py](qt6_window_only.py) uses
`QVTKRenderWindowInteractor` and must use `QOpenGLWidget` as described above.
The two paths are not interchangeable: a successful standalone VTK window
does not guarantee that the default QWidget-based QVTK wrapper is configured
correctly.

## Debugging sequence

When diagnosing a new environment, test in this order:

1. Run `qt6_window_only.py` to verify that PyQt6 can display a normal window.
2. Run `qt6_window_only.py` with VTK imports but no rendering objects.
3. Add the QVTK widget and cone renderer.
4. Confirm that `QVTKRenderWindowInteractor.__mro__` contains
   `PyQt6.QtOpenGLWidgets.QOpenGLWidget`.
5. Only then integrate the same setup into the CC3D player.

Useful backend check:

```python
import vtkmodules.qt
vtkmodules.qt.QVTKRWIBase = "QOpenGLWidget"
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

print(QVTKRenderWindowInteractor.__mro__[:3])
```

Expected output includes:

```text
PyQt6.QtOpenGLWidgets.QOpenGLWidget
```

