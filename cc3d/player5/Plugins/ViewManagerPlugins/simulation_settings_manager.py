import os
from pathlib import Path
from typing import Callable, Optional, Tuple

from PyQt5.QtWidgets import QMessageBox

import cc3d.core.DefaultSettingsData as settings_data
import cc3d.player5.Configuration as Configuration
from cc3d.player5.Plugins.ViewManagerPlugins.SimulationSettingsDialog import SimulationSettingsDialog


TITLE = "Manage Simulation Settings"


def simulation_settings_paths(simulation_file_name: str) -> Tuple[Optional[Path], Optional[Path]]:
    current_simulation_path = os.path.abspath(str(simulation_file_name)) if simulation_file_name else ''
    if not current_simulation_path or not os.path.isfile(current_simulation_path):
        return None, None

    settings_dir = Path(current_simulation_path).parent.joinpath("Simulation")
    return settings_dir.joinpath(settings_data.SETTINGS_FILE_NAME), settings_dir.joinpath("_custom_settings.xml")


def ensure_custom_settings_storage(sqlite_path: Path, xml_path: Path):
    if not Configuration.Configuration.myCustomSettingsPath:
        Configuration.load_or_create_simulation_settings(
            path=str(sqlite_path),
            path_xml=str(xml_path) if xml_path.is_file() else ''
        )


def close_custom_settings_storage_for_delete(sqlite_path: Path, xml_path: Path):
    custom_settings_path = str(sqlite_path)
    custom_settings_path_xml = str(xml_path)

    if Configuration.Configuration.myCustomSettingsPath == custom_settings_path:
        if Configuration.Configuration.myCustomSettings is not None:
            Configuration.Configuration.myCustomSettings.close()
        Configuration.Configuration.myCustomSettings = None
        Configuration.Configuration.myCustomSettingsPath = ''

    if Configuration.Configuration.myCustomSettingsPathXML == custom_settings_path_xml:
        Configuration.Configuration.myCustomSettingsPathXML = ''


class SimulationSettingsManager:
    def __init__(self, parent, simulation_file_name: str, save_windows_layout: Callable[[], None]):
        self.parent = parent
        self.simulation_file_name = simulation_file_name
        self.save_windows_layout = save_windows_layout

    @property
    def settings_paths(self):
        return simulation_settings_paths(self.simulation_file_name)

    def warn_no_active_project(self):
        QMessageBox.warning(
            self.parent,
            TITLE,
            "No active .cc3d project is loaded. Open a simulation first."
        )

    def show_dialog(self):
        sqlite_path, xml_path = self.settings_paths
        if sqlite_path is None:
            self.warn_no_active_project()
            return

        dlg = SimulationSettingsDialog(self.parent)
        dlg.set_settings_paths(sqlite_path=str(sqlite_path), xml_path=str(xml_path))
        dlg.exportSettingsButton.clicked.connect(lambda: self.export_settings(dlg))
        dlg.deleteSettingsButton.clicked.connect(lambda: self.delete_settings(dlg))
        dlg.exec_()

    def export_settings(self, dlg: SimulationSettingsDialog):
        sqlite_path, xml_path = self.settings_paths
        if sqlite_path is None:
            self.warn_no_active_project()
            return

        try:
            sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            ensure_custom_settings_storage(sqlite_path=sqlite_path, xml_path=xml_path)
            self.save_windows_layout()
            Configuration.writeAllSettings()
        except Exception as e:
            QMessageBox.warning(
                self.parent,
                TITLE,
                f"Could not save SQLite settings to:\n{sqlite_path}\n\n{e}"
            )
            return

        saved_xml_path = None
        xml_notice = None
        if dlg.xml_format_enabled():
            xml_saved, xml_notice = self.export_xml_settings(dlg=dlg, xml_path=xml_path)
            if xml_saved:
                saved_xml_path = str(xml_path)

        dlg.set_saved_status(sqlite_path=str(sqlite_path), xml_path=saved_xml_path, notice=xml_notice)

    def export_xml_settings(self, dlg: SimulationSettingsDialog, xml_path: Path) -> Tuple[bool, Optional[str]]:
        if xml_path.exists():
            ret = QMessageBox.question(
                self.parent,
                TITLE,
                f"XML settings already exist:\n{xml_path}\n\nOverwrite this file?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if ret == QMessageBox.Cancel:
                return False, "XML export canceled."
            if ret == QMessageBox.No:
                return False, "XML export skipped."

        try:
            Configuration.export_settings_to_xml(xml_file_path=str(xml_path), scope='custom')
        except Exception as e:
            QMessageBox.warning(
                self.parent,
                TITLE,
                f"Could not export XML settings to:\n{xml_path}\n\n{e}"
            )
            return False, "XML export failed."

        return True, None

    def delete_settings(self, dlg: SimulationSettingsDialog):
        sqlite_path, xml_path = self.settings_paths
        if sqlite_path is None:
            self.warn_no_active_project()
            return

        delete_paths = [sqlite_path]
        if dlg.xml_format_enabled():
            delete_paths.append(xml_path)

        delete_text = "\n".join(str(path) for path in delete_paths)
        ret = QMessageBox.question(
            self.parent,
            TITLE,
            f"Delete simulation settings?\n\n{delete_text}",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.No:
            return

        try:
            close_custom_settings_storage_for_delete(sqlite_path=sqlite_path, xml_path=xml_path)
            deleted_paths = []
            for path in delete_paths:
                if path.exists():
                    path.unlink()
                    deleted_paths.append(str(path))
        except Exception as e:
            QMessageBox.warning(
                self.parent,
                TITLE,
                f"Could not delete simulation settings.\n\n{e}"
            )
            return

        if deleted_paths:
            dlg.set_delete_status(deleted_paths)
        else:
            dlg.set_notice_status("No matching settings files were present.")
