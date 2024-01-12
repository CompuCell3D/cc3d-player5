"""
Controls color schemes for Player by loading in CSS files.
"""
from pathlib import Path
import glob
import weakref

from cc3d.player5 import Configuration

BASE_STYLES_FNAME = "BaseStyles"

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
def _getStyleSheet(_themeName):
    global currentTheme
    if _themeName == currentTheme and currentStyleSheet:
        return currentStyleSheet
    else:
        themePath = Path(themeDir).joinpath(_themeName)
        themePath = themePath.with_suffix(".css")
        if Path.exists(themePath):
            currentTheme = _themeName
            with open(themePath, 'r') as themeFile:
                customStyles = themeFile.read().replace('\n', '')
                # Just a concatenation between stylesheets...
                # it is slow but effective.
                return _getBaseStylesheet() + customStyles
        else:
            print(type(_themeName))
            print('Could not find theme: ' + _themeName + ' in the styles directory.')
            return ""


"""
Prepares the given widget to automatically update when the stylesheet changes.
Additionally, this sets the widget's current style sheet according to 
the `ThemeName` set to `Configuration`.
This assumes that a .css file exists in the appropriate directory. 
"""
def subscribeToStylesheet(widget):
    global subscribers
    ref = weakref.ref(widget)
    subscribers.append(ref)
    
    widget.setStyleSheet(_getStyleSheet(Configuration.getSetting("ThemeName")))


"""
This method removes all garbage-collected references from `subscribers`.
It is not necessary. It just prevents `subscribers` from being full of `None`.
"""
def _cleanupSubscribers():
    global subscribers
    if len(subscribers) > 100: #arbitrary; makes this method fire only periodically
        toKeep = []
        for ref in subscribers:
            if ref():
                toKeep.append(ref)
        subscribers = toKeep


"""
Sets the current theme of all widgets subscribed to stylesheet changes.
"""
def publishStylesheet(themeName):
    _cleanupSubscribers()
    stylesheet = _getStyleSheet(themeName)
    for widget in subscribers:
        if widget():
            widget().setStyleSheet(stylesheet)