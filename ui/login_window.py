"""
登录窗口（模态对话框）
"""

from ui.styles import GLOBAL_STYLE, SECONDARY_BTN_STYLE, LINK_BTN_STYLE
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QWidget
)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui_helpers import make_eye_icon, toggle_password_visibility
from utils.password_utils import is_weak_password


class LoginWindow(QDialog):
    """登录窗口"""

    def __init__(self, user_service, parent=None):
        super().__init__(parent)
        self.user_service = user_service
        self.login_success = False
        self.skip_mode = False      # True=访客浏览, False=X关闭退出
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("用户登录")
        self.setFixedSize(420, 420)
        self.setStyleSheet(GLOBAL_STYLE)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(40, 25, 40, 25)

        title = QLabel("🥬 蔬菜百科与推荐系统")
        title.setProperty("cssClass", "title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("用户登录")
        subtitle.setProperty("cssClass", "subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        layout.addWidget(QLabel("用户名"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        layout.addWidget(self.username_input)

        # 密码（眼睛图标内嵌切换）
        layout.addWidget(QLabel("密码"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._on_login)
        self._pwd_icon_visible = make_eye_icon(True)
        self._pwd_icon_hidden = make_eye_icon(False)
        self._pwd_action = QAction(
            self._pwd_icon_visible, "", self.password_input)
        self._pwd_action.triggered.connect(self._toggle_password)
        self.password_input.addAction(
            self._pwd_action, QLineEdit.TrailingPosition)
        layout.addWidget(self.password_input)

        layout.addSpacing(5)

        # 登录 + 注册按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.login_btn = QPushButton("登 录")
        self.login_btn.clicked.connect(self._on_login)
        btn_layout.addWidget(self.login_btn)

        self.register_btn = QPushButton("注 册")
        self.register_btn.setStyleSheet(SECONDARY_BTN_STYLE)
        self.register_btn.clicked.connect(self._on_register)
        btn_layout.addWidget(self.register_btn)

        layout.addLayout(btn_layout)

        # 跳过登录（访客浏览）
        skip_btn = QPushButton("跳过，以访客身份浏览")
        skip_btn.setStyleSheet(LINK_BTN_STYLE)
        skip_btn.clicked.connect(self._on_skip)
        layout.addWidget(skip_btn)

        layout.addStretch()

        hint = QLabel("测试账号：test / Test1234\n管理员：admin / Admin1234")
        hint.setStyleSheet("color: #999; font-size: 12px;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        self.setLayout(layout)

    def _on_login(self):
        """处理登录（弱密码登录后提醒修改）"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "提示", "请输入用户名和密码")
            return

        success, msg = self.user_service.login(username, password)
        if success:
            self.login_success = True
            if is_weak_password(password):
                reply = QMessageBox.question(
                    self, "安全提醒",
                    "当前密码安全等级过低，建议修改密码以确保账户安全。\n是否现在修改密码？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self._show_change_password_dialog()
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", msg)

    def _show_change_password_dialog(self):
        """弹出修改密码对话框"""
        dlg = QDialog(self)
        dlg.setWindowTitle("修改密码")
        dlg.setFixedSize(400, 280)
        dlg.setStyleSheet(GLOBAL_STYLE)
        dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 20, 25, 20)

        layout.addWidget(QLabel("新密码（至少8位，含大小写+数字）："))

        new_input = QLineEdit()
        new_input.setPlaceholderText("请输入新密码")
        new_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(new_input)

        cfm_input = QLineEdit()
        cfm_input.setPlaceholderText("请再次输入新密码")
        cfm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(cfm_input)

        hint = QLabel("密码需包含大写字母+小写字母 和 数字")
        hint.setStyleSheet("color: #999; font-size: 11px;")
        layout.addWidget(hint)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确认修改")
        ok_btn.clicked.connect(dlg.accept)
        btn_layout.addWidget(ok_btn)
        skip_btn = QPushButton("暂不修改")
        skip_btn.setStyleSheet(SECONDARY_BTN_STYLE)
        skip_btn.clicked.connect(dlg.reject)
        btn_layout.addWidget(skip_btn)
        layout.addLayout(btn_layout)

        while True:
            if dlg.exec() != QDialog.Accepted:
                break
            new_pwd = new_input.text()
            confirm = cfm_input.text()
            if not new_pwd or not confirm:
                QMessageBox.warning(dlg, "提示", "请填写所有字段")
                continue
            if new_pwd != confirm:
                QMessageBox.warning(dlg, "两次输入的密码不一致")
                new_input.clear()
                cfm_input.clear()
                continue
            if is_weak_password(new_pwd):
                QMessageBox.warning(dlg, "密码强度不足",
                                    "密码需至少8位，且包含大小写字母+数字")
                continue
            success, msg = self.user_service.change_password(
                self.password_input.text(), new_pwd
            )
            if success:
                QMessageBox.information(self, "成功", "密码修改成功！")
                break
            else:
                QMessageBox.warning(dlg, "修改失败", msg)
                break

    def _toggle_password(self):
        """切换密码显示/隐藏"""
        toggle_password_visibility(
            self.password_input, self._pwd_action,
            self._pwd_icon_visible, self._pwd_icon_hidden
        )

    def _on_skip(self):
        """访客浏览"""
        self.skip_mode = True
        self.reject()

    def _on_register(self):
        """打开注册窗口（模态，注册完自动回到登录）"""
        from ui.register_window import RegisterWindow
        reg_dlg = RegisterWindow(self.user_service, self)
        if reg_dlg.exec() == QDialog.Accepted:
            QMessageBox.information(self, "提示", "注册成功！请使用新账号登录")
            if reg_dlg.registered_username:
                self.username_input.setText(reg_dlg.registered_username)
        self.password_input.setFocus()
