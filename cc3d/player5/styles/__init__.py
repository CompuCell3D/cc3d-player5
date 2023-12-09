tab_bar_style = """
* {
    color: white;
    background-color: rgb(37, 37, 37);
    font-family: Verdana;
}

QDialog { 
    background-color: rgb(17, 17, 17);
}

QPushButton {
    text-align: left;
    border: none;
    padding:  4px 12px 4px 12px;
    background-color: rgb(74, 74, 74);
    border-radius: 6px;
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

#line_1, #line_2, #line_3, #line_4 {
    background-color: rgb(104, 104, 104);
}

"""

