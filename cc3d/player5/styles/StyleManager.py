"""
This class manages color schemes for Player.
"""
from PyQt5.QtGui import QColor

from .DOMUtils import DOMBase
# from cc3d.twedit5.twedit.utils.global_imports import *
# from cc3d.twedit5 import twedit
from cc3d.player5.styles import *
import os
from pathlib import Path
from xml.dom.minidom import parse, parseString
import glob


class ComponentStyle(DOMBase):

    def __init__(self, _name=''):
        DOMBase.__init__(self, _name='ComponentStyle')

        self.attrNameToTypeDict = {
                'target': (str, ''), 'fgColor': (str, '000000'), 'bgColor': (str, 'FF0000'),
                'fontName': (str, ''), 'fontStyle': (int, 0), 'fontSize': (int, -1)
        }

class Theme(object):

    def __init__(self, _name='GENERAL THEME'):

        self.name = _name

        self.themeFileName = ''

        # {name: style}
        self.globalStyle = {}

    def addGlobalStyle(self, _style):

        self.globalStyle[_style.target] = _style
        print("Set addGlobalStyle: ",_style.target,"...",_style)

    def getGlobalStyle(self, _name):
        try:
            return self.globalStyle[_name]
        except LookupError:
            return ComponentStyle()



class StyleManager(object):

    def __init__(self):

        self.themeDict = {}

        self.themeDir = os.path.join(os.path.dirname(__file__), 'themes')

    def getThemeNames(self):

        themesSorted = sorted(self.themeDict.keys())

        return themesSorted

    def readThemes(self):

        theme_file_list = glob.glob(self.themeDir + "/*.xml")

        for themeFileName in theme_file_list:
            print("themeFileName",themeFileName)
            core_theme_name, ext = os.path.splitext(os.path.basename(themeFileName))

            theme = Theme(core_theme_name)

            theme.themeFileName = themeFileName

            self.parseTheme(_theme=theme)
            self.themeDict[core_theme_name] = theme

    def parseTheme(self, _theme):

        dom = parse(_theme.themeFileName)

        qt_style_elems = dom.getElementsByTagName('QtStyles')
        for qtStyleElem in qt_style_elems:
            components_style_elems = qtStyleElem.getElementsByTagName('ComponentStyle')

            for componentStyleElem in components_style_elems:
                component_style = ComponentStyle()
                component_style.fromDOMElem(componentStyleElem)
                print("Parsed word_style",component_style)
                print("from",componentStyleElem)
                _theme.addGlobalStyle(component_style)

    def npStrToQColor(self, _str):

        r = int(_str[0:2], 16)

        g = int(_str[2:4], 16)

        b = int(_str[4:6], 16)

        try:
            return QColor(int(_str[0:2], 16), int(_str[2:4], 16), int(_str[4:6], 16))
        except ValueError:
            return None

    def npStrToSciColor(self, _str):

        try:
            return (int(_str[4:6], 16) << 16) + (int(_str[2:4], 16) << 8) + (int(_str[0:2], 16))
        except ValueError:
            return None

    def getStylesheet(self, _themeName):
        try:
            theme = self.themeDict[_themeName]
        except LookupError:
            print(type(_themeName))
            print('Could not find theme: ' + _themeName + ' in StyleManager')
            print('got these themes=', list(self.themeDict.keys()))
            return None

        print("theme.getGlobalStyle(QDialog)",theme.getGlobalStyle("QDialog"))
        print("theme.getGlobalStyle(QDialog).bgColor",theme.getGlobalStyle("QDialog").bgColor)

        return """
            * {
                font-family: Verdana;
            }
            
            QWidget {
                color: white;
                background-color: rgb(37, 37, 37);
            }
            
            QPushButton:enabled, QLineEdit:enabled, QSpinBox:enabled {
                background-color: rgb(64, 64, 64);
                color: rgb(255, 255, 255);
            }
            QPushButton:disabled, QLineEdit:disabled, QSpinBox:disabled {
                /*Make semi-transparent and grayed out*/
                background-color: rgba(255, 255, 255, 100);
                color: rgba(255, 255, 255, 150);
            }
            QPushButton:focus, QLineEdit:focus, QSpinBox:focus {
                background-color: rgb(17, 17, 17);
                color: white;
            }
            
            QDialog { 
                background-color: #"""+ theme.getGlobalStyle("QDialog").bgColor +""";
            }
            
            QDialog { 
                border: 10px solid red;
            }
            
            QPushButton {
                text-align: left;
                border: none;
                padding:  4px 12px 4px 12px;
                border-radius: 6px;
                background-color: rgb(74, 74, 74);
            }
            
            QSpinBox, QLineEdit {
                border-radius: 3px;
                border: 1px solid #AAAAAA;
            }
            
            QTabWidget::pane {
                background-color: rgb(62, 57, 57);
                border: 1px solid gray;
            }
            
            QTabBar::tab {
                background-color: rgb(54, 54, 54);
                border: 1px solid rgb(74, 74, 74);
                padding: 4px;
                border-radius: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: rgb(116, 195, 207);
                margin-bottom: -1px;
                margin-top: 1px;
            }
            
            /*
              All QLine instances must be written here since that tag is broken
            */
            #line_1, #line_2, #line_3, #line_4, #line_5, #line_6 {
                background-color: rgb(104, 104, 104);
            }
            
            """

