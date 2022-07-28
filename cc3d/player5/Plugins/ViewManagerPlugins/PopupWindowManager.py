from .PopupMessageWindowInterface import PopupMessageWindowInterface
from PyQt5 import QtCore
from cc3d.player5.Graphics.PopupMessageWidget import PopupMessageWidget
from cc3d.player5.Plugins.ViewManagerPlugins.PopupWindowManagerBase import PopupWindowManagerBase
from cc3d.core.enums import *
from cc3d.player5.Graphics.GraphicsWindowData import GraphicsWindowData
import cc3d.player5.Configuration as Configuration


class PopupWindowManager(QtCore.QObject, PopupWindowManagerBase):

    new_popup_window_signal = QtCore.pyqtSignal(QtCore.QMutex, object)

    def __init__(self, view_manager=None):
        QtCore.QObject.__init__(self, None)
        PopupWindowManagerBase.__init__(self, view_manager)

        self.popup_window_list = []
        self.popup_window_mutex = QtCore.QMutex()
        self.signals_initialized = False

    def reset(self):
        self.plot_window_list = []

    def init_signal_and_slots(self):
        # since initSignalAndSlots can be called in SimTabView multiple times
        # (after each simulation restart) we have to ensure that signals are connected only once
        # otherwise there will be an avalanche of signals - each signal for each additional
        # simulation run this will cause lots of extra windows to pop up

        if not self.signals_initialized:
            self.new_popup_window_signal.connect(self.process_request_for_new_popup_window)
            self.signals_initialized = True

    def restore_popup_layout(self):
        """
        This function restores popup layout - it is called from CompuCellSetup.py inside mainLoopNewPlayer function
        :return:
        """

        windows_layout_dict = Configuration.getSetting('WindowsLayout')

        if not windows_layout_dict:
            return

        for winId, win in self.vm.win_inventory.getWindowsItems(MESSAGE_WINDOW_LABEL):
            popup_message_widget = win.widget()

            # plot_frame_widget.plotInterface is a weakref
            # getting weakref
            msg_window_interface = popup_message_widget.msg_window_interface()

            # if weakref to plot_interface is None we ignore such window
            if not msg_window_interface:
                continue

            if str(popup_message_widget.title) in list(windows_layout_dict.keys()):
                window_data_dict = windows_layout_dict[str(popup_message_widget.title)]

                gwd = GraphicsWindowData()
                gwd.fromDict(window_data_dict)

                if gwd.winType != 'message':
                    return

                win.resize(gwd.winSize)
                win.move(gwd.winPosition)
                win.setWindowTitle(popup_message_widget.title)

    def get_new_popup_window(self, specs=None):
        """
        Returns recently added plot window
        :param specs:
        :return:
        """


        self.popup_window_mutex.lock()

        self.new_popup_window_signal.emit(self.popup_window_mutex, specs)
        # processRequestForNewPlotWindow will be called and it will
        # unlock drawMutex but before it will finish running
        # (i.e. before the new window is actually added)we must make sure that getNewPlotwindow does not return
        self.popup_window_mutex.lock()
        self.popup_window_mutex.unlock()

        # returning recently added window
        return self.popup_window_list[-1]

    def get_popup_windows_layout_dict(self):
        """
        Returns dictionary that summarizes how popup windows geometry should be saved
        in the settings file
        """

        windows_layout = {}

        for winId, win in self.vm.win_inventory.getWindowsItems(MESSAGE_WINDOW_LABEL):
            popup_message_widget = win.widget()
            # getting weakref
            msg_window_interface = popup_message_widget.msg_window_interface()
            if not msg_window_interface:
                continue

            gwd = GraphicsWindowData()
            # gwd.sceneName = msg_window_interface.title
            gwd.sceneName = popup_message_widget.title
            gwd.winType = 'message'
            # plot_window = plot_interface.plotWindow
            mdi_msg_window = win
            gwd.winSize = mdi_msg_window.size()
            gwd.winPosition = mdi_msg_window.pos()

            windows_layout[gwd.sceneName] = gwd.toDict()

        return windows_layout

    def process_request_for_new_popup_window(self, _mutex, specs):

        if not self.vm.simulationIsRunning:
            return

        new_window = PopupMessageWidget(self.vm, **specs)

        new_window.show()

        mdi_msg_window = self.vm.addSubWindow(new_window)

        mdi_msg_window.setWindowTitle(specs['title'])

        suggested_win_pos = self.vm.suggested_window_position()

        if suggested_win_pos.x() != -1 and suggested_win_pos.y() != -1:
            mdi_msg_window.move(suggested_win_pos)

        self.vm.lastActiveRealWindow = mdi_msg_window

        new_window.show()

        msg_window_interface = PopupMessageWindowInterface(new_window)
        # store plot window interface in the window list
        self.popup_window_list.append(msg_window_interface)

        self.popup_window_mutex.unlock()
