from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from cc3d.core.enums import *

from cc3d.player5 import Graphics
from .WindowInventory import WindowInventory
import sys
from math import ceil, sqrt
from weakref import ref
from gc import collect


class SubWindow(QFrame):
    def __init__(self, _parent):
        super(SubWindow, self).__init__(_parent)
        self.parent = _parent
        self.main_widget = None
        # self.setWindowFlags(Qt.Window|Qt.CustomizeWindowHint|Qt.WindowMaximizeButtonHint|Qt.WindowMinimizeButtonHint\
        # |Qt.WindowCloseButtonHint|Qt.FramelessWindowHint)

        # note Qt.Drawer looks completely different on OSX than on Windows.
        # QWindow on the other hand on linux displays all windows in dock widget and behaves stranegely
        # thus the settings below
        # are actually the ones that work on all platforms

        if sys.platform.startswith('darwin'):
            # on OSX we apply different settings than on other platforms
            self.setWindowFlags(
                Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint
                | Qt.WindowCloseButtonHint | Qt.FramelessWindowHint
            )
        else:
            self.setWindowFlags(
                Qt.Dialog | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
            )

    @property
    def parent(self):
        try:
            o = self._parent()
        except TypeError:
            o = self._parent
        return o

    @parent.setter
    def parent(self, _i):
        try:
            self._parent = ref(_i)
        except TypeError:
            self._parent = _i

    @property
    def main_widget(self):
        try:
            o = self._main_widget()
        except TypeError:
            o = self._main_widget
        return o

    @main_widget.setter
    def main_widget(self, _i):
        try:
            self._main_widget = ref(_i)
        except TypeError:
            self._main_widget = _i

    def setWidget(self, widget):
        """
        Places widget  in the frame's layout

        :param widget:widget to be added to Qframe
        :return:None
        """
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addWidget(widget)
        # layout.setMargin(0)
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(0)
        self.main_widget = widget
        self.setLayout(layout)

    def sizeHint(self):
        """
        returns suggested size for qframe

        :return:QSize
        """
        return QSize(400, 400)

    def widget(self):
        """
        main widget displayed in Qframe

        :return: main widget displayed in Qframe
        """
        return self.main_widget

    def mousePressEvent(self, ev):
        """
        handler for mouse click event - updates self.parent.lastActiveRealWindow member variable

        :param ev: mousePressEvent
        :return:None
        """
        self.parent.lastActiveRealWindow = self
        super(SubWindow, self).mousePressEvent(ev)

    def mouseDoubleClickEvent(self, ev):
        """
        handler for mouse double-click event - updates self.parent.lastActiveRealWindow member variable

        :param ev:  mouseDoubleClickEvent
        :return:None
        """
        self.parent.lastActiveRealWindow = self
        super(SubWindow, self).mouseDoubleClickEvent(ev)

    # def changeEvent(self, ev):
    #     """
    #     sets MainArea's lastActiveRealWindow - currently inactive
    #     :param ev: QEvent
    #     :return:None
    #     """
    #
    #     return
    # if ev.type() == QEvent.ActivationChange:
    #     if self.isActiveWindow():
    #         print 'will activate ', self
    #         self.parent.lastActiveRealWindow = self
    #
    # super(DockSubWindow,self).changeEvent(ev)

    def closeEvent(self, ev):
        """
        handler for close event event - removes sub window from inventory

        :param ev:  closeEvent
        :return:None
        """
        widget = self.widget()
        if widget:
            widget.closeEvent(ev)
        self.parent.removeSubWindow(self)
        super(SubWindow, self).closeEvent(ev)


class PythonSteeringSubWindow(QFrame):
    def __init__(self, _parent=None):
        super(PythonSteeringSubWindow, self).__init__(_parent)
        self.title = 'Steering Panel'
        self.parent = _parent
        self.main_widget = None


class MainArea(QWidget):
    def __init__(self, stv, ui):

        self.MDI_ON = False

        self.stv = stv  # SimpleTabView
        self.UI = ui  # UserInterface

        self.win_inventory = WindowInventory()

        self.lastActiveRealWindow = None  # keeps track of the last active real window
        self.last_suggested_window_position = QPoint(0, 0)

    @property
    def stv(self):
        """
        SimpleTabView inheriting instance; same as self

        :return: SimpleTabView instance
        :rtype: cc3d.player5.Plugins.ViewManagerPlugins.SimpleTabView.SimpleTabView
        """
        return self._stv()

    @stv.setter
    def stv(self, _i):
        self._stv = ref(_i)

    @property
    def UI(self):
        """
        Parent UserInterface

        :return: parent
        :rtype: cc3d.player5.UI.UserInterface.UserInterface
        """
        return self._UI()

    @UI.setter
    def UI(self, _i):
        self._UI = ref(_i)

    @property
    def lastActiveRealWindow(self):
        """
        Last active subwindow if any, otherwise None
        """
        try:
            o = self._lastActiveRealWindow()
        except TypeError:
            o = self._lastActiveRealWindow
        return o

    @lastActiveRealWindow.setter
    def lastActiveRealWindow(self, _i):
        try:
            self._lastActiveRealWindow = ref(_i)
        except TypeError:
            self._lastActiveRealWindow = _i

    def suggested_window_position(self):
        """
        returns suggested position of the next window

        :return:QPoint - position of the next window
        """

        rec = QApplication.desktop().screenGeometry()

        if self.last_suggested_window_position.x() == 0 and self.last_suggested_window_position.y() == 0:

            self.last_suggested_window_position = QPoint(int(rec.width() / 5), int(rec.height() / 5))
            return self.last_suggested_window_position
        else:
            from random import randint
            self.last_suggested_window_position = QPoint(randint(int(rec.width() / 5), int(rec.width() / 2)),
                                                         randint(int(rec.height() / 5), int(rec.height() / 2)))
            return self.last_suggested_window_position

    def addSubWindow(self, widget):
        """
        adds subwindow containing widget to the player5

        :param widget: widget to be added to sub windows
        :return:None
        """

        # print('INSTANCE OF GraphicsFrameWidget =  ',
        #       isinstance(widget, Graphics.GraphicsFrameWidget.GraphicsFrameWidget))
        obj_type = 'other'
        if isinstance(widget, Graphics.GraphicsFrameWidget.GraphicsFrameWidget):
            obj_type = GRAPHICS_WINDOW_LABEL

        elif isinstance(widget, Graphics.PlotFrameWidget.PlotFrameWidget):
            obj_type = PLOT_WINDOW_LABEL

        elif isinstance(widget, Graphics.PopupMessageWidget.PopupMessageWidget):
            obj_type = MESSAGE_WINDOW_LABEL


        window_name = obj_type + ' ' + str(self.win_inventory.get_counter())

        subWindow = self.createSubWindow(name=window_name)  # sub windowª
        self.setupSubWindow(subWindow, widget, window_name)

        # inserting widget into dictionary
        self.win_inventory.add_to_inventory(obj=subWindow, obj_type=obj_type)

        return subWindow

    def addSteeringSubWindow(self, widget):
        """
        Creates QMdiSubwindow containing widget and adds it to QMdiArea

        :param widget: widget that will be placed in the qmdisubwindow
        :return: None
        """

        mdi_sub_window = PythonSteeringSubWindow(self)
        subWindow = self.createSubWindow(name='Steering Panel')  # sub window
        self.setupSubWindow(subWindow, widget, 'Steering Panel')

        subWindow.resize(widget.sizeHint())

        self.win_inventory.add_to_inventory(obj=mdi_sub_window, obj_type=STEERING_PANEL_LABEL)
        return mdi_sub_window

    def tileSubWindows(self):
        """
        Tiles floating Player windows across the available screen area.

        :return: None
        """
        windows = self.__arrangeable_windows()
        if not windows:
            return

        available_rect = self.__available_arrangement_rect(reserve_main_window=True)
        margin = 12
        spacing = 8
        window_count = len(windows)
        column_count = int(ceil(sqrt(window_count)))
        row_count = int(ceil(float(window_count) / column_count))
        tile_width = max(240, int((available_rect.width() - 2 * margin - spacing * (column_count - 1)) / column_count))
        tile_height = max(200, int((available_rect.height() - 2 * margin - spacing * (row_count - 1)) / row_count))

        for idx, win in enumerate(windows):
            row = int(idx / column_count)
            column = idx % column_count
            x = available_rect.x() + margin + column * (tile_width + spacing)
            y = available_rect.y() + margin + row * (tile_height + spacing)
            win.showNormal()
            win.setGeometry(x, y, tile_width, tile_height)
            win.raise_()

        self.setActiveSubWindow(windows[-1])

    def cascadeSubWindows(self):
        """
        Cascades floating Player windows across the available screen area.

        :return: None
        """
        windows = self.__arrangeable_windows()
        if not windows:
            return

        available_rect = self.__available_arrangement_rect(reserve_main_window=True)
        margin = 24
        offset = 32
        cascade_width = min(900, max(360, int(available_rect.width() * 0.68)))
        cascade_height = min(700, max(300, int(available_rect.height() * 0.68)))
        max_x = available_rect.right() - cascade_width - margin
        max_y = available_rect.bottom() - cascade_height - margin
        x = available_rect.x() + margin
        y = available_rect.y() + margin

        for win in windows:
            if x > max_x or y > max_y:
                x = available_rect.x() + margin
                y = available_rect.y() + margin
            win.showNormal()
            win.setGeometry(x, y, cascade_width, cascade_height)
            win.raise_()
            x += offset
            y += offset

        self.setActiveSubWindow(windows[-1])

    def move_windows_to_screen(self, screen_index):
        """
        Moves the main Player window and floating subwindows to another screen without resizing them.

        :param screen_index: target screen index in QApplication.screens()
        :type screen_index: int
        :return: None
        """
        screens = QApplication.screens()
        if screen_index < 0 or screen_index >= len(screens):
            return

        windows = [self.UI] + self.__arrangeable_windows()
        if not windows:
            return

        target_rect = screens[screen_index].availableGeometry()
        margin = 12
        source_rect = QRect(windows[0].frameGeometry())
        for win in windows[1:]:
            source_rect = source_rect.united(win.frameGeometry())

        offset = target_rect.topLeft() + QPoint(margin, margin) - source_rect.topLeft()
        for win in windows:
            target_pos = win.pos() + offset
            target_pos = self.__constrained_window_position(win, target_pos, target_rect, margin)
            win.move(target_pos)
            win.raise_()

    def __constrained_window_position(self, win, position, available_rect, margin):
        """
        Keeps a moved window's top-left position within the target screen.

        :param win: window being moved
        :param position: requested top-left position
        :param available_rect: target screen available geometry
        :param margin: screen-edge margin
        :return: QPoint
        """
        width = win.frameGeometry().width()
        height = win.frameGeometry().height()
        min_x = available_rect.left() + margin
        min_y = available_rect.top() + margin
        max_x = max(min_x, available_rect.right() - width - margin + 1)
        max_y = max(min_y, available_rect.bottom() - height - margin + 1)
        x = max(min_x, min(position.x(), max_x))
        y = max(min_y, min(position.y(), max_y))

        return QPoint(x, y)

    def __arrangeable_windows(self):
        """
        Returns visible floating subwindows that should participate in layout operations.

        :return: list of SubWindow objects
        """
        windows = []
        for win in self.subWindowList():
            widget = win.widget()
            if widget is not None and getattr(widget, 'is_screenshot_widget', False):
                continue
            if not win.isVisible():
                continue
            windows.append(win)

        return windows

    def __available_arrangement_rect(self, reserve_main_window=False):
        """
        Returns the available geometry of the screen that owns the active Player window.

        :param reserve_main_window: optional flag that reserves space for the main Player window
        :type reserve_main_window: bool
        :return: QRect
        """
        reference_point = self.UI.frameGeometry().center()
        if self.lastActiveRealWindow is not None:
            reference_point = self.lastActiveRealWindow.frameGeometry().center()

        screen = QApplication.screenAt(reference_point)
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is not None:
            available_rect = screen.availableGeometry()
        else:
            available_rect = QApplication.desktop().availableGeometry()

        if reserve_main_window:
            return self.__arrangement_rect_excluding_main_window(available_rect)

        return available_rect

    def __arrangement_rect_excluding_main_window(self, available_rect):
        """
        Moves the main Player window to the top-left and returns the remaining area for floating windows.

        :param available_rect: available screen geometry
        :type available_rect: QRect
        :return: QRect
        """
        margin = 12
        spacing = 8
        main_window = self.UI
        main_window.move(available_rect.topLeft() + QPoint(margin, margin))
        main_window.raise_()

        remaining_x = main_window.frameGeometry().right() + spacing
        remaining_width = available_rect.right() - remaining_x - margin + 1
        if remaining_width >= 320:
            return QRect(
                remaining_x,
                available_rect.y(),
                remaining_width,
                available_rect.height()
            )

        remaining_y = main_window.frameGeometry().bottom() + spacing
        remaining_height = available_rect.bottom() - remaining_y - margin + 1
        if remaining_height >= 240:
            return QRect(
                available_rect.x(),
                remaining_y,
                available_rect.width(),
                remaining_height
            )

        return available_rect

    def activeSubWindow(self):
        """
        returns last active subwindow

        :return: SubWindow object
        """
        print('returning lastActiveRealWindow=', self.lastActiveRealWindow)
        return self.lastActiveRealWindow

    def setActiveSubWindow(self, win):
        """
        Activates subwindow win

        :param: win - SubWindow object
        :return: None
        """
        win.activateWindow()
        self.lastActiveRealWindow = win

    def subWindowList(self):
        """
        returns list of all open subwindows

        :return: python list of SubWindow objects
        """
        return list(self.win_inventory.values())

    def createSubWindow(self, name):
        """
        Creates SubWindow with title specified using name parameter

        :param: name -  subwindow title
        :return: SubWindow object
        """

        sub_window = SubWindow(self)
        sub_window.setObjectName(name)
        return sub_window

    def setupSubWindow(self, sub_window, widget, caption):
        """
        Configures subwindow by placing widget in to qframe layout, setting window title (caption)
        and showing subwindow

        :param: sub_window - SubWindow object
        :param: widget - widget to be placed into sub_window
        :param: caption - subwindow title
        :return: None
        """

        if caption is None:
            caption = ''

        sub_window.setWindowTitle(caption)
        sub_window.setWidget(widget)
        sub_window.show()

    def removeSubWindow(self, widget: QFrame) -> None:
        """
        Removes a QFrame from the QWidget.

        If there are any windows left in the inventory, the first one is activated.

        :param widget: subwindow
        :type widget: QFrame
        :return: None
        """
        self.win_inventory.remove_from_inventory(widget)
        widget.deleteLater()
        if widget is self.activateWindow():
            win_list = self.win_inventory.values()
            if win_list:
                self.setActiveSubWindow(win_list[0])
            else:
                self.lastActiveRealWindow = None
        collect()
