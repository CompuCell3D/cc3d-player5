from PyQt5 import QtCore
from weakref import ref


class PopupWindowManagerBase:

    new_popup_window_signal = QtCore.pyqtSignal(QtCore.QMutex, object)

    def __init__(self, view_manager=None):

        self.vm = view_manager

    @property
    def vm(self):
        try:
            o = self._vm()
        except TypeError:
            o = self._vm
        return o

    @vm.setter
    def vm(self, _i):
        try:
            self._vm = ref(_i)
        except TypeError:
            self._vm = _i


    def reset(self):
        pass

    def init_signal_and_slots(self):
        pass

    def restore_popup_layout(self):
        pass

    def get_new_popup_window(self, specs=None):
        pass

    def get_popup_windows_layout_dict(self):
        pass

    def process_request_for_new_popup_window(self, _mutex, specs):
        pass
