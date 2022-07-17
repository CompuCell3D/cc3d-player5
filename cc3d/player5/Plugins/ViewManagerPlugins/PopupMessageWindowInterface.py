# -*- coding: utf-8 -*-
import weakref
from PyQt5 import QtCore
import warnings
from cc3d.core.PySteppables import *

try:
    import webcolors as wc
except ImportError:
    warnings.warn('Could not find webcolors. Run "pip install webcolors" to fix this', RuntimeWarning)

PLOT_TYPE_POSITION = 3
(XYPLOT, HISTOGRAM, BARPLOT) = list(range(0, 3))
MAX_FIELD_LENGTH = 25

# Notice histogram and Bar Plot implementations need more work.
# They are functional but have a bit strange syntax and for Bar Plot we can only plot one series per plot


class PopupMessageWindowInterface(QtCore.QObject):

    add_text_signal = QtCore.pyqtSignal(dict, QtCore.QMutex)

    def __init__(self, msg_window=None):

        QtCore.QObject.__init__(self, None)

        if msg_window:
            self.msg_window = msg_window

            self.msg_window.msg_window_interface = weakref.ref(self)
            self.text_widget = self.msg_window.popup_message_widget

        self.init_signals_and_slots()
        self.msg_window_interface_mutex = QtCore.QMutex()


    def init_signals_and_slots(self):
        self.add_text_signal.connect(self.add_text_handler)

    def clear(self):
        self.text_widget.clear()

    def set_title_handler(self, title):
        self.title = str(title)
        self.text_widget.setTitle(title)

    def set_title(self, title):
        self.title = str(title)
        self.setTitleSignal.emit(title)

    def print(self, *args, style=None, color=None):
        """
        User's API function - adds a data series plot to the plotting window

        :param style:
        :param color:
        :return:
        """
        text = ''
        for t in args:
            text += f'{str(t)} '
        text_specs = dict(text=text, style=style, color=color)
        self.msg_window_interface_mutex.lock()
        self.add_text_signal.emit(text_specs, self.msg_window_interface_mutex)
        # wait here until add_text_signal gets handled
        self.msg_window_interface_mutex.lock()
        self.msg_window_interface_mutex.unlock()

    def add_text_handler(self, text_specs: dict):
        """
        Actually puts the text into text widget
        """
        # self.text_widget.appendPlainText('html')
        # self.msg_window_interface_mutex.unlock()
        # return
        color = text_specs['color']
        style_tag = f'style="color:{color}; "' if color else ''
        html = f"<span {style_tag}>{text_specs['text']}<span>"
        style = text_specs['style']
        if style is not None:
            html = f"<strong>{html}</strong>" if style & BOLD else html
            html = f"<em>{html}</em>" if style & ITALIC else html
            html = f"<u>{html}</u>" if style & UNDERLINE else html
            html = f"<s>{html}</s>" if style & STRIKE else html
        self.text_widget.appendHtml(html)
        self.msg_window_interface_mutex.unlock()

