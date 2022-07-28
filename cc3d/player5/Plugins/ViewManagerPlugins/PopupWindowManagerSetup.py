from .PopupWindowManagerBase import PopupWindowManagerBase
from .PopupWindowManager import PopupWindowManager

# called from SimpleTabView
def create_popup_window_manager(view_manager=None):
    """

    :param view_manager: instance of viewManager
    :return:
    """
    # todo detect if we are running in PLayer or not and return appropriate interface
    return PopupWindowManager(view_manager)
    # if plots_available:
    #     return PlotManager(view_manager, True)
    # else:
    #     return PlotManagerBase(view_manager, False)
