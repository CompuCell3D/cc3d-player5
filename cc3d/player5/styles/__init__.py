tab_bar_style = """
* {
    color: white;
    background-color: rgb(37, 37, 37);
    font-family: Verdana;
}

QDialog { 
    background-color: rgb(37, 37, 37);
}

QPushButton {
    text-align: left;
    border-left: none;
    border-right: none;
    border-top: none;
    border-bottom: 4px solid red;
    padding:  4px 12px 4px 12px;
    background-color: rgb(74, 74, 74);
    border-radius: 6px;
}

QPushButton:active {
    border-bottom: none;
}

QSpinBox, QLineEdit {
    border-radius: 3px;
    border: 1px solid #AAAAAA;
    background-color: rgba(0,0,0,0);
}

QSpinBox:focus, QLineEdit:focus {
    background-color: rgb(74, 74, 74);
}

QTabWidget::pane {
    /*background-color: rgb(64, 64, 64);*/
    background-color: rgb(124, 124, 124);
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

#line_4, #line_5, #line_3 {
    background-color: rgb(104, 104, 104);
}
"""

