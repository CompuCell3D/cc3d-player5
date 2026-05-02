from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from cc3d.player5.Plugins.ViewManagerPlugins.ui_simulation_settings_dialog import Ui_SimulationSettingsDialog


class SimulationSettingsDialog(QDialog, Ui_SimulationSettingsDialog):
    def __init__(self, parent=None):
        super(SimulationSettingsDialog, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.setupUi(self)
        self.xmlFormatCheckBox.toggled.connect(self.set_xml_controls_enabled)
        self.set_xml_controls_enabled(self.xmlFormatCheckBox.isChecked())

    def set_settings_paths(self, sqlite_path: str, xml_path: str):
        self.sqliteLocationLineEdit.setText(sqlite_path)
        self.xmlLocationLineEdit.setText(xml_path)

    def xml_format_enabled(self) -> bool:
        return self.xmlFormatCheckBox.isChecked()

    def set_xml_controls_enabled(self, enabled: bool):
        self.xmlLocationLabel.setEnabled(enabled)
        self.xmlLocationLineEdit.setEnabled(enabled)

    def set_status(self, text: str):
        self.statusLabel.setText(text)
