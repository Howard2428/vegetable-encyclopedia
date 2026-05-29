"""
后台管理窗口
提供蔬菜CRUD、菜谱数据导入和关联规则挖掘功能。
"""

from service.vegetable_service import VegetableService
from entity.vegetable import Vegetable
from ui.styles import GLOBAL_STYLE, CARD_BG
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QStackedWidget, QWidget, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog,
    QInputDialog, QFrame, QComboBox, QLineEdit, QTextEdit,
    QFormLayout, QHeaderView, QSpinBox, QDoubleSpinBox
)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AdminWindow(QDialog):
    """后台管理窗口"""

    def __init__(self, vegetable_service, search_service,
                 mining_service, recipe_dao, association_rule_dao,
                 user_dao=None, parent=None):
        super().__init__(parent)
        self.vegetable_service = vegetable_service
        self.search_service = search_service
        self.mining_service = mining_service
        self.recipe_dao = recipe_dao
        self.rule_dao = association_rule_dao
        self.user_dao = user_dao
        self._init_ui()
        self._load_vegetables()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("后台管理")
        self.setMinimumSize(850, 580)
        self.resize(900, 620)
        self.setStyleSheet(GLOBAL_STYLE)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # === 左侧导航 ===
        nav_frame = QFrame()
        nav_frame.setFixedWidth(170)
        nav_frame.setStyleSheet(
            f"background-color: {CARD_BG}; border-right: 1px solid #E0E0E0;"
        )
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setSpacing(2)
        nav_layout.setContentsMargins(12, 0, 12, 12)

        nav_title = QLabel("  后台管理")
        nav_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #333; "
            "padding: 18px 15px; background-color: #FFF3E0;"
        )
        nav_layout.addWidget(nav_title)

        self.nav_veg = QPushButton("🥬 蔬菜信息管理")
        self.nav_veg.setStyleSheet(self._nav_style(True))
        self.nav_veg.clicked.connect(lambda: self._switch_page(0))
        nav_layout.addWidget(self.nav_veg)

        self.nav_recipe = QPushButton("📖 菜谱数据管理")
        self.nav_recipe.setStyleSheet(self._nav_style(False))
        self.nav_recipe.clicked.connect(lambda: self._switch_page(1))
        nav_layout.addWidget(self.nav_recipe)

        self.nav_mining = QPushButton("⛏ 关联规则挖掘")
        self.nav_mining.setStyleSheet(self._nav_style(False))
        self.nav_mining.clicked.connect(lambda: self._switch_page(2))
        nav_layout.addWidget(self.nav_mining)

        self.nav_users = QPushButton("👥 用户管理")
        self.nav_users.setStyleSheet(self._nav_style(False))
        self.nav_users.clicked.connect(lambda: self._switch_page(3))
        nav_layout.addWidget(self.nav_users)

        self.nav_reset = QPushButton("🔄 系统重置")
        self.nav_reset.setStyleSheet(self._nav_style(False))
        self.nav_reset.clicked.connect(lambda: self._switch_page(4))
        nav_layout.addWidget(self.nav_reset)

        nav_layout.addStretch()

        # 底部按钮（内联样式避免property选择器失效）
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background-color: transparent;")
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setSpacing(0)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

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

        self.veg_page = self._create_veg_page()
        self.content_stack.addWidget(self.veg_page)

        self.recipe_page = self._create_recipe_page()
        self.content_stack.addWidget(self.recipe_page)

        self.mining_page = self._create_mining_page()
        self.content_stack.addWidget(self.mining_page)

        self.users_page = self._create_users_page()
        self.content_stack.addWidget(self.users_page)

        self.reset_page = self._create_reset_page()
        self.content_stack.addWidget(self.reset_page)

        main_layout.addWidget(self.content_stack)
        self.setLayout(main_layout)

    def _nav_style(self, active: bool) -> str:
        """导航按钮样式"""
        bg = "#FFF3E0" if active else "transparent"
        color = "#E65100" if active else "#333"
        return (
            f"text-align: left; padding: 12px 18px; border: none; "
            f"border-radius: 0; background-color: {bg}; "
            f"color: {color}; font-size: 14px;"
            + ("font-weight: bold;" if active else "")
        )

    def _switch_page(self, index: int):
        """切换页面"""
        self.content_stack.setCurrentIndex(index)
        btns = [self.nav_veg, self.nav_recipe, self.nav_mining,
                self.nav_users, self.nav_reset]
        for i, btn in enumerate(btns):
            btn.setStyleSheet(self._nav_style(i == index))
        if index == 2:
            self._refresh_mining_status()
        if index == 3:
            self._load_users()

    def _create_veg_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 15, 20, 15)

        header = QHBoxLayout()
        title = QLabel("蔬菜信息管理")
        title.setProperty("cssClass", "section-title")
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ 新增蔬菜")
        add_btn.clicked.connect(self._add_vegetable)
        header.addWidget(add_btn)

        edit_btn = QPushButton("编辑选中")
        edit_btn.clicked.connect(self._edit_vegetable)
        header.addWidget(edit_btn)

        del_btn = QPushButton("删除选中")
        del_btn.setProperty("cssClass", "danger")
        del_btn.clicked.connect(self._delete_vegetable)
        header.addWidget(del_btn)

        layout.addLayout(header)

        # 蔬菜表格
        self.veg_table = QTableWidget()
        self.veg_table.setColumnCount(8)
        self.veg_table.setHorizontalHeaderLabels(
            ["ID", "名称", "别名", "品类", "时令", "价格(元/斤)", "浏览", "收藏"]
        )
        self.veg_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.veg_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.veg_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.veg_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.veg_table)

        return page

    def _load_vegetables(self):
        """加载蔬菜数据到表格"""
        vegetables = self.vegetable_service.get_all_vegetables()
        self.veg_table.setRowCount(len(vegetables))
        for i, v in enumerate(vegetables):
            self.veg_table.setItem(i, 0, QTableWidgetItem(str(v.veg_id)))
            self.veg_table.setItem(i, 1, QTableWidgetItem(v.name))
            self.veg_table.setItem(i, 2, QTableWidgetItem(v.alias))
            self.veg_table.setItem(i, 3, QTableWidgetItem(v.category))
            self.veg_table.setItem(i, 4, QTableWidgetItem(v.season))
            self.veg_table.setItem(i, 5, QTableWidgetItem(
                f"{v.price_ref:.2f}" if v.price_ref else "0.00"
            ))
            self.veg_table.setItem(i, 6, QTableWidgetItem(str(v.view_count)))
            self.veg_table.setItem(
                i, 7, QTableWidgetItem(str(v.favorite_count)))

    def _add_vegetable(self):
        """新增蔬菜"""
        veg = Vegetable()
        if self._show_veg_dialog(veg, "新增蔬菜"):
            success, msg = self.vegetable_service.add_vegetable(veg)
            if success:
                self._load_vegetables()
                QMessageBox.information(self, "成功", msg)
            else:
                QMessageBox.warning(self, "失败", msg)

    def _edit_vegetable(self):
        """编辑蔬菜"""
        row = self.veg_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要编辑的蔬菜")
            return
        veg_id = int(self.veg_table.item(row, 0).text())
        veg = self.vegetable_service.get_vegetable_by_id(veg_id)
        if veg and self._show_veg_dialog(veg, "编辑蔬菜"):
            success, msg = self.vegetable_service.update_vegetable(veg)
            if success:
                self._load_vegetables()
                QMessageBox.information(self, "成功", msg)
            else:
                QMessageBox.warning(self, "失败", msg)

    def _delete_vegetable(self):
        """删除蔬菜"""
        row = self.veg_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要删除的蔬菜")
            return
        veg_id = int(self.veg_table.item(row, 0).text())
        veg_name = self.veg_table.item(row, 1).text()
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除蔬菜「{veg_name}」吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = self.vegetable_service.delete_vegetable(veg_id)
            if success:
                self._load_vegetables()
                QMessageBox.information(self, "成功", msg)
            else:
                QMessageBox.warning(self, "失败", msg)

    def _show_veg_dialog(self, veg: Vegetable, title: str) -> bool:
        """显示蔬菜编辑对话框"""
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.setFixedSize(500, 520)
        dlg.setStyleSheet(GLOBAL_STYLE)
        dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QFormLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 20, 25, 20)

        name_input = QLineEdit(veg.name)
        name_input.setPlaceholderText("必填")
        layout.addRow("蔬菜名称 *：", name_input)

        alias_input = QLineEdit(veg.alias)
        alias_input.setPlaceholderText("多个别名用逗号分隔")
        layout.addRow("别名：", alias_input)

        cat_combo = QComboBox()
        cat_combo.addItems(VegetableService.VALID_CATEGORIES)
        if veg.category:
            cat_combo.setCurrentText(veg.category)
        layout.addRow("品类 *：", cat_combo)

        season_combo = QComboBox()
        season_combo.addItems(['春', '夏', '秋', '冬', '全年'])
        if veg.season:
            season_combo.setCurrentText(veg.season)
        layout.addRow("时令 *：", season_combo)

        price_spin = QDoubleSpinBox()
        price_spin.setRange(0, 9999)
        price_spin.setDecimals(2)
        price_spin.setValue(veg.price_ref or 0)
        price_spin.setPrefix("¥ ")
        layout.addRow("参考价格(元/斤)：", price_spin)

        nutrition_text = QTextEdit()
        nutrition_text.setPlaceholderText("输入营养功效说明...")
        nutrition_text.setText(veg.nutrition or '')
        nutrition_text.setMaximumHeight(100)
        layout.addRow("营养功效：", nutrition_text)

        purchase_text = QTextEdit()
        purchase_text.setPlaceholderText("输入选购技巧...")
        purchase_text.setText(veg.purchase_tips or '')
        purchase_text.setMaximumHeight(80)
        layout.addRow("选购技巧：", purchase_text)

        storage_text = QTextEdit()
        storage_text.setPlaceholderText("输入储存方法...")
        storage_text.setText(veg.storage_method or '')
        storage_text.setMaximumHeight(80)
        layout.addRow("储存方法：", storage_text)

        # 图片路径（可选，留空则自动按名称查找）
        img_layout = QHBoxLayout()
        img_path_input = QLineEdit(veg.image_path or '')
        img_path_input.setPlaceholderText("留空自动匹配 data/images/蔬菜名.jpg")
        img_layout.addWidget(img_path_input)
        browse_btn = QPushButton("浏览...")
        browse_btn.setStyleSheet(
            "QPushButton { background-color: #757575; color: white; border: none; "
            "border-radius: 4px; padding: 6px 12px; font-size: 12px; } "
            "QPushButton:hover { background-color: #616161; }"
        )
        browse_btn.clicked.connect(lambda: img_path_input.setText(
            QFileDialog.getOpenFileName(dlg, "选择蔬菜图片", "",
                                        "Images (*.jpg *.jpeg *.png *.webp)")[0] or img_path_input.text()
        ))
        img_layout.addWidget(browse_btn)
        layout.addRow("图片路径：", img_layout)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("保 存")
        cancel_btn = QPushButton("取 消")
        cancel_btn.setProperty("cssClass", "secondary")
        ok_btn.clicked.connect(dlg.accept)
        cancel_btn.clicked.connect(dlg.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        if dlg.exec() == QDialog.Accepted:
            veg.name = name_input.text().strip()
            veg.alias = alias_input.text().strip()
            veg.category = cat_combo.currentText()
            veg.season = season_combo.currentText()
            veg.price_ref = price_spin.value()
            veg.nutrition = nutrition_text.toPlainText().strip()
            veg.purchase_tips = purchase_text.toPlainText().strip()
            veg.storage_method = storage_text.toPlainText().strip()
            veg.image_path = img_path_input.text().strip()
            return True
        return False

    def _create_recipe_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 15, 20, 15)

        header = QHBoxLayout()
        title = QLabel("菜谱数据管理")
        title.setProperty("cssClass", "section-title")
        header.addWidget(title)
        header.addStretch()

        import_btn = QPushButton("📂 导入JSON菜谱")
        import_btn.clicked.connect(self._import_recipes)
        header.addWidget(import_btn)

        layout.addLayout(header)

        self.recipe_count_label = QLabel()
        self.recipe_count_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.recipe_count_label)

        self.recipe_list = QListWidget()
        layout.addWidget(self.recipe_list)

        self._refresh_recipes()
        return page

    def _refresh_recipes(self):
        """刷新菜谱列表"""
        self.recipe_list.clear()
        recipes = self.recipe_dao.get_all_recipes()
        self.recipe_count_label.setText(
            f"共 {len(recipes)} 条菜谱数据"
        )
        for r in recipes:
            self.recipe_list.addItem(
                f"{r['name']} — 食材：{'、'.join(r['ingredients'])}"
            )

    def _import_recipes(self):
        """导入菜谱JSON文件"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "选择菜谱JSON文件", "",
            "JSON Files (*.json);;All Files (*)"
        )
        if filepath:
            try:
                count = self.recipe_dao.import_from_json(filepath)
                self._refresh_recipes()
                QMessageBox.information(
                    self, "导入成功",
                    f"成功导入 {count} 条菜谱数据！"
                )
            except Exception as e:
                QMessageBox.warning(self, "导入失败", str(e))

    def _create_mining_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 15)

        title = QLabel("关联规则挖掘")
        title.setProperty("cssClass", "section-title")
        layout.addWidget(title)

        # 状态信息
        status_frame = QFrame()
        status_frame.setStyleSheet(
            f"background-color: {CARD_BG}; border-radius: 8px; "
            "border: 1px solid #E0E0E0; padding: 15px;"
        )
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(8)

        self.recipe_status_label = QLabel()
        status_layout.addWidget(self.recipe_status_label)

        self.rule_status_label = QLabel()
        status_layout.addWidget(self.rule_status_label)

        layout.addWidget(status_frame)

        # 参数设置
        param_frame = QFrame()
        param_frame.setStyleSheet(
            f"background-color: {CARD_BG}; border-radius: 8px; "
            "border: 1px solid #E0E0E0; padding: 15px;"
        )
        param_layout = QFormLayout(param_frame)
        param_layout.setSpacing(8)

        self.min_support_spin = QDoubleSpinBox()
        self.min_support_spin.setRange(0.001, 1.0)
        self.min_support_spin.setDecimals(3)
        self.min_support_spin.setValue(0.01)
        self.min_support_spin.setSingleStep(0.005)
        param_layout.addRow("最小支持度：", self.min_support_spin)

        self.min_confidence_spin = QDoubleSpinBox()
        self.min_confidence_spin.setRange(0.01, 1.0)
        self.min_confidence_spin.setDecimals(2)
        self.min_confidence_spin.setValue(0.1)
        self.min_confidence_spin.setSingleStep(0.05)
        param_layout.addRow("最小置信度：", self.min_confidence_spin)

        layout.addWidget(param_frame)

        # 挖掘按钮
        self.mining_btn = QPushButton("⛏ 开始挖掘")
        self.mining_btn.setStyleSheet(
            "font-size: 16px; padding: 12px; min-height: 40px;"
        )
        self.mining_btn.clicked.connect(self._start_mining)
        layout.addWidget(self.mining_btn)

        layout.addStretch()
        return page

    def _refresh_mining_status(self):
        """刷新挖掘状态"""
        recipe_count = self.recipe_dao.get_recipe_count()
        rule_count = self.rule_dao.count()
        self.recipe_status_label.setText(f"📖 菜谱数据：{recipe_count} 条")
        self.rule_status_label.setText(f"🔗 当前规则库：{rule_count} 条规则")

    def _start_mining(self):
        """开始关联规则挖掘"""
        self._refresh_mining_status()
        recipe_count = self.recipe_dao.get_recipe_count()
        if recipe_count == 0:
            QMessageBox.warning(
                self, "提示",
                "没有菜谱数据！请先在「菜谱数据管理」页导入菜谱JSON文件"
            )
            return

        from ui.mining_progress_dialog import MiningProgressDialog
        dlg = MiningProgressDialog(self.mining_service, self)
        dlg.start_mining(
            min_support=self.min_support_spin.value(),
            min_confidence=self.min_confidence_spin.value(),
        )
        dlg.exec()
        self._refresh_mining_status()

    def _create_users_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 15, 20, 15)

        title = QLabel("用户管理")
        title.setProperty("cssClass", "section-title")
        layout.addWidget(title)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(
            ["ID", "用户名", "邮箱", "角色", "注册时间", "最后登录"]
        )
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.users_table)

        btn_layout = QHBoxLayout()
        reset_btn = QPushButton("🔑 重置选中用户密码为 12345678")
        reset_btn.setStyleSheet(
            "QPushButton { background-color: #FF6F00; color: white; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-size: 14px; font-weight: bold; "
            "min-height: 30px; } "
            "QPushButton:hover { background-color: #FF8F00; }"
        )
        reset_btn.clicked.connect(self._reset_user_password)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return page

    def _load_users(self):
        """加载用户列表"""
        if not self.user_dao:
            return
        users = self.user_dao.get_all_users()
        self.users_table.setRowCount(len(users))
        for i, u in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(str(u['user_id'])))
            self.users_table.setItem(i, 1, QTableWidgetItem(u['username']))
            self.users_table.setItem(i, 2, QTableWidgetItem(u['email'] or '-'))
            self.users_table.setItem(i, 3, QTableWidgetItem(u['role']))
            self.users_table.setItem(i, 4, QTableWidgetItem(
                str(u['register_time']) if u['register_time'] else '-'))
            self.users_table.setItem(i, 5, QTableWidgetItem(
                str(u['last_login_time']) if u['last_login_time'] else '从未登录'))

    def _reset_user_password(self):
        """重置选中用户的密码为12345678"""
        if not self.user_dao:
            return
        row = self.users_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要重置密码的用户")
            return
        user_id = int(self.users_table.item(row, 0).text())
        username = self.users_table.item(row, 1).text()
        reply = QMessageBox.question(
            self, "确认重置",
            f"确定要将用户「{username}」的密码重置为 12345678 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from utils.password_utils import hash_password
            self.user_dao.update_password(user_id, hash_password("12345678"))
            QMessageBox.information(
                self, "成功", f"用户「{username}」密码已重置为 12345678")

    def _create_reset_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 15)

        title = QLabel("系统重置")
        title.setProperty("cssClass", "section-title")
        layout.addWidget(title)

        desc = QLabel("以下操作会清除统计数据，不会删除蔬菜和用户数据。")
        desc.setStyleSheet("color: #666; font-size: 13px;")
        layout.addWidget(desc)

        # 清除浏览/收藏统计
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px; "
                                  "border: 1px solid #E0E0E0; padding: 15px;")
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setSpacing(10)

        stats_label = QLabel("📊 统计数据重置")
        stats_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        stats_layout.addWidget(stats_label)
        stats_desc = QLabel("将所有蔬菜的浏览量和收藏量归零，热门榜单也会重置。")
        stats_desc.setStyleSheet("color: #666;")
        stats_desc.setWordWrap(True)
        stats_layout.addWidget(stats_desc)

        self.reset_stats_btn = QPushButton("清除所有浏览/收藏统计")
        self.reset_stats_btn.setStyleSheet(
            "QPushButton { background-color: #D32F2F; color: white; border: none; "
            "border-radius: 6px; padding: 10px 20px; font-size: 14px; font-weight: bold; "
            "min-height: 30px; } "
            "QPushButton:hover { background-color: #E53935; }"
        )
        self.reset_stats_btn.clicked.connect(self._do_reset_stats)
        stats_layout.addWidget(self.reset_stats_btn)

        layout.addWidget(stats_frame)

        # 清除关联规则
        rules_frame = QFrame()
        rules_frame.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px; "
                                  "border: 1px solid #E0E0E0; padding: 15px;")
        rules_layout = QVBoxLayout(rules_frame)
        rules_layout.setSpacing(10)

        rules_label = QLabel("🔗 关联规则重置")
        rules_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        rules_layout.addWidget(rules_label)
        rules_desc = QLabel("清空所有挖掘出的关联规则，之后可重新执行挖掘。")
        rules_desc.setStyleSheet("color: #666;")
        rules_desc.setWordWrap(True)
        rules_layout.addWidget(rules_desc)

        self.reset_rules_btn = QPushButton("清空所有关联规则")
        self.reset_rules_btn.setStyleSheet(
            "QPushButton { background-color: #D32F2F; color: white; border: none; "
            "border-radius: 6px; padding: 10px 20px; font-size: 14px; font-weight: bold; "
            "min-height: 30px; } "
            "QPushButton:hover { background-color: #E53935; }"
        )
        self.reset_rules_btn.clicked.connect(self._do_reset_rules)
        rules_layout.addWidget(self.reset_rules_btn)

        layout.addWidget(rules_frame)

        # 清除所有用户数据
        users_frame = QFrame()
        users_frame.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px; "
                                  "border: 1px solid #E0E0E0; padding: 15px;")
        users_layout = QVBoxLayout(users_frame)
        users_layout.setSpacing(10)

        users_label = QLabel("👥 用户数据清除")
        users_label.setStyleSheet(
            "font-weight: bold; font-size: 15px; color: #D32F2F;")
        users_layout.addWidget(users_label)
        users_desc = QLabel(
            "删除所有用户及其收藏夹、自定义清单、浏览历史。蔬菜数据和关联规则保留。\n删除后会自动重建 test 和 admin 账号。")
        users_desc.setStyleSheet("color: #666;")
        users_desc.setWordWrap(True)
        users_layout.addWidget(users_desc)

        self.reset_users_btn = QPushButton("删除所有用户数据")
        self.reset_users_btn.setStyleSheet(
            "QPushButton { background-color: #B71C1C; color: white; border: none; "
            "border-radius: 6px; padding: 10px 20px; font-size: 14px; font-weight: bold; "
            "min-height: 30px; } "
            "QPushButton:hover { background-color: #D32F2F; }"
        )
        self.reset_users_btn.clicked.connect(self._do_reset_users)
        users_layout.addWidget(self.reset_users_btn)

        layout.addWidget(users_frame)
        layout.addStretch()

        return page

    def _do_reset_stats(self):
        """清除所有浏览/收藏统计"""
        reply = QMessageBox.question(
            self, "确认重置",
            "确定要清除所有蔬菜的浏览量和收藏量吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            count = self.vegetable_service.vegetable_dao.reset_all_stats()
            QMessageBox.information(self, "成功", f"已重置 {count} 种蔬菜的统计数据")

    def _do_reset_rules(self):
        """清空所有关联规则"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空所有关联规则吗？\n之后需要重新执行规则挖掘。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            count = self.rule_dao.clear_all()
            QMessageBox.information(self, "成功", f"已清空 {count} 条关联规则")

    def _do_reset_users(self):
        """删除所有用户数据"""
        reply = QMessageBox.question(
            self, "⚠ 确认删除",
            "确定要删除所有用户及关联数据吗？\n\n"
            "将删除：所有用户、收藏夹、自定义清单、浏览历史\n"
            "保留：蔬菜数据、菜谱数据、关联规则\n\n"
            "此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        if not self.user_dao:
            QMessageBox.warning(self, "错误", "无法访问用户数据")
            return

        count = self.user_dao.delete_all_users()
        # 重建测试账号
        from utils.password_utils import hash_password
        self.user_dao.create_user(
            'test',
            hash_password('Test1234'),
            'test@example.com',
            'user')
        self.user_dao.create_user(
            'admin',
            hash_password('Admin1234'),
            'admin@example.com',
            'admin')

        QMessageBox.information(
            self, "成功",
            f"已删除 {count} 个用户及关联数据。\n"
            "已重建测试账号：test/Test1234、admin/Admin1234"
        )


# 导入放最后避免循环引用
