"""
注册窗口（模态对话框）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from ui.styles import GLOBAL_STYLE, SECONDARY_BTN_STYLE
from utils.ui_helpers import make_eye_icon, toggle_password_visibility
from utils.password_utils import check_password_strength, is_weak_password


class RegisterWindow(QDialog):
    """注册窗口"""

    def __init__(self, user_service, parent=None):
        super().__init__(parent)
        self.user_service = user_service
        self.registered_username = ''
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("用户注册")
        self.setFixedSize(420, 500)
        self.setStyleSheet(GLOBAL_STYLE)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(40, 20, 40, 20)

        title = QLabel("用户注册")
        title.setProperty("cssClass", "subtitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(8)

        layout.addWidget(QLabel("用户名 *"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("2-50个字符")
        layout.addWidget(self.username_input)

        # 密码（眼睛图标内嵌切换）
        layout.addWidget(QLabel("密码 *"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("至少8位，含大小写字母+数字")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self._check_strength)
        self._icon_visible = make_eye_icon(True)
        self._icon_hidden = make_eye_icon(False)
        self._pwd1_action = QAction(self._icon_visible, "", self.password_input)
        self._pwd1_action.triggered.connect(lambda: self._toggle_pwd(self.password_input, self._pwd1_action))
        self.password_input.addAction(self._pwd1_action, QLineEdit.TrailingPosition)
        layout.addWidget(self.password_input)

        # 密码强度（条+文字并排）
        strength_row = QHBoxLayout()
        strength_row.setSpacing(8)
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setFixedHeight(12)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #E0E0E0; border-radius: 6px; background: #F5F5F5; }"
            "QProgressBar::chunk { border-radius: 5px; background: #BDBDBD; }"
        )
        strength_row.addWidget(self.strength_bar, 1)
        self.strength_label = QLabel("")
        self.strength_label.setStyleSheet("font-size: 11px; color: #999;")
        self.strength_label.setFixedWidth(120)
        strength_row.addWidget(self.strength_label)
        layout.addLayout(strength_row)

        # 确认密码
        layout.addWidget(QLabel("确认密码 *"))
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("请再次输入密码")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self._pwd2_action = QAction(self._icon_visible, "", self.confirm_input)
        self._pwd2_action.triggered.connect(lambda: self._toggle_pwd(self.confirm_input, self._pwd2_action))
        self.confirm_input.addAction(self._pwd2_action, QLineEdit.TrailingPosition)
        layout.addWidget(self.confirm_input)

        layout.addWidget(QLabel("邮箱（选填）"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("用于找回密码")
        layout.addWidget(self.email_input)

        layout.addSpacing(12)

        self.register_btn = QPushButton("注 册")
        self.register_btn.clicked.connect(self._on_register)
        layout.addWidget(self.register_btn)

        layout.addSpacing(10)

        self.cancel_btn = QPushButton("取 消")
        self.cancel_btn.setStyleSheet(SECONDARY_BTN_STYLE)
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)

        self.setLayout(layout)

    def _toggle_pwd(self, input_field, action):
        """切换密码显示/隐藏"""
        toggle_password_visibility(
            input_field, action,
            self._icon_visible, self._icon_hidden
        )

    def _check_strength(self, text: str):
        """检测密码强度"""
        score = 0
        if len(text) >= 8:
            score += 25
        if re.search(r'[a-z]', text) and re.search(r'[A-Z]', text):
            score += 25
        if re.search(r'\d', text):
            score += 25
        if re.search(r'[!@#$%^&*(),.?\":{}|<>_\-]', text):
            score += 25

        self.strength_bar.setValue(score)
        colors = ["#D32F2F", "#FF6F00", "#FBC02D", "#4CAF50"]
        labels = ["弱", "较弱", "中等", "强"]
        idx = min(score // 25, 3) if score > 0 else 0
        self.strength_bar.setStyleSheet(
            f"QProgressBar {{ border: 1px solid #E0E0E0; border-radius: 6px; background: #F5F5F5; }}"
            f"QProgressBar::chunk {{ border-radius: 5px; background: {colors[idx]}; }}"
        )
        self.strength_label.setText(labels[idx] if text else "")
        self.strength_label.setStyleSheet(f"font-size: 11px; color: {colors[idx]};")

    def _on_register(self):
        """处理注册"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        email = self.email_input.text().strip()

        if not username or not password or not confirm:
            QMessageBox.warning(self, "提示", "请填写所有必填字段")
            return

        if len(username) < 2:
            QMessageBox.warning(self, "提示", "用户名至少需要2个字符")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "提示", "密码至少需要8个字符")
            return

        if is_weak_password(password):
            QMessageBox.warning(
                self, "密码强度不足",
                "密码需包含以下至少2项：\n"
                "  • 大写字母 + 小写字母\n"
                "  • 数字\n"
                "  • 特殊符号（!@#$%等）"
            )
            return

        if password != confirm:
            QMessageBox.warning(self, "提示", "两次输入的密码不一致")
            return

        success, msg = self.user_service.register(username, password, email)
        if success:
            self.registered_username = username
            self.accept()
        else:
            QMessageBox.warning(self, "注册失败", msg)
