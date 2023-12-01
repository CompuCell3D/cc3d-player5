from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from cc3d.player5.CustomGui.CTabWidget import CTabWidget
from cc3d.player5.styles import tab_bar_style
from .ConsoleWidget import ConsoleWidget

try:
    from .ErrorConsole import ErrorConsole

    qsci_error_console_exits = True
except ImportError:
    qsci_error_console_exits = False


class Console(CTabWidget):
    def __init__(self, parent):
        QTabWidget.__init__(self, parent)
        self.setTabPosition(QTabWidget.South)
        self.tabBar().setStyleSheet(tab_bar_style)

        # self.__errorConsole.setText("Error: XML Error \n  File: cellsort_2D_error.xml\n
        # Line: 23 Col: 1 has the following problem not well-formed (invalid token) \n\n\n\n")

        self.std_out_text_color = QColor("black")
        self.std_err_text_color = QColor("red")

        self.__stdout = ConsoleWidget(text_color=self.std_out_text_color)
        self.__stdout.ensureCursorVisible()
        self.__stdoutIndex = self.addTab(self.__stdout, "Output")

        if qsci_error_console_exits:
            self.__errorConsole = ErrorConsole(self)
        else:
            self.__errorConsole = ConsoleWidget(text_color=self.std_err_text_color)
            self.__errorConsole.ensureCursorVisible()

        self.__errorIndex = self.addTab(self.__errorConsole, "Errors")
        self.__menu = QMenu(self)
        self.__menu.addAction("Clear", self.__handle_clear)
        self.__menu.addAction("Copy", self.__handle_copy)
        self.__menu.addSeparator()
        self.__menu.addAction("Select All", self.__handle_select_all)

        self.setTabContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__handle_show_context_menu)

        # self.setSizePolicy(
        #     QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        # self.connect(self,SIGNAL('customTabContextMenuRequested(const QPoint &, int)'),
        #              self.__handleShowContextMenu)

    def get_std_err_console(self):
        return self.__stdout

    def get_syntax_error_console(self):
        return self.__errorConsole

    def bring_up_syntax_error_console(self):
        self.setCurrentWidget(self.__errorConsole)

    def bring_up_output_console(self):
        self.setCurrentWidget(self.__stdout)

    def __handle_show_context_menu(self, coord, index):
        """
        Private slot to show the tab context menu.

        @param coord the position of the mouse pointer (QPoint)
        @param index index of the tab the menu is requested for (integer)
        """
        self.__menuIndex = index
        coord = self.mapToGlobal(coord)
        self.__menu.popup(coord)

    def __handle_clear(self):
        """
        Private slot to handle the clear tab menu entry.
        """
        self.widget(self.__menuIndex).clear()

    def __handle_copy(self):
        """
        Private slot to handle the copy tab menu entry.
        """
        self.widget(self.__menuIndex).copy()

    def __handle_select_all(self):
        """
        Private slot to handle the select all tab menu entry.
        """
        self.widget(self.__menuIndex).selectAll()

    def show_log_tab(self, tabname):
        """
        Public method to show a particular Log-Viewer tab.

        @param tabname string naming the tab to be shown ("stdout", "stderr")
        """
        if tabname == "stdout":
            self.setCurrentIndex(self.__stdoutIndex)
        # elif tabname == "stderr":
        # self.setCurrentIndex(self.__stderrIndex)
        else:
            raise RuntimeError("wrong tabname given")

    def set_stdout_content(self, txt):
        self.__stdout.setTextColor(self.std_out_text_color)
        self.__stdout.setText(txt)

    def set_stderr_content(self, txt):
        self.__errorConsole.setTextColor(self.std_out_text_color)
        self.__errorConsole.setText(txt)

    def append_to_stdout(self, txt):
        """
        Public slot to appand text to the "stdout" tab.

        @param txt text to be appended (string or QString)
        """

        self.__stdout.setTextColor(self.std_out_text_color)

        self.__stdout.insertPlainText(txt)
        self.__stdout.ensureCursorVisible()

        # QApplication.processEvents() #this is causing application crash

    def append_to_stderr(self, txt):
        """
        Public slot to appand text to the "stderr" tab.

        @param txt text to be appended (string or QString)
        """
        return

    # Changes the initial size of the console
    def sizeHint(self):
        return QSize(self.width(), 100)
