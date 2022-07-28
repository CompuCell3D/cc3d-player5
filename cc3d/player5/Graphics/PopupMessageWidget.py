import warnings
from weakref import ref

try:
    import webcolors as wc
except ImportError:
    warnings.warn('Could not find webcolors. Run "pip install webcolors" to fix this', RuntimeWarning)

from PyQt5 import QtCore, QtWidgets


class PopupMessageWidget(QtWidgets.QFrame):
    def __init__(self, parent=None, **kwds):
        QtWidgets.QFrame.__init__(self, parent)

        self.params = kwds
        self.popup_message_widget = QtWidgets.QPlainTextEdit()
        self.msg_window_interface = None
        self.title = self.params['title']

        # try:
        #     bg_color = kwds['background']
        # except LookupError:
        #     bg_color = None
        #
        # if bg_color:
        #     try:
        #         bg_color_rgb = wc.name_to_rgb(bg_color)
        #         self.plotWidget.setBackground(background=bg_color_rgb)
        #     except ValueError as e:
        #         print('Could not decode the color %s : Exception : %s'%(bg_color, str(e)), file=sys.stderr)

        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        # self.plotInterface = None

        # self.parentWidget = parent
        layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
        layout.addWidget(self.popup_message_widget)

        # self.plotWidget.setTitle(kwds['title'])
        # self.plotWidget.setLabel(axis='bottom', text=kwds['xAxisTitle'])
        # self.plotWidget.setLabel(axis='left', text=kwds['yAxisTitle'])
        # x_log_flag, y_log_flag = False, False
        # if kwds['xScaleType'].strip().lower() == 'log':
        #     x_log_flag = True
        #
        # if kwds['yScaleType'].strip().lower() == 'log':
        #     y_log_flag = True
        #
        # self.plotWidget.setLogMode(x=x_log_flag, y=y_log_flag)
        # if kwds['grid']:
        #     self.plotWidget.showGrid(x=True, y=True, alpha=1.0)

        self.setLayout(layout)
        # needs to be defined to resize smaller than 400x400
        self.setMinimumSize(100, 100)

    @property
    def parentWidget(self):
        """
        Parent if any, otherwise None
        """
        try:
            o = self._parentWidget()
        except TypeError:
            o = self._parentWidget
        return o

    @parentWidget.setter
    def parentWidget(self, _i):
        try:
            self._parentWidget = ref(_i)
        except TypeError:
            self._parentWidget = _i


    # def resizePlot(self, x, y):
    #
    #     self.plotWidget.sizeHint = QtCore.QSize(x, y)
    #     self.plotWidget.resize(self.plotWidget.sizeHint)
    #     self.resize(self.plotWidget.sizeHint)
    #
    # def getPlotParams(self):
    #     """
    #     Fetches a dictionary of parameters describing plot
    #
    #     :return: {dict}
    #     """
    #     return self.plot_params

    def closeEvent(self, ev):
        pass
