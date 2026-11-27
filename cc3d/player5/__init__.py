try:
    # needed to avoid import errors on some windows systems
    import vtk
except ImportError:
    print('vtk not found. Ignoring for now')

# Configure the Qt6/VTK integration before any player graphics module imports
# QVTKRenderWindowInteractor.
from cc3d.player5.Graphics.vtk_qt_setup import configure_vtk_qt

configure_vtk_qt()

from cc3d.core.GraphicsOffScreen import *


def _hook_cc3d_player():
    """
    Hooks Player configuration with core: Player uses a static configuration and has additional settings

    :return: None
    """
    from . import Configuration
    from cc3d.CompuCellSetup import persistent_globals

    def get_configuration():
        return Configuration

    persistent_globals.set_configuration_getter(get_configuration)


_hook_cc3d_player()
