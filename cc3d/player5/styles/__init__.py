tab_bar_style = """
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
    background-color: rgb(17, 17, 17);
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

# LIGHT_THEME = "light"
# DARK_THEME = "dark"

# #LT = Light Theme
# #DT = Dark Theme
# LT_COLOR = "white"

# def getStylesheet(chosenTheme):
#     if chosenTheme == LIGHT_THEME:
#
#     elif chosenTheme == DARK_THEME:
#         return """
#         * {
#             font-family: Verdana;
#         }
#
#         QWidget {
#             color: white;
#             background-color: rgb(37, 37, 37);
#         }
#
#         QPushButton:enabled, QLineEdit:enabled, QSpinBox:enabled {
#             background-color: rgb(64, 64, 64);
#             color: rgb(255, 255, 255);
#         }
#         QPushButton:disabled, QLineEdit:disabled, QSpinBox:disabled {
#             /*Make semi-transparent and grayed out*/
#             background-color: rgba(255, 255, 255, 100);
#             color: rgba(255, 255, 255, 150);
#         }
#         QPushButton:focus, QLineEdit:focus, QSpinBox:focus {
#             background-color: rgb(17, 17, 17);
#             color: white;
#         }
#
#         QDialog {
#             background-color: rgb(17, 17, 17);
#         }
#
#         QPushButton {
#             text-align: left;
#             border: none;
#             padding:  4px 12px 4px 12px;
#             border-radius: 6px;
#             background-color: rgb(74, 74, 74);
#         }
#
#         QSpinBox, QLineEdit {
#             border-radius: 3px;
#             border: 1px solid #AAAAAA;
#         }
#
#         QTabWidget::pane {
#             background-color: rgb(62, 57, 57);
#             border: 1px solid gray;
#         }
#
#         QTabBar::tab {
#             background-color: rgb(54, 54, 54);
#             border: 1px solid rgb(74, 74, 74);
#             padding: 4px;
#             border-radius: 2px;
#         }
#
#         QTabBar::tab:selected {
#             background-color: rgb(116, 195, 207);
#             margin-bottom: -1px;
#             margin-top: 1px;
#         }
#
#         /*
#           All QLine instances must be written here since that tag is broken
#         */
#         #line_1, #line_2, #line_3, #line_4, #line_5, #line_6 {
#             background-color: rgb(104, 104, 104);
#         }
#
#         """
#     else:
#         print(f"Invalid theme selected `{chosenTheme}`")
#         return ""
