# -*- coding: utf-8 -*-
import os
import sys
from os.path import join, dirname
import cc3d.player5.Configuration as Configuration
from cc3d.core.GraphicsUtils.ScreenshotData import ScreenshotData
from cc3d.core.GraphicsUtils.ScreenshotManagerCore import ScreenshotManagerCore
from cc3d.core.GraphicsOffScreen.GenericDrawer import GenericDrawer
from weakref import ref
from cc3d.CompuCellSetup import persistent_globals
from cc3d.core.utils import mkdir_p
from cc3d import CompuCellSetup
from PyQt5.QtWidgets import *
from typing import Optional
from typing import List


class ScreenshotManager(ScreenshotManagerCore):
    def __init__(self, _tabViewWidget):
        ScreenshotManagerCore.__init__(self)

        self.tabViewWidget = ref(_tabViewWidget)
        tvw = self.tabViewWidget()

        self.basicSimulationData = tvw.basicSimulationData
        self.basicSimulationData = tvw.basicSimulationData
        self.screenshot_number_of_digits = len(str(self.basicSimulationData.numberOfSteps))

        # we limit max number of screenshots to discourage users from using screenshots as their main analysis tool
        self.maxNumberOfScreenshots = 100

        self.screenshotGraphicsWidget = None

        try:
            boundary_strategy = persistent_globals.simulator.getBoundaryStrategy()
        except AttributeError:
            boundary_strategy = None

        self.gd = GenericDrawer(boundary_strategy=boundary_strategy)
        self.gd.set_field_extractor(field_extractor=tvw.fieldExtractor)

    def cleanup(self):
        # have to do cleanup to ensure some of the memory intensive resources e.g.
        # self.screenshotGraphicsWidget get deallocated
        if self.screenshotGraphicsWidget:
            # print("JUST BEFORE CLOSING self.screenshotGraphicsWidget")
            # this close and assignment do not do much for the non-mdi layout
            self.screenshotGraphicsWidget.close()
            self.screenshotGraphicsWidget = None
        self.tabViewWidget = None
        self.basicSimulationData = None

    def safe_write_screenshot_description_file(self, out_fname):
        """
        writes screenshot descr file in a safe mode. any problems are reported via warning
        :param out_fname: {str}
        :return: None
        """
        mkdir_p(dirname(out_fname))
        self.write_screenshot_description_file(out_fname)

    def serialize_screenshot_data(self):
        """
        Method called immediately after we add new screenshot via camera button. It serializes all screenshots data
        for future reference/reuse
        :return: None
        """
        persistent_globals = CompuCellSetup.persistent_globals

        out_dir_name = persistent_globals.output_directory
        sim_fname = persistent_globals.simulation_file_name

        out_fname = join(out_dir_name, "screenshot_data", "screenshots.json")
        out_fname_in_sim_dir = join(dirname(sim_fname), "screenshot_data", "screenshots.json")

        # writing in the simulation output dir
        self.safe_write_screenshot_description_file(out_fname)

        # writing in the original simulation location
        self.safe_write_screenshot_description_file(out_fname_in_sim_dir)

    def store_gui_vis_config(self, scrData):
        """
        Stores visualization settings such as cell borders, on/or cell on/off etc...

        :param scrData: {instance of ScreenshotDescriptionData}
        :return: None
        """

        tvw = self.tabViewWidget()
        if tvw:
            tvw.update_active_window_vis_flags(self.screenshotGraphicsWidget)

        scrData.cell_borders_on = tvw.border_act.isChecked()
        scrData.cells_on = tvw.cells_act.isChecked()
        scrData.cluster_borders_on = tvw.cluster_border_act.isChecked()
        scrData.cell_glyphs_on = tvw.cell_glyphs_act.isChecked()
        scrData.fpp_links_on = tvw.fpp_links_act.isChecked()
        scrData.lattice_axes_on = Configuration.getSetting("ShowHorizontalAxesLabels") or Configuration.getSetting(
            "ShowVerticalAxesLabels"
        )
        scrData.lattice_axes_labels_on = Configuration.getSetting("ShowAxes")
        scrData.bounding_box_on = Configuration.getSetting("BoundingBoxOn")

        invisible_types = Configuration.getSetting("Types3DInvisible")
        invisible_types = invisible_types.strip()

        if invisible_types:
            scrData.invisible_types = list([int(x) for x in invisible_types.split(",")])
            if 0 not in scrData.invisible_types:
                scrData.invisible_types = [0] + scrData.invisible_types

        else:
            scrData.invisible_types = [0]

    #
    def add_2d_screenshot(self, _plotName, _plotType, _projection, _projectionPosition, _camera, metadata=None):
        """
        Adds 2D screenshot configuration . Called from GraphicsFrameWidget
        :param _plotName:
        :param _plotType:
        :param _projection:
        :param _projectionPosition:
        :param _camera:
        :param metadata:
        :return:
        """

        scr_data = ScreenshotData()
        scr_data.spaceDimension = "2D"
        scr_data.plotData = (_plotName, _plotType)

        scr_data.projection = _projection
        scr_data.projectionPosition = int(_projectionPosition)

        self.update_screenshot_container(scr_data=scr_data, _camera=_camera, metadata=metadata)

    def add_3d_screenshot(self, _plotName, _plotType, _camera, metadata=None):
        """
        Adds 3D screenshot configuration . Called from GraphicsFrameWidget
        :param _plotName:
        :param _plotType:
        :param _camera:
        :param metadata:
        :return:
        """
        scr_data = ScreenshotData()
        scr_data.spaceDimension = "3D"
        scr_data.plotData = (_plotName, _plotType)
        self.update_screenshot_container(scr_data=scr_data, _camera=_camera, metadata=metadata)

    def update_screenshot_container(
        self, scr_data: ScreenshotData, _camera: object, metadata: Optional[dict] = None
    ) -> None:
        """
        updates screenshot data based on requested configuration. Users will have a chance to approve overwriting
        of existing screenshot configuration
        :param scr_data:
        :param _camera:
        :param metadata:
        :return:
        """

        x_size = Configuration.getSetting("Screenshot_X")
        y_size = Configuration.getSetting("Screenshot_Y")

        (scr_name, scr_core_name) = self.produce_screenshot_name(scr_data)

        scr_data = self.fill_in_screenshot_data_details(scr_data=scr_data, _camera=_camera, metadata=metadata)

        # if self.ok_to_add_screenshot(scr_name=scr_name, camera=_camera):
        if self.ok_to_add_screenshot_detailed(scr_data=scr_data):

            self.screenshot_config_counter += 1
            screenshot_uid = (f"{scr_name}{self.screenshot_config_counter_separator}"
                              f"{str(self.screenshot_config_counter).zfill(self.padding)}")

            # on linux there is a problem with X-server/Qt/QVTK implementation and calling
            # resize right after additional QVTK
            # is created causes segfault so possible "solution" is to do resize right before taking screenshot.
            # It causes flicker but does not cause segfault
            # User should NOT close or minimize this "empty" window (on Linux anyway).
            self.screenshotDataDict[screenshot_uid] = scr_data

        # serializing all screenshots
        self.serialize_screenshot_data()

    def fill_in_screenshot_data_details(
        self, scr_data: ScreenshotData, _camera: object, metadata: Optional[dict] = None
    ) -> ScreenshotData:
        """
        Populates screenshot data content
        :param metadata:
        :param _camera:
        :param scr_data:
        :return:
        """
        x_size = Configuration.getSetting("Screenshot_X")
        y_size = Configuration.getSetting("Screenshot_Y")

        (scr_name, scr_core_name) = self.produce_screenshot_name(scr_data)

        scr_data.screenshotName = scr_name

        scr_data.screenshotCoreName = scr_core_name
        scr_data.screenshotGraphicsWidget = self.screenshotGraphicsWidget
        scr_data.cell_shell_optimization = Configuration.getSetting("CellShellOptimization")

        scr_data.win_width = x_size
        scr_data.win_height = y_size

        if metadata is not None:
            scr_data.metadata = metadata

        tvw = self.tabViewWidget()
        if tvw:
            tvw.update_active_window_vis_flags(self.screenshotGraphicsWidget)

        self.store_gui_vis_config(scrData=scr_data)

        scr_data.extractCameraInfo(_camera)

        return scr_data

    def ok_to_add_screenshot_detailed(self, scr_data: ScreenshotData) -> bool:

        ok_to_add_screenshot = True
        for scr_name_stored, scr_data_stored in self.screenshotDataDict.items():
            differences = self.compare_dictionaries(
                dict1=scr_data.to_json_simulate_file_readout(),
                dict2=scr_data_stored.to_json_simulate_file_readout(),
                ignore_keys=["actual_screenshot", "screenshotName"],
            )

            if not differences:

                ret = QMessageBox.warning(
                    self.tabViewWidget(),
                    "Screenshot Already Exists",
                    "Screenshot with identical settings exists in <br/><b>screenshot_data/screenshots.json</b><br/>"
                    "Would you like to add with different screenshot name or discard it (recommended) ",
                    QMessageBox.No | QMessageBox.Yes,
                )

                if ret == QMessageBox.No:
                    ok_to_add_screenshot = False


        if ok_to_add_screenshot:
            # before we accept new screenshot we check if max number of screenshots has been reached
            if len(self.screenshotDataDict) >= self.maxNumberOfScreenshots:
                ret = QMessageBox.information(
                    self.tabViewWidget(),
                    "Max Number oF screenshots Has Been reached",
                    "Maximum number of screenshots has been reached. You may want to save VTK simulation "
                    "snapshots "
                    "and replay them in player after simulation is done to take additional screenshot configurations",
                    QMessageBox.Ok,
                )
                ok_to_add_screenshot = False

        return ok_to_add_screenshot

    def compare_dictionaries(self, dict1, dict2, path="", ignore_keys: Optional[List[str]] = None):
        """
        Compare two dictionaries and return a dictionary detailing the differences.

        Parameters:
        - dict1: The first dictionary to compare.
        - dict2: The second dictionary to compare.
        - path: The current path (used for nested dictionaries).

        Returns:
        A dictionary detailing the differences.
        """
        differences = {}

        key_union = set(dict1.keys() | dict2.keys())
        if ignore_keys is not None:
            key_union.difference_update(set(ignore_keys))
        # for key in dict1.keys() | dict2.keys():

        for key in key_union:

            new_path = f"{path}/{key}" if path else key

            if key in dict1 and key not in dict2:
                differences[new_path] = ("Only in dict1", dict1[key])
            elif key in dict2 and key not in dict1:
                differences[new_path] = ("Only in dict2", dict2[key])
            else:
                if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    nested_diff = self.compare_dictionaries(dict1[key], dict2[key], new_path, ignore_keys=ignore_keys)
                    if nested_diff:
                        differences.update(nested_diff)
                elif isinstance(dict1[key], (list, tuple)) and isinstance(dict2[key], (list, tuple)):
                    if tuple(dict1[key]) != tuple(dict2[key]):
                        differences[new_path] = (dict1[key], dict2[key])
                else:
                    if dict1[key] != dict2[key]:
                        differences[new_path] = (dict1[key], dict2[key])

        return differences

    def get_basic_simulation_data(self):
        """
        Returns an instance of BasicSimulationData
        :return: {BasicSimulationData}
        """
        tvw = self.tabViewWidget()
        bsd = tvw.basicSimulationData
        return bsd

    def output_screenshots_impl(self, mcs: int, screenshot_label_list: list):
        """
        implementation function ofr taking screenshots
        :param mcs:
        :param screenshot_label_list:
        :return
        """
        if self.output_error_flag:
            return

        bsd = self.get_basic_simulation_data()

        screenshot_directory_name = self.get_screenshot_dir_name()

        mcs_formatted_number = str(mcs).zfill(self.screenshot_number_of_digits)

        for i, screenshot_name in enumerate(screenshot_label_list):
            screenshot_data = self.screenshotDataDict[screenshot_name]
            # we are inserting a flag into scene metadata that informs the rest
            # of the visualization pipeline that we are dealing with actual screenshop
            # and if so we will use e.g. colors from screenshot description file, and not from settings
            screenshot_data.metadata["actual_screenshot"] = True

            if not screenshot_name:
                screenshot_name = "screenshot_" + str(i)

            screenshot_dir = os.path.join(screenshot_directory_name, screenshot_name)

            # will create screenshot directory if directory does not exist
            if not os.path.isdir(screenshot_dir):
                mkdir_p(screenshot_dir)

            screenshot_fname = os.path.join(screenshot_dir, screenshot_name + "_" + mcs_formatted_number + ".png")

            self.gd.clear_display()
            self.gd.draw(screenshot_data=screenshot_data, bsd=bsd, screenshot_name=screenshot_name)
            self.gd.output_screenshot(
                screenshot_fname=screenshot_fname, file_format="png", screenshot_data=screenshot_data
            )
