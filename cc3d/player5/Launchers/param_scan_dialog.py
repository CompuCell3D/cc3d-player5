# -*- coding: utf-8 -*-
import os
from cc3d import CompuCellSetup
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from os.path import expanduser, join
from os import environ
import sys
from pathlib import Path

import cc3d.player5.Configuration as Configuration


from . import ui_param_scan_dialog

MAC = "qt_mac_set_native_menubar" in dir()

MODULENAME = '------- ConfigurationDialog.py: '


class ParamScanDialog(QDialog, ui_param_scan_dialog.Ui_ParamScanDialog):

    def __init__(self, parent=None, name=None, modal=False):
        QDialog.__init__(self, parent)
        self.setModal(modal)

        self.setupUi(self)  # in ui_configurationdlg.Ui_CC3DPrefs

        self.browse_output_dir_PB.clicked.connect(self.select_output_dir)
        self.install_dir_browse_PB.clicked.connect(self.select_cc3d_install_dir)
        self.browse_simulation_PB.clicked.connect(self.select_simulation)
        self.update_cml_PB.clicked.connect(self.update_cml)


    def select_output_dir(self):

        current_dir = self.output_dir_LE.text()
        if current_dir.strip() != '':
            default_dir = current_dir
        else:
            default_dir = join(expanduser('~'), 'CC3DWorkspace')

        output_dir = QFileDialog.getExistingDirectory(
            self,
            QApplication.translate('ViewManager', "Parameter Scan Output Directory"),
            default_dir,
        )

        self.output_dir_LE.setText(output_dir)

    def select_cc3d_install_dir(self):

        current_dir = self.install_dir_LE.text()
        if current_dir.strip() != '':
            default_dir = current_dir
        else:
            default_dir = join(expanduser('~'), 'Downloads')

        cc3d_install_dir = QFileDialog.getExistingDirectory(
            self,
            QApplication.translate('ViewManager', "CC3D Installation Directory"),
            default_dir,
        )

        self.install_dir_LE.setText(cc3d_install_dir)

    def select_simulation(self):

        current_dir = self.install_dir_LE.text()
        if current_dir.strip() != '':
            default_dir = str(Path(current_dir).joinpath('Demos'))
        else:
            default_dir = join(expanduser('~'), 'Downloads')

        filter_ext = "CC3D Parameter Scan Simulation  (*.cc3d )"

        cc3d_simulation_tuple = QFileDialog.getOpenFileName(
            self,
            QApplication.translate('Parameter Scan', "CC3D Parameter Scan Simulation"),
            default_dir,
            filter_ext
        )
        cc3d_simulation = os.path.abspath(str(cc3d_simulation_tuple[0]))

        if os.path.splitext(cc3d_simulation)[1] == '.cc3d':
            self.param_scan_simulation_LE.setText(cc3d_simulation)

    def get_cml_list(self):
        """
        Returns CML for PS as a list
        :return:
        """

        python_exe = f'{sys.executable}'
        cml_list = [python_exe, '-m', 'cc3d.core.param_scan.parameter_scan_run']

        if python_exe.find(' ') >= 0:

            raise RuntimeError ('python executable script is installed in the folder that contains spaces. In current'
                                'version we require that installation of CC3D should be into a folder without spaces if'
                                'you want to run parameter scan')



        cml_list.append(f'--input="{self.param_scan_simulation_LE.text()}"')

        cml_list.append(f'--output-dir="{self.output_dir_LE.text()}"')

        cml_list.append(f'--install-dir="{self.install_dir_LE.text()}"')

        if self.output_snapshot_CB.isChecked():
            cml_list.append(f'--output-frequency={self.output_freq_SB.value()}')

        if self.output_screenshot_CB.isChecked():
            cml_list.append(f'--screenshot-output-frequency={self.screenshot_freq_CB.value()}')

        if self.gui_CB.isChecked():
            cml_list.append('--gui')

        return cml_list

    def update_cml(self):
        """

        :return:
        """
        try:
            cml_list = self.get_cml_list()
        except RuntimeError:

            self.cml_PTE.setPlainText('Could not generate command line. Most likely PREFIX_CC3D env var was not set')
            self.run_PB.setEnabled(False)
            return

        cml_str = ' '.join(cml_list)

        cml_str += '\n\n\nCopy above command , paste it into terminal and run. Or run directly by pressing "Run" button'

        self.cml_PTE.setPlainText(cml_str)

        self.run_PB.setEnabled(True)
