"""
Controls color schemes for Player by loading in CSS files.
"""
from pathlib import Path
import glob
import weakref

from cc3d.player5 import Configuration

BASE_STYLES_FNAME = "BaseStyles"
DEFAULT_STYLE_FNAME = "DefaultTheme"

styleManagerPath = Path(__file__).parents[0]
themeDir = styleManagerPath.joinpath('themes')
currentTheme = None
currentStyleSheet = None
subscribers = []

"""
Returns a list of all `.css` file names and extensions 
contained in the themes directory.
"""
def getThemeNames():
    theme_file_list = glob.glob(str(themeDir) + "/*.css")
    themeNames = []
    for themeFileName in theme_file_list:
        stem = Path(themeFileName).stem
        if stem != BASE_STYLES_FNAME:
            themeNames.append(stem)

    return themeNames


def _getBaseStylesheet():
    themePath = Path(themeDir).joinpath(BASE_STYLES_FNAME + ".css")
    if Path.exists(themePath):
        with open(themePath, 'r') as baseStylesFile:
            return baseStylesFile.read().replace('\n', '')
    else:
        print('Could not find the ' + BASE_STYLES_FNAME + '.css file.')
        return ""

"""
Returns a combination of BaseStyles.css and the 
current theme's CSS file contents.
:_themeName: the name of a .css file without its extension, such as "LightTheme"
"""
# def _getStyleSheet(_themeName):
#     global currentTheme
#     if _themeName == currentTheme and currentStyleSheet:
#         return currentStyleSheet
#     else:
#         themePath = Path(themeDir).joinpath(_themeName)
#         themePath = themePath.with_suffix(".css")
#         if Path.exists(themePath):
#             currentTheme = _themeName
#             with open(themePath, 'r') as themeFile:
#                 customStyles = themeFile.read().replace('\n', '')
#                 # Just a concatenation between stylesheets...
#                 # it is slow but effective.
#
#                 if _themeName != DEFAULT_STYLE_FNAME:
#                     return _getBaseStylesheet() + customStyles
#                 else:
#                     return  customStyles
#         else:
#             print(type(_themeName))
#             print('Could not find theme: ' + _themeName + ' in the styles directory.')
#             return ""

def _getStyleSheet(_themeName):
    # global currentTheme
    # if _themeName == currentTheme and currentStyleSheet:
    #     return currentStyleSheet
    # else:
    themePath = Path(themeDir).joinpath(_themeName)
    themePath = themePath.with_suffix(".css")
    if Path.exists(themePath):
        currentTheme = _themeName
        with open(themePath, 'r') as themeFile:
            customStyles = themeFile.read().replace('\n', '')
            # Just a concatenation between stylesheets...
            # it is slow but effective.

            return customStyles
            if _themeName != DEFAULT_STYLE_FNAME:
                return _getBaseStylesheet() + customStyles
            else:
                return customStyles
    else:
        print(type(_themeName))
        print('Could not find theme: ' + _themeName + ' in the styles directory.')
        return ""



def subscribeToStylesheet(widget):
    """
    Prepares the given widget to automatically update when the stylesheet changes.
    Additionally, this sets the widget's current style sheet according to
    the `ThemeName` set to `Configuration`.
    This assumes that a .css file exists in the appropriate directory.
    """

    global subscribers
    ref = weakref.ref(widget)
    subscribers.append(ref)
    theme_content = _getStyleSheet(Configuration.getSetting("ThemeName"))
    if theme_content.strip():
        widget.setStyleSheet(theme_content)



def _cleanup_subscribers():
    """
    This method removes all garbage-collected references from `subscribers`.
    It is not necessary. It just prevents `subscribers` from being full of `None`.
    """
    global subscribers

    # arbitrary; makes this method fire only periodically
    if len(subscribers) > 100:
        to_keep = []
        for ref in subscribers:
            if ref():
                to_keep.append(ref)
        subscribers = to_keep



def publishStylesheet(themeName):
    """
    Sets the current theme of all widgets subscribed to stylesheet changes.
    """
    return
    _cleanup_subscribers()
    stylesheet = _getStyleSheet(themeName)
    for widget in subscribers:
        if widget():
            widget().setStyleSheet(stylesheet)