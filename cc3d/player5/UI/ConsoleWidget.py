from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .ConsoleWidgetBase import ConsoleWidgetBase


class ConsoleWidget(ConsoleWidgetBase, QTextEdit):
    """
    Class providing a specialized text edit for displaying logging information.
    """

    def __init__(self, text_color=QColor("black"), parent=None):
        """
        Constructor

        @param parent reference to the parent widget (QWidget)
        """
        QTextEdit.__init__(self, parent)
        self.text_color = text_color
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setReadOnly(True)
        self.setFrameStyle(QFrame.NoFrame)

        # Why do I need this? create the context menu
        self.__menu = QMenu(self)
        self.__menu.addAction("Clear", self.clear)
        self.__menu.addAction("Copy", self.copy)
        self.__menu.addSeparator()
        self.__menu.addAction("Select All", self.selectAll)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__handleShowContextMenu)
        # self.setSizePolicy(
        #     QSizePolicy(QSizePolicy.Expanding,
        #                           QSizePolicy.Expanding))

    def set_player_main_widget(self, main_player_widget):
        pass

    def connect_close_cc3d_signal(self, callback):
        pass

    def emitCloseCC3D(self):
        pass

    def set_service_port_cc3d_sender(self, port: int):
        pass

    def is_qsci_based(self):
        return False

    def __handleShowContextMenu(self, coord):
        """
        Private slot to show the context menu.

        @param coord the position of the mouse pointer (QPoint)
        """
        coord = self.mapToGlobal(coord)
        self.__menu.popup(coord)

    def appendText(self, txt):
        """
        Public method to append text to the end.

        @param txt text to insert (QString)
        """
        tc = self.textCursor()
        tc.movePosition(QTextCursor.End)
        self.setTextCursor(tc)
        self.insertPlainText(txt)
        self.ensureCursorVisible()

    def setText(self, txt):
        self.setTextColor(self.text_color)
        super(ConsoleWidget, self).setText(txt)
