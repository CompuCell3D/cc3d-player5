"""
Player5 CLI
"""

import sys
from cc3d import player5
from cc3d.player5.CMLParser import CMLParser
from cc3d.player5.UI.UserInterface import UserInterface
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from cc3d.player5.CQt.CQApplication import CQApplication
# setting debug information output
from cc3d.player5.Messaging import setDebugging

import cc3d
from cc3d.player5.styles.StyleManager import subscribe_to_style_sheet

setDebugging(0)

if sys.platform.lower().startswith('linux'):
    # On linux have to import rr early on to avoid
    # PyQt-related crash - appears to only affect VirtualBox Installs   
    # of linux
    try:
        import roadrunner
    except ImportError:
        print('Could not import roadrunner')
        pass

if sys.platform.startswith('win'):
    # this takes care of the need to distribute qwindows.dll with the qt5 application
    # it needs to be located in the directory <library_path>/platforms
    QCoreApplication.addLibraryPath("./bin/")

# installing message handler to suppress spurious qt messages
if sys.platform == 'darwin':
    import platform

    mac_ver = platform.mac_ver()
    mac_ver_float = float('.'.join(mac_ver[0].split('.')[:2]))
    if mac_ver_float == 10.11:

        def handler(msg_type, msg_log_context, msg_string=None):
            if msg_log_context.startswith('QCocoaView handleTabletEvent'):
                return
            print(msg_log_context)

            # looks like we do not need those in PyQt5 version
            # PyQt5.QtCore.qInstallMsgHandler(handler)

    elif mac_ver_float == 10.10:

        def handler(msg_type, msg_log_context, msg_string=None):
            # pass
            if msg_log_context.startswith('Qt: qfontForThemeFont:'):
                return
            print(msg_log_context)

            # looks like we do not need those in PyQt5 version
            # PyQt5.QtCore.qInstallMsgHandler(handler)


def main(argv=None):

    if argv is None:
        argv = []

    # if sys.platform.startswith('darwin'):
    #     PyQt5.QtCore.QCoreApplication.setAttribute(Qt.AA_DontUseNativeMenuBar)

    app = CQApplication(argv)
    subscribe_to_style_sheet(app)

    pixmap = QPixmap("icons/splash_angio.png")
    splash = QSplashScreen(pixmap)

    splash.show()

    if sys.platform.startswith('darwin'):
        splash.raise_()

    print(cc3d.get_formatted_version_info())

    base_message = f'{cc3d.get_version_info()}\n'

    first_message = base_message + "Loading User Interface ..."

    splash.showMessage(first_message, Qt.AlignLeft, Qt.white)

    second_message = base_message + "Loading CompuCell3D Python Modules..."

    splash.showMessage(second_message, Qt.AlignLeft, Qt.white)

    app.processEvents()

    cml_parser = CMLParser()
    cml_parser.parse_cml(argv)
    cml_args = cml_parser.cml_args

    main_window = UserInterface()

    # passing command line to the code
    main_window.setArgv(argv)

    # process reminder of the command line options
    if argv != "":
        main_window.viewmanager.set_cml_args(cml_args)
        main_window.viewmanager.process_command_line_options(cml_args)

    main_window.show()
    splash.finish(main_window)

    # we are making sure here that after all windows have been restored that
    # all actions' check state e.g. View->Console reflect what is being shown on the screen
    # this is especially important when global settings and simulation differ in what windows they show
    main_window.synchronizes_dock_windows_actions()

    main_window.raise_()

    error_code_local = app.exec_()

    print('EXITING WITH ERROR CODE=', error_code_local)
    return error_code_local


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
    sys.exit(1)


if __name__ == '__main__':
    # enable it during debugging in pycharm
    sys.excepthook = except_hook

    error_code = main(sys.argv[1:])

    # if error_code !=0 :
    #     print traceback.print_tb()

    # sys.excepthook = except_hook

    sys.exit(error_code)
