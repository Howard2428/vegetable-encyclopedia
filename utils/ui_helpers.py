"""
UI共享工具模块
提供多个UI窗口共用的图标绘制、密码可见性切换等功能。
"""

from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt


def make_eye_icon(visible: bool) -> QIcon:
    """绘制密码可见性切换用的眼睛图标（visible=True 睁眼 / False 闭眼）"""
    px = QPixmap(32, 32)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    if visible:
        p.setPen(QPen(QColor("#666"), 2))
        p.setBrush(QBrush(Qt.white))
        p.drawEllipse(6, 10, 20, 13)
        p.setBrush(QBrush(QColor("#666")))
        p.drawEllipse(14, 13, 6, 7)
    else:
        p.setPen(QPen(QColor("#666"), 2))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(6, 10, 20, 13)
        p.setPen(QPen(QColor("#D32F2F"), 2.5))
        p.drawLine(3, 3, 29, 29)
    p.end()
    return QIcon(px)


def toggle_password_visibility(input_field: QLineEdit,
                               action: QAction,
                               icon_visible: QIcon,
                               icon_hidden: QIcon) -> None:
    """切换密码输入框的显示/隐藏状态并更新图标"""
    if input_field.echoMode() == QLineEdit.Password:
        input_field.setEchoMode(QLineEdit.Normal)
        action.setIcon(icon_hidden)
    else:
        input_field.setEchoMode(QLineEdit.Password)
        action.setIcon(icon_visible)
