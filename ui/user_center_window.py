"""
个人中心窗口
管理用户的收藏夹和自定义清单。
支持双击蔬菜跳转到详情页。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QStackedWidget, QWidget, QInputDialog,
    QMessageBox, QListWidgetItem, QFrame, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor, QPen, QBrush
from ui.styles import GLOBAL_STYLE, CARD_BG


def _make_eye_icon(visible: bool) -> QIcon:
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


class UserCenterWindow(QDialog):
    """个人中心窗口"""

    def __init__(self, user_service, collection_service,
                 search_service, recommendation_service,
                 browse_history_dao=None, parent=None):
        super().__init__(parent)
        self.user_service = user_service
        self.collection_service = collection_service
        self.search_service = search_service
        self.recommendation_service = recommendation_service
        self.browse_history_dao = browse_history_dao
        self._fav_vegetables = []
        self._custom_vegetables = []
        self._history_vegetables = []
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("个人中心")
        self.setMinimumSize(750, 520)
        self.resize(800, 580)
        self.setStyleSheet(GLOBAL_STYLE)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # === 左侧导航栏 ===
        nav_frame = QFrame()
        nav_frame.setFixedWidth(180)
        nav_frame.setStyleSheet(
            f"background-color: {CARD_BG}; border-right: 1px solid #E0E0E0;"
        )
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setSpacing(2)
        nav_layout.setContentsMargins(12, 0, 12, 12)

        nav_title = QLabel("  个人中心")
        nav_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #333; "
            "padding: 18px 15px; background-color: #E8F5E9;"
        )
        nav_layout.addWidget(nav_title)

        self.nav_favorites = QPushButton("⭐ 我的收藏夹")
        self.nav_favorites.setStyleSheet(self._nav_btn_style(True))
        self.nav_favorites.clicked.connect(lambda: self._switch_page(0))
        nav_layout.addWidget(self.nav_favorites)

        self.nav_custom = QPushButton("📋 我的自定义清单")
        self.nav_custom.setStyleSheet(self._nav_btn_style(False))
        self.nav_custom.clicked.connect(lambda: self._switch_page(1))
        nav_layout.addWidget(self.nav_custom)

        self.nav_history = QPushButton("🕐 浏览历史")
        self.nav_history.setStyleSheet(self._nav_btn_style(False))
        self.nav_history.clicked.connect(lambda: self._switch_page(2))
        nav_layout.addWidget(self.nav_history)

        nav_layout.addStretch()

        # 底部按钮组（不拉伸，使用内联样式避免property选择器失效）
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background-color: transparent;")
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setSpacing(6)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        chpwd_btn = QPushButton("🔒 修改密码")
        chpwd_btn.setStyleSheet(
            "QPushButton { background-color: #FFF3E0; color: #E65100; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-size: 13px; font-weight: bold; "
            "min-height: 30px; } "
            "QPushButton:hover { background-color: #FFE0B2; }"
        )
        chpwd_btn.clicked.connect(self._on_change_password)
        bottom_layout.addWidget(chpwd_btn)

        logout_btn = QPushButton("🚪 退出登录")
        logout_btn.setStyleSheet(
            "QPushButton { background-color: #D32F2F; color: white; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-size: 13px; font-weight: bold; "
            "min-height: 30px; } "
            "QPushButton:hover { background-color: #E53935; }"
        )
        logout_btn.clicked.connect(self._on_logout)
        bottom_layout.addWidget(logout_btn)

        close_btn = QPushButton("返回主窗口")
        close_btn.setStyleSheet(
            "QPushButton { background-color: white; color: #2E7D32; "
            "border: 2px solid #2E7D32; border-radius: 6px; padding: 8px 16px; "
            "font-size: 13px; font-weight: bold; min-height: 30px; } "
            "QPushButton:hover { background-color: #E8F5E9; }"
        )
        close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(close_btn)

        nav_layout.addWidget(bottom_widget)

        main_layout.addWidget(nav_frame)

        # === 右侧内容区 ===
        self.content_stack = QStackedWidget()

        # 页面0：收藏夹
        self.favorites_page = self._create_favorites_page()
        self.content_stack.addWidget(self.favorites_page)

        # 页面1：自定义清单
        self.custom_page = self._create_custom_page()
        self.content_stack.addWidget(self.custom_page)

        # 页面2：浏览历史
        self.history_page = self._create_history_page()
        self.content_stack.addWidget(self.history_page)

        main_layout.addWidget(self.content_stack)
        self.setLayout(main_layout)

    def _nav_btn_style(self, active: bool) -> str:
        """导航按钮样式"""
        if active:
            return (
                "text-align: left; padding: 12px 18px; border: none; "
                "border-radius: 0; background-color: #E8F5E9; "
                "color: #2E7D32; font-weight: bold; font-size: 14px;"
            )
        return (
            "text-align: left; padding: 12px 18px; border: none; "
            "border-radius: 0; background-color: transparent; "
            "color: #333; font-size: 14px;"
        )

    def _switch_page(self, index: int):
        """切换页面"""
        self.content_stack.setCurrentIndex(index)
        self.nav_favorites.setStyleSheet(self._nav_btn_style(index == 0))
        self.nav_custom.setStyleSheet(self._nav_btn_style(index == 1))
        self.nav_history.setStyleSheet(self._nav_btn_style(index == 2))
        if index == 2:
            self._load_history()

    def _create_favorites_page(self) -> QWidget:
        """创建收藏夹页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)

        # 标题和操作按钮
        header = QHBoxLayout()
        title = QLabel("我的收藏夹")
        title.setProperty("cssClass", "section-title")
        header.addWidget(title)
        header.addStretch()

        new_btn = QPushButton("+ 新建收藏夹")
        new_btn.clicked.connect(self._create_fav_list)
        header.addWidget(new_btn)

        del_btn = QPushButton("删除收藏夹")
        del_btn.setProperty("cssClass", "danger")
        del_btn.clicked.connect(self._delete_fav_list)
        header.addWidget(del_btn)

        layout.addLayout(header)

        # 收藏夹列表
        self.fav_list_widget = QListWidget()
        self.fav_list_widget.setMaximumHeight(120)
        self.fav_list_widget.currentRowChanged.connect(
            self._on_fav_list_selected
        )
        layout.addWidget(self.fav_list_widget)

        # 蔬菜列表（支持双击跳转详情）
        veg_label = QLabel("收藏夹中的蔬菜（双击可查看详情）：")
        veg_label.setStyleSheet("font-weight: bold; color: #555; font-size: 13px;")
        layout.addWidget(veg_label)

        self.fav_veg_widget = QListWidget()
        self.fav_veg_widget.doubleClicked.connect(self._on_fav_veg_double_click)
        layout.addWidget(self.fav_veg_widget, 1)  # stretch factor

        # 移除按钮
        btn_layout = QHBoxLayout()
        remove_btn = QPushButton("从收藏夹移除")
        remove_btn.setProperty("cssClass", "danger")
        remove_btn.clicked.connect(self._remove_from_fav)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return page

    def _create_custom_page(self) -> QWidget:
        """创建自定义清单页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)

        # 标题和操作按钮
        header = QHBoxLayout()
        title = QLabel("我的自定义清单")
        title.setProperty("cssClass", "section-title")
        header.addWidget(title)
        header.addStretch()

        new_btn = QPushButton("+ 新建清单")
        new_btn.clicked.connect(self._create_custom)
        header.addWidget(new_btn)

        del_btn = QPushButton("删除清单")
        del_btn.setProperty("cssClass", "danger")
        del_btn.clicked.connect(self._delete_custom)
        header.addWidget(del_btn)

        layout.addLayout(header)

        # 清单列表
        self.custom_list_widget = QListWidget()
        self.custom_list_widget.setMaximumHeight(120)
        self.custom_list_widget.currentRowChanged.connect(
            self._on_custom_list_selected
        )
        layout.addWidget(self.custom_list_widget)

        # 蔬菜列表（支持双击跳转详情）
        veg_label = QLabel("清单中的蔬菜（双击可查看详情）：")
        veg_label.setStyleSheet("font-weight: bold; color: #555; font-size: 13px;")
        layout.addWidget(veg_label)

        self.custom_veg_widget = QListWidget()
        self.custom_veg_widget.doubleClicked.connect(self._on_custom_veg_double_click)
        layout.addWidget(self.custom_veg_widget, 1)  # stretch factor

        # 移除按钮
        btn_layout = QHBoxLayout()
        remove_btn = QPushButton("从清单移除")
        remove_btn.setProperty("cssClass", "danger")
        remove_btn.clicked.connect(self._remove_from_custom)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return page

    def _load_data(self):
        """加载数据（首次进入时自动创建默认收藏夹）"""
        # 如果用户还没有任何收藏夹，自动创建一个
        fav_lists = self.collection_service.get_user_favorites_lists()
        if not fav_lists:
            self.user_service.create_favorites_list("默认收藏夹")
        self._load_fav_lists()
        self._load_custom_lists()

    def _load_fav_lists(self):
        """加载收藏夹列表"""
        self.fav_list_widget.clear()
        self._fav_lists = self.collection_service.get_user_favorites_lists()
        for fl in self._fav_lists:
            self.fav_list_widget.addItem(fl.list_name)

    def _load_custom_lists(self):
        """加载自定义清单列表"""
        self.custom_list_widget.clear()
        self._custom_lists = self.collection_service.get_user_custom_lists()
        for cl in self._custom_lists:
            text = cl.list_name
            if cl.description:
                text += f" — {cl.description}"
            self.custom_list_widget.addItem(text)

    def _on_fav_list_selected(self, index: int):
        """收藏夹选中事件"""
        self.fav_veg_widget.clear()
        self._fav_vegetables = []
        if index < 0 or index >= len(self._fav_lists):
            return
        fl = self._fav_lists[index]
        vegetables = self.collection_service.get_favorites_items(fl.fav_list_id)
        self._fav_vegetables = vegetables
        for v in vegetables:
            item = QListWidgetItem(f"{v.name}  ({v.category} | {v.season} | ¥{v.price_ref:.1f}/斤)")
            item.setData(Qt.UserRole, v.veg_id)
            self.fav_veg_widget.addItem(item)

    def _on_custom_list_selected(self, index: int):
        """清单选中事件"""
        self.custom_veg_widget.clear()
        self._custom_vegetables = []
        if index < 0 or index >= len(self._custom_lists):
            return
        cl = self._custom_lists[index]
        vegetables = self.collection_service.get_custom_list_items(cl.list_id)
        self._custom_vegetables = vegetables
        for v in vegetables:
            item = QListWidgetItem(f"{v.name}  ({v.category} | {v.season} | ¥{v.price_ref:.1f}/斤)")
            item.setData(Qt.UserRole, v.veg_id)
            self.custom_veg_widget.addItem(item)

    def _on_fav_veg_double_click(self, index):
        """双击收藏夹中的蔬菜 → 打开详情窗口"""
        row = index.row()
        if 0 <= row < len(self._fav_vegetables):
            veg = self._fav_vegetables[row]
            self._open_vegetable_detail(veg)

    def _on_custom_veg_double_click(self, index):
        """双击清单中的蔬菜 → 打开详情窗口"""
        row = index.row()
        if 0 <= row < len(self._custom_vegetables):
            veg = self._custom_vegetables[row]
            self._open_vegetable_detail(veg)

    def _on_change_password(self):
        """修改密码（自定义对话框，带密码显示切换）"""
        dlg = QDialog(self)
        dlg.setWindowTitle("修改密码")
        dlg.setFixedSize(400, 300)
        dlg.setStyleSheet(GLOBAL_STYLE)
        dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 20, 25, 20)

        layout.addWidget(QLabel("旧密码："))
        old_input = self._make_pwd_field("请输入旧密码")
        layout.addWidget(old_input)

        layout.addWidget(QLabel("新密码（至少8位）："))
        new_input = self._make_pwd_field("请输入新密码")
        layout.addWidget(new_input)

        layout.addWidget(QLabel("确认新密码："))
        cfm_input = self._make_pwd_field("请再次输入新密码")
        layout.addWidget(cfm_input)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确认修改")
        ok_btn.clicked.connect(dlg.accept)
        btn_layout.addWidget(ok_btn)
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(
            "QPushButton { background-color: white; color: #2E7D32; "
            "border: 2px solid #2E7D32; border-radius: 6px; padding: 8px 16px; "
            "font-size: 14px; font-weight: bold; min-height: 30px; } "
            "QPushButton:hover { background-color: #E8F5E9; }"
        )
        cancel_btn.clicked.connect(dlg.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        if dlg.exec() != QDialog.Accepted:
            return

        old_pwd = old_input.text()
        new_pwd = new_input.text()
        confirm = cfm_input.text()

        if not old_pwd or not new_pwd or not confirm:
            QMessageBox.warning(self, "错误", "请填写所有密码字段")
            return

        if new_pwd != confirm:
            QMessageBox.warning(self, "错误", "两次输入的新密码不一致")
            return

        success, msg = self.user_service.change_password(old_pwd, new_pwd)
        if success:
            QMessageBox.information(self, "成功", msg)
        else:
            QMessageBox.warning(self, "失败", msg)

    def _create_history_page(self) -> QWidget:
        """创建浏览历史页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)

        header = QHBoxLayout()
        title = QLabel("浏览历史（最近20条）")
        title.setProperty("cssClass", "section-title")
        header.addWidget(title)
        header.addStretch()

        clear_btn = QPushButton("清空历史")
        clear_btn.setStyleSheet(
            "QPushButton { background-color: #D32F2F; color: white; border: none; "
            "border-radius: 6px; padding: 6px 14px; font-size: 12px; font-weight: bold; } "
            "QPushButton:hover { background-color: #E53935; }"
        )
        clear_btn.clicked.connect(self._clear_history)
        header.addWidget(clear_btn)
        layout.addLayout(header)

        self.history_list = QListWidget()
        self.history_list.doubleClicked.connect(self._on_history_double_click)
        layout.addWidget(self.history_list, 1)

        return page

    def _load_history(self):
        """加载浏览历史"""
        self.history_list.clear()
        self._history_vegetables = []
        if not self.browse_history_dao or not self.user_service.is_logged_in:
            self.history_list.addItem("（请先登录）")
            return
        vegetables = self.browse_history_dao.get_history(
            self.user_service.current_user.user_id
        )
        self._history_vegetables = vegetables
        if not vegetables:
            self.history_list.addItem("（暂无浏览记录）")
        else:
            for v in vegetables:
                self.history_list.addItem(f"{v.name}  ({v.category})")

    def _on_history_double_click(self, index):
        """双击历史记录 → 跳转蔬菜详情"""
        row = index.row()
        if 0 <= row < len(self._history_vegetables):
            veg = self._history_vegetables[row]
            self._open_vegetable_detail(veg)

    def _clear_history(self):
        """清空浏览历史"""
        if not self.user_service.is_logged_in:
            return
        reply = QMessageBox.question(
            self, "确认清空", "确定要清空所有浏览历史吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes and self.browse_history_dao:
            self.browse_history_dao.clear_history(
                self.user_service.current_user.user_id
            )
            self._load_history()
            QMessageBox.information(self, "成功", "浏览历史已清空")

    def _make_pwd_field(self, placeholder: str) -> QLineEdit:
        """创建带眼睛图标的密码输入框"""
        pwd_input = QLineEdit()
        pwd_input.setPlaceholderText(placeholder)
        pwd_input.setEchoMode(QLineEdit.Password)
        eye_visible = _make_eye_icon(True)
        eye_hidden = _make_eye_icon(False)
        action = QAction(eye_visible, "", pwd_input)
        action.triggered.connect(
            lambda: self._toggle_pwd(pwd_input, action, eye_visible, eye_hidden)
        )
        pwd_input.addAction(action, QLineEdit.TrailingPosition)
        return pwd_input

    @staticmethod
    def _toggle_pwd(input_field, action, icon_visible, icon_hidden):
        """切换密码显示/隐藏"""
        if input_field.echoMode() == QLineEdit.Password:
            input_field.setEchoMode(QLineEdit.Normal)
            action.setIcon(icon_hidden)
        else:
            input_field.setEchoMode(QLineEdit.Password)
            action.setIcon(icon_visible)

    def _on_logout(self):
        """退出登录"""
        reply = QMessageBox.question(
            self, "退出登录", "确定要退出登录吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.user_service.logout()
            self.accept()

    def _open_vegetable_detail(self, vegetable):
        """打开蔬菜详情窗口"""
        self.search_service.increment_view_count(vegetable.veg_id)
        vegetable.view_count += 1

        # 记录浏览历史
        if self.user_service.is_logged_in and self.browse_history_dao:
            self.browse_history_dao.add_history(
                self.user_service.current_user.user_id, vegetable.veg_id
            )

        from ui.vegetable_detail_window import VegetableDetailWindow
        detail_win = VegetableDetailWindow(
            vegetable,
            self.search_service,
            self.recommendation_service,
            self.collection_service,
            self.user_service,
            browse_history_dao=self.browse_history_dao,
            parent=self,
        )
        detail_win.exec()

    def _create_fav_list(self):
        """创建新收藏夹"""
        name, ok = QInputDialog.getText(
            self, "新建收藏夹", "请输入收藏夹名称："
        )
        if ok and name.strip():
            success, msg = self.user_service.create_favorites_list(name.strip())
            if success:
                self._load_fav_lists()
                QMessageBox.information(self, "成功", msg)
            else:
                QMessageBox.warning(self, "失败", msg)

    def _delete_fav_list(self):
        """删除收藏夹（默认收藏夹不可删除）"""
        idx = self.fav_list_widget.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "提示", "请先选择要删除的收藏夹")
            return
        fl = self._fav_lists[idx]
        if fl.list_name == "默认收藏夹":
            QMessageBox.warning(self, "提示", "默认收藏夹不可删除")
            return
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除收藏夹「{fl.list_name}」及其中的所有蔬菜吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = self.collection_service.delete_favorites_list(
                fl.fav_list_id
            )
            if success:
                self._load_fav_lists()
                self.fav_veg_widget.clear()
                self._fav_vegetables = []
                QMessageBox.information(self, "成功", msg)
            else:
                QMessageBox.warning(self, "失败", msg)

    def _remove_from_fav(self):
        """从收藏夹移除蔬菜"""
        list_idx = self.fav_list_widget.currentRow()
        veg_idx = self.fav_veg_widget.currentRow()
        if list_idx < 0 or veg_idx < 0:
            QMessageBox.warning(self, "提示", "请先选择收藏夹和要移除的蔬菜")
            return

        fl = self._fav_lists[list_idx]
        if veg_idx < len(self._fav_vegetables):
            veg = self._fav_vegetables[veg_idx]
            success, msg = self.collection_service.remove_from_favorites(
                fl.fav_list_id, veg.veg_id
            )
            if success:
                self._on_fav_list_selected(list_idx)
                QMessageBox.information(self, "成功", f"已从收藏夹移除「{veg.name}」")
            else:
                QMessageBox.warning(self, "失败", msg)

    def _create_custom(self):
        """创建新自定义清单"""
        name, ok = QInputDialog.getText(
            self, "新建清单", "请输入清单名称："
        )
        if ok and name.strip():
            desc, ok2 = QInputDialog.getText(
                self, "清单描述", "请输入清单描述（可选）："
            )
            description = desc.strip() if ok2 else ''
            success, msg = self.user_service.create_custom_list(
                name.strip(), description
            )
            if success:
                self._load_custom_lists()
                QMessageBox.information(self, "成功", msg)
            else:
                QMessageBox.warning(self, "失败", msg)

    def _delete_custom(self):
        """删除自定义清单"""
        idx = self.custom_list_widget.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "提示", "请先选择要删除的清单")
            return
        cl = self._custom_lists[idx]
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除清单「{cl.list_name}」及其中的所有蔬菜吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = self.collection_service.delete_custom_list(
                cl.list_id
            )
            if success:
                self._load_custom_lists()
                self.custom_veg_widget.clear()
                self._custom_vegetables = []
                QMessageBox.information(self, "成功", msg)
            else:
                QMessageBox.warning(self, "失败", msg)

    def _remove_from_custom(self):
        """从清单移除蔬菜"""
        list_idx = self.custom_list_widget.currentRow()
        veg_idx = self.custom_veg_widget.currentRow()
        if list_idx < 0 or veg_idx < 0:
            QMessageBox.warning(self, "提示", "请先选择清单和要移除的蔬菜")
            return

        cl = self._custom_lists[list_idx]
        if veg_idx < len(self._custom_vegetables):
            veg = self._custom_vegetables[veg_idx]
            success, msg = self.collection_service.remove_from_custom_list(
                cl.list_id, veg.veg_id
            )
            if success:
                self._on_custom_list_selected(list_idx)
                QMessageBox.information(self, "成功", f"已从清单移除「{veg.name}」")
            else:
                QMessageBox.warning(self, "失败", msg)
