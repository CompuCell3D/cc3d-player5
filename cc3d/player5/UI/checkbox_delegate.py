from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QApplication, QTableView, QStyleOptionButton, QStyle


class CheckBoxDelegate(QtWidgets.QItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox cell of the column to which it's applied.
    """
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        """
        Important, otherwise an editor is created if the user clicks in this cell.
        """
        return None

    def draw_checkbox(self, value:bool, painter, option):
        checkbox = QStyleOptionButton()
        checkbox.rect = option.rect
        checkbox.state |= QStyle.State_On if value else QStyle.State_Off
        checkbox.state |= QStyle.State_Enabled
        # checkbox.state |= QStyle.State_MouseOver if option.state & QStyle.State_MouseOver else QStyle.State_None

        QApplication.style().drawControl(QStyle.CE_CheckBox, checkbox, painter)

    def paint(self, painter, option, index):
        """
        Paint a checkbox without the label.
        """
        try:
            value = bool(int(index.data()))
            self.draw_checkbox(value=value, painter=painter, option=option)
        except TypeError:
            print('got option ', option, ' index=', index.row())
            pass


    def editorEvent(self, event, model, option, index):
        """
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton and this cell is editable. Otherwise do nothing.

        :param event:
        :param model:
        :param option:
        :param index:
        :return:
        """
        if not int(index.flags() & QtCore.Qt.ItemIsEditable) > 0:
            return False

        if event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
            # Change the checkbox-state
            self.setModelData(None, model, index)
            return True

        return False

    def setModelData(self, editor, model, index):
        """
        The user wanted to change the old state in the opposite.
        :param editor:
        :param model:
        :param index:
        :return:
        """
        model.setData(index, 1 if int(index.data()) == 0 else 0, QtCore.Qt.EditRole)
