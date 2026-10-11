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
from PyQt5.QtWidgets import QMessageBox, QLabel, QTextEdit, QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QStyle
import html
import sys

cell_type_color_props = namedtuple('cell_type_color_props', 'color type_name invisible')



def get_monospace_font_stack():
    if sys.platform == "darwin":
        return "Menlo, Monaco, monospace"
    elif sys.platform.startswith("win"):
        return "Consolas, Courier New, monospace"
    else:
        return "DejaVu Sans Mono, Liberation Mono, monospace"


def _build_traceback_html(traceback_text: str) -> str:
    line_html = []

    for raw_line in traceback_text.splitlines():
        escaped_line = html.escape(raw_line)
        stripped_line = raw_line.strip()

        if raw_line.startswith("Traceback"):
            color = "#c7922b"
            font_weight = "700"
        elif stripped_line.startswith('File "'):
            color = "#4f8cc9"
            font_weight = "600"
        elif raw_line.startswith("    "):
            color = "#d8dee9"
            font_weight = "400"
        elif stripped_line and not raw_line.startswith(" "):
            color = "#ff8a80"
            font_weight = "700"
        else:
            color = "#d8dee9"
            font_weight = "400"

        line_html.append(
            f"<span style='color: {color}; font-weight: {font_weight}; white-space: pre-wrap;'>{escaped_line}</span>"
        )

    return "<br>".join(line_html) if line_html else (
        "<span style='color: #d8dee9; white-space: pre-wrap;'>No traceback available.</span>"
    )


class ErrorDetailsDialog(QDialog):
    def __init__(
        self,
        title: str,
        message: str,
        informative_text: str = "",
        detailed_text: str = "",
        parent=None,
    ):
        super().__init__(parent)

        self._compact_size = (900, 170)
        self._expanded_size = (900, 560)

        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(*self._compact_size)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 12)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        icon_label = QLabel(self)
        icon_pixmap = self.style().standardIcon(QStyle.SP_MessageBoxCritical).pixmap(32, 32)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        header_layout.addWidget(icon_label, 0, Qt.AlignVCenter)

        title_label = QLabel(f"<b>{message}</b>", self)
        title_label.setWordWrap(True)
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        title_label.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(title_label, 1, Qt.AlignVCenter)
        layout.addLayout(header_layout)

        if informative_text:
            info_label = QLabel(self)
            info_label.setWordWrap(True)
            info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            info_label.setStyleSheet(
                "QLabel {"
                "background: #fff8e1;"
                "border: 1px solid #e6cf8b;"
                "border-radius: 6px;"
                "padding: 6px 8px;"
                "color: #3a3122;"
                "}"
            )
            info_label.setText(
                f"<pre style='margin: 0; font-family: {get_monospace_font_stack()};'>"
                f"{html.escape(informative_text)}"
                f"</pre>"
            )
            layout.addWidget(info_label)

        self.details_edit = QTextEdit(self)
        self.details_edit.setReadOnly(True)
        self.details_edit.setAcceptRichText(True)
        self.details_edit.setStyleSheet(
            "QTextEdit {"
            "background: #1f2430;"
            "color: #d8dee9;"
            "border: 1px solid #394150;"
            "border-radius: 8px;"
            "padding: 8px;"
            "}"
        )
        self.details_edit.document().setDefaultStyleSheet(
            "body {"
            f"font-family: {get_monospace_font_stack()};"
            "font-size: 11pt;"
            "line-height: 1.35;"
            "white-space: pre-wrap;"
            "}"
        )
        self.details_edit.setHtml(
            "<body>"
            f"{_build_traceback_html(detailed_text)}"
            "</body>"
        )
        self.details_edit.setVisible(False)
        has_details = bool(detailed_text.strip())
        layout.addWidget(self.details_edit, 1)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok, parent=self)
        self.details_button = None
        if has_details:
            self.details_button = button_box.addButton("Show More", QDialogButtonBox.ActionRole)
            self.details_button.clicked.connect(self._toggle_details)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

    def _toggle_details(self):
        showing_details = self.details_edit.isVisible()
        self.details_edit.setVisible(not showing_details)

        if self.details_button is not None:
            self.details_button.setText("Show Less" if not showing_details else "Show More")

        self.resize(*(self._expanded_size if not showing_details else self._compact_size))


def show_exception_messagebox(
    title: str,
    message: str,
    exception: Exception,
    parent=None,
):
    tb_str = "".join(traceback.format_exception(
        type(exception), exception, exception.__traceback__)
    )
    dialog = ErrorDetailsDialog(
        title=title,
        message=message,
        informative_text=str(exception),
        detailed_text=tb_str,
        parent=parent,
    )
    dialog.exec_()


def show_text_messagebox(
    title: str,
    message: str,
    informative_text: str = "",
    detailed_text: str = "",
    parent=None,
):
    dialog = ErrorDetailsDialog(
        title=title,
        message=message,
        informative_text=informative_text,
        detailed_text=detailed_text,
        parent=parent,
    )
    dialog.exec_()


def show_formatted_error_messagebox(error_text: str, parent=None):
    error_text = error_text or ""
    lines = [line.strip() for line in error_text.splitlines() if line.strip()]
    informative_text = lines[0] if lines else "Unknown Player error"

    show_text_messagebox(
        title="Player Error",
        message="A simulation error occurred.",
        informative_text=informative_text,
        detailed_text=error_text,
        parent=parent,
    )


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
