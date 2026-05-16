from html import escape

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


STATUS_PANEL_BACKGROUND = "#f5f9ff"
STATUS_PANEL_BORDER = "#9bbce8"
STATUS_PANEL_ACCENT = "#1f6feb"
STATUS_PANEL_TEXT = "#1f2937"
STATUS_PATH_TEXT = "#111827"
STATUS_SUCCESS = "#137333"
STATUS_DANGER = "#b42318"
STATUS_NOTICE = "#8a4b00"


def status_panel_style(label) -> str:
    selector = f"QLabel#{label.objectName()}" if label.objectName() else "QLabel"
    return f"""
        {selector} {{
            background-color: {STATUS_PANEL_BACKGROUND};
            border: 1px solid {STATUS_PANEL_BORDER};
            border-left: 4px solid {STATUS_PANEL_ACCENT};
            border-radius: 4px;
            color: {STATUS_PANEL_TEXT};
            padding: 8px 10px;
        }}
    """


def configure_status_label(label):
    label.setTextFormat(Qt.RichText)
    label.setWordWrap(True)
    label.setOpenExternalLinks(False)
    label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    label.setStyleSheet(status_panel_style(label))
    label.hide()


def set_status_html(label, html: str):
    if html:
        label.setText(html)
        label.show()
    else:
        label.clear()
        label.hide()


def set_status_text(label, text: str):
    set_status_html(label, escape(text).replace("\n", "<br>"))


def set_status_message(label, text: str, color=STATUS_PANEL_TEXT, font_weight=600):
    if not text:
        set_status_html(label, "")
        return
    set_status_html(label, format_message(text=text, color=color, font_weight=font_weight))


def set_notice_status(label, text: str):
    set_status_html(label, format_notice_row(text))


def format_status_row(label: str, value: str, color: str) -> str:
    return (
        '<div style="margin-bottom: 6px;">'
        f'<div style="font-weight: 700; color: {color};">{escape(label)}:</div>'
        f'<div style="font-family: monospace; color: {STATUS_PATH_TEXT};">{escape(str(value))}</div>'
        '</div>'
    )


def format_notice_row(text: str) -> str:
    return f'<div><span style="font-weight: 600; color: {STATUS_NOTICE};">{escape(text)}</span></div>'


def format_message(text: str, color=STATUS_PANEL_TEXT, font_weight=600) -> str:
    css_color = css_color_name(color)
    return f'<span style="color: {css_color}; font-weight: {font_weight};">{escape(text)}</span>'


def css_color_name(color) -> str:
    qcolor = color if isinstance(color, QColor) else QColor(color)
    if not qcolor.isValid():
        print(f"WARNING: Invalid color '{color}', falling back to black")
        qcolor = QColor("black")
    return qcolor.name()
