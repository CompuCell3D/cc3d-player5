"""
This class manages color schemes for Player by loading in CSS files.
"""
from pathlib import Path
import glob

BASE_STYLES_FNAME = "BaseStyles"


class StyleManager(object):

    def __init__(self):
        if len(Path(__file__).parents) <= 1:
            print('StyleManager error: Something is wrong with the source code directory')
        styleManagerPath = Path(__file__).parents[0]

        self.themeDir = styleManagerPath.joinpath('themes')

        if not Path.exists(self.themeDir):
            print('StyleManager error: Could not find the `themes` directory in', self.themeDir)

    def getThemeNames(self):
        theme_file_list = glob.glob(str(self.themeDir) + "/*.css")
        themeNames = []
        for themeFileName in theme_file_list:
            stem = Path(themeFileName).stem
            if stem != BASE_STYLES_FNAME:
                themeNames.append(stem)

        return themeNames


    def getBaseStylesheet(self):
        themePath = Path(self.themeDir).joinpath(BASE_STYLES_FNAME + ".css")
        if Path.exists(themePath):
            with open(themePath, 'r') as baseStylesFile:
                return baseStylesFile.read().replace('\n', '')
        else:
            print('Could not find the ' + BASE_STYLES_FNAME + '.css file.')
            return ""


    """
    Returns a combination of BaseStyles.css and the 
    given CSS file contents.
    :_themeName: the name of a .css file without its extension, such as "LightTheme"
    """
    def getStylesheet(self, _themeName):
        themePath = Path(self.themeDir).joinpath(_themeName)
        themePath = themePath.with_suffix(".css")
        if Path.exists(themePath):
            with open(themePath, 'r') as themeFile:
                customStyles = themeFile.read().replace('\n', '')
                # Just a concatenation between stylesheets...
                # it is slow but effective.
                return self.getBaseStylesheet() + customStyles
        else:
            print(type(_themeName))
            print('Could not find theme: ' + _themeName + ' in the styles directory.')
            return ""
