"""
Controls color schemes for Player by loading in CSS files.
"""
from pathlib import Path
import glob
import weakref

from cc3d.player5 import Configuration

DEFAULT_STYLE_FNAME = "DefaultTheme"

styleManagerPath = Path(__file__).parents[0]
themeDir = styleManagerPath.joinpath('themes')
currentTheme = None
currentStyleSheet = None
subscribers = []


def get_theme_names():
    """
    Returns a list of all `.css` file names and extensions 
    contained in the themes directory.
    """
    theme_file_list = glob.glob(str(themeDir) + "/*.css")
    themeNames = []
    for themeFileName in theme_file_list:
        stem = Path(themeFileName).stem
        themeNames.append(stem)

    return themeNames


def _get_style_sheet(_themeName):
    """
    Returns the current theme's CSS file contents.
    :_themeName: the name of a .css file without its extension, such as "LightTheme"
    """
    themePath = Path(themeDir).joinpath(_themeName)
    themePath = themePath.with_suffix(".css")
    if Path.exists(themePath):
        with open(themePath, 'r') as themeFile:
            customStyles = themeFile.read().replace('\n', '')
            return customStyles
    else:
        print(type(_themeName))
        print('Could not find theme: ' + _themeName + ' in the styles directory.')
        return ""


def subscribe_to_style_sheet(widget):
    """
    Prepares the given widget to automatically update when the stylesheet changes.
    Additionally, this sets the widget's current style sheet according to
    the `ThemeName` set to `Configuration`.
    This assumes that a .css file exists in the appropriate directory.
    """
    global subscribers
    ref = weakref.ref(widget)
    subscribers.append(ref)
    theme_content = _get_style_sheet(Configuration.getSetting("ThemeName"))
    if theme_content.strip():
        widget.setStyleSheet(theme_content)



def publish_style_sheet(themeName):
    """
    Sets the current theme of all widgets subscribed to stylesheet changes.
    """
    global subscribers
    stylesheet = _get_style_sheet(themeName)
    for widget in subscribers:
        if widget():
            widget().setStyleSheet(stylesheet)