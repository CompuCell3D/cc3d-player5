from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from cc3d.player5.Plugins.ViewManagerPlugins.status_label_utils import (
    STATUS_DANGER,
    STATUS_SUCCESS,
    configure_status_label as configure_status_label_widget,
    format_notice_row,
    format_status_row,
    set_notice_status as set_notice_status_widget,
    set_status_html as set_status_html_widget,
    set_status_text as set_status_text_widget,
)
from cc3d.player5.Plugins.ViewManagerPlugins.ui_simulation_settings_dialog import Ui_SimulationSettingsDialog


class SimulationSettingsDialog(QDialog, Ui_SimulationSettingsDialog):
    def __init__(self, parent=None):
        super(SimulationSettingsDialog, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.setupUi(self)
        self.configure_status_label()
        self.xmlFormatCheckBox.toggled.connect(self.set_xml_controls_enabled)
        self.set_xml_controls_enabled(self.xmlFormatCheckBox.isChecked())

    def configure_status_label(self):
        configure_status_label_widget(self.statusLabel)

    def set_settings_paths(self, sqlite_path: str, xml_path: str):
        self.sqliteLocationLineEdit.setText(sqlite_path)
        self.xmlLocationLineEdit.setText(xml_path)

    def xml_format_enabled(self) -> bool:
        return self.xmlFormatCheckBox.isChecked()

    def set_xml_controls_enabled(self, enabled: bool):
        self.xmlLocationLabel.setEnabled(enabled)
        self.xmlLocationLineEdit.setEnabled(enabled)

    def set_status(self, text: str):
        set_status_text_widget(self.statusLabel, text)

    def set_status_html(self, html: str):
        set_status_html_widget(self.statusLabel, html)

    def set_saved_status(self, sqlite_path: str, xml_path: str = None, notice: str = None):
        rows = [format_status_row("Saved SQLite settings", sqlite_path, STATUS_SUCCESS)]
        if xml_path:
            rows.append(format_status_row("Saved XML settings", xml_path, STATUS_SUCCESS))
        if notice:
            rows.append(format_notice_row(notice))
        self.set_status_html("".join(rows))

    def set_delete_status(self, deleted_paths):
        rows = [format_status_row("Deleted", path, STATUS_DANGER) for path in deleted_paths]
        self.set_status_html("".join(rows))

    def set_notice_status(self, text: str):
        set_notice_status_widget(self.statusLabel, text)
