from html import escape

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from cc3d.player5.Plugins.ViewManagerPlugins.ui_simulation_settings_dialog import Ui_SimulationSettingsDialog


class SimulationSettingsDialog(QDialog, Ui_SimulationSettingsDialog):
    STATUS_PANEL_STYLE = """
        QLabel#statusLabel {
            background-color: #f5f9ff;
            border: 1px solid #9bbce8;
            border-left: 4px solid #1f6feb;
            border-radius: 4px;
            color: #1f2937;
            padding: 8px 10px;
        }
    """

    def __init__(self, parent=None):
        super(SimulationSettingsDialog, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.setupUi(self)
        self.configure_status_label()
        self.xmlFormatCheckBox.toggled.connect(self.set_xml_controls_enabled)
        self.set_xml_controls_enabled(self.xmlFormatCheckBox.isChecked())

    def configure_status_label(self):
        self.statusLabel.setTextFormat(Qt.RichText)
        self.statusLabel.setWordWrap(True)
        self.statusLabel.setOpenExternalLinks(False)
        self.statusLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.statusLabel.setStyleSheet(self.STATUS_PANEL_STYLE)
        self.statusLabel.hide()

    def set_settings_paths(self, sqlite_path: str, xml_path: str):
        self.sqliteLocationLineEdit.setText(sqlite_path)
        self.xmlLocationLineEdit.setText(xml_path)

    def xml_format_enabled(self) -> bool:
        return self.xmlFormatCheckBox.isChecked()

    def set_xml_controls_enabled(self, enabled: bool):
        self.xmlLocationLabel.setEnabled(enabled)
        self.xmlLocationLineEdit.setEnabled(enabled)

    def set_status(self, text: str):
        self.set_status_html(escape(text).replace("\n", "<br>"))

    def set_status_html(self, html: str):
        if html:
            self.statusLabel.setText(html)
            self.statusLabel.show()
        else:
            self.statusLabel.clear()
            self.statusLabel.hide()

    def set_saved_status(self, sqlite_path: str, xml_path: str = None, notice: str = None):
        rows = [self.format_status_row("Saved SQLite settings", sqlite_path, "#137333")]
        if xml_path:
            rows.append(self.format_status_row("Saved XML settings", xml_path, "#137333"))
        if notice:
            rows.append(self.format_notice_row(notice))
        self.set_status_html("".join(rows))

    def set_delete_status(self, deleted_paths):
        rows = [self.format_status_row("Deleted", path, "#b42318") for path in deleted_paths]
        self.set_status_html("".join(rows))

    def set_notice_status(self, text: str):
        self.set_status_html(self.format_notice_row(text))

    @staticmethod
    def format_status_row(label: str, path: str, color: str) -> str:
        return (
            '<div style="margin-bottom: 6px;">'
            f'<div style="font-weight: 700; color: {color};">{escape(label)}:</div>'
            f'<div style="font-family: monospace; color: #111827;">{escape(str(path))}</div>'
            '</div>'
        )

    @staticmethod
    def format_notice_row(text: str) -> str:
        return f'<div><span style="font-weight: 600; color: #8a4b00;">{escape(text)}</span></div>'
