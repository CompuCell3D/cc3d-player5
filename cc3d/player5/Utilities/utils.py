# From core; do not remove unless you're looking for trouble, or making Player-specific implementations!
from cc3d.core.GraphicsUtils.utils import *
from cc3d.player5.UI.cell_type_colors import default_cell_type_color_list
from collections import namedtuple, OrderedDict
from typing import Dict, Optional
from PyQt5.QtGui import QColor


cell_type_color_props = namedtuple('cell_type_color_props', 'color type_name invisible')


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
