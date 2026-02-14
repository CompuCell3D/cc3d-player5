# From core; do not remove unless you're looking for trouble, or making Player-specific implementations!
from pathlib import Path

from cc3d.core.GraphicsUtils.utils import *
from cc3d.player5.UI.cell_type_colors import default_cell_type_color_list
from collections import namedtuple, OrderedDict
from typing import Dict, Optional
from PyQt5.QtGui import QColor, QDesktopServices
from PyQt5.QtCore import Qt, QUrl
import traceback
from functools import wraps
from PyQt5.QtWidgets import QMessageBox, QLabel, QTextEdit
import sys

cell_type_color_props = namedtuple('cell_type_color_props', 'color type_name invisible')



def get_monospace_font_stack():
    if sys.platform == "darwin":
        return "Menlo, Monaco, monospace"
    elif sys.platform.startswith("win"):
        return "Consolas, Courier New, monospace"
    else:
        return "DejaVu Sans Mono, Liberation Mono, monospace"

def show_exception_messagebox(
    title: str,
    message: str,
    exception: Exception,
    parent=None,
):
    tb_str = "".join(traceback.format_exception(
        type(exception), exception, exception.__traceback__)
    )

    msg = QMessageBox(parent)

    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)

    msg.setText(f"<b>{message}</b>")
    font_stack = get_monospace_font_stack()

    msg.setInformativeText(
        f"<pre style='font-family: {font_stack};'>"
        f"{str(exception)}</pre>"
    )

    msg.setDetailedText(tb_str)

    msg.setStandardButtons(QMessageBox.Ok)

    msg.setTextInteractionFlags(Qt.TextSelectableByMouse)

    # ---- FORCE WIDER DIALOG ----
    desired_width = 800

    # Resize main dialog
    msg.resize(desired_width, msg.sizeHint().height())

    # Resize internal label
    label = msg.findChild(QLabel, "qt_msgbox_label")
    if label:
        label.setMinimumWidth(desired_width)

    # Resize informative label
    info_label = msg.findChild(QLabel, "qt_msgbox_informativelabel")
    if info_label:
        info_label.setMinimumWidth(desired_width)

    # Resize detailed traceback area
    text_edit = msg.findChild(QTextEdit)
    if text_edit:
        text_edit.setMinimumWidth(desired_width)
        text_edit.setMinimumHeight(300)

    msg.exec_()



def safe_callback(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            traceback.print_exc()

            show_exception_messagebox(
                title="Player Error",
                message="An unexpected error occurred while executing the operation.",
                exception=e,
                parent=None,
            )

    return wrapper


def open_folder_in_file_browser(path, parent=None) -> bool:
    """
    Opens the given folder in the system file browser.

    Returns True if successful, False otherwise.
    """

    if not path:
        QMessageBox.warning(
            parent,
            "Folder not available",
            "Path is not set.",
            QMessageBox.Ok,
        )
        return False

    folder = Path(path)

    if not folder.exists():
        QMessageBox.warning(
            parent,
            "Folder not found",
            f"The folder does not exist:\n{folder}",
            QMessageBox.Ok,
        )
        return False

    # If file, open parent folder
    if folder.is_file():
        folder = folder.parent

    url = QUrl.fromLocalFile(str(folder))

    success = QDesktopServices.openUrl(url)

    if not success:
        QMessageBox.warning(
            parent,
            "Error",
            f"Could not open folder:\n{folder}",
            QMessageBox.Ok,
        )

    return success


def qcolor_to_rgba(qcolor: object) -> tuple:
    """
    Converts qcolor to rgba tuple

    :param qcolor: {QColor}
    :return: {tuple (int, int, int, int)} rgba
    """

    return (qcolor.red(), qcolor.green(), qcolor.blue(), qcolor.alpha())


def assign_cell_type_colors(type_id_type_name_dict: Dict[int, str],
                            setting_type_color_map: Dict[int, QColor],
                            setting_types_invisible: Optional[str] = None) -> Dict[int, cell_type_color_props]:
    """
    given mapping of type name to type id we use this information to populate cell type colors
    In case certain type is "seen for the first time" we use default colors to assign color to it

    :param type_id_type_name_dict: type it to type name mapping
    :param setting_type_color_map: TypeColorMap setting
    :param setting_types_invisible: Types3DInvisible setting
    :return:
    """
    types_invisible_dict = {}
    if setting_types_invisible:
        types_invisible = setting_types_invisible.replace(" ", "")
        types_invisible = types_invisible.split(",")
        if types_invisible:
            types_invisible_dict = {int(type_id): 1 for type_id in types_invisible}

    # Enforce invisible medium
    types_invisible_dict[0] = 1

    type_id_to_type_name_color_map = OrderedDict()
    if type_id_type_name_dict is not None and len(type_id_type_name_dict):
        for type_id, type_name in type_id_type_name_dict.items():
            try:
                color_from_setting = setting_type_color_map[type_id]
            except KeyError:
                try:
                    color_from_setting = QColor(default_cell_type_color_list[type_id])
                except IndexError:
                    color_from_setting = QColor('black')
            try:
                invisible = types_invisible_dict[type_id]
            except KeyError:
                invisible = False

            type_id_to_type_name_color_map[type_id] = cell_type_color_props(color_from_setting, type_name, invisible)

    else:
        # this happens before we start simulation
        for type_id, color in setting_type_color_map.items():
            try:
                invisible = types_invisible_dict[type_id]
            except KeyError:
                invisible = False

            type_id_to_type_name_color_map[type_id] = cell_type_color_props(color, '', invisible)

    return type_id_to_type_name_color_map
