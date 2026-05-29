"""
主窗口
系统的主界面，包含搜索栏、时令蔬菜、分类导航、热门榜单和状态栏。
"""

from ui.styles import GLOBAL_STYLE, PRIMARY_COLOR, CARD_BG
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QTableWidget, QTableWidgetItem,
    QScrollArea, QFrame, QStatusBar, QMessageBox, QHeaderView,
    QListWidgetItem
)
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, search_service, recommendation_service,
                 user_service, collection_service,
                 vegetable_service, mining_service,
                 recipe_dao, association_rule_dao, user_dao=None,
                 browse_history_dao=None):
        super().__init__()
        self.search_service = search_service
        self.recommendation_service = recommendation_service
        self.user_service = user_service
        self.collection_service = collection_service
        self.vegetable_service = vegetable_service
        self.mining_service = mining_service
        self.recipe_dao = recipe_dao
        self.user_dao = user_dao
        self.browse_history_dao = browse_history_dao
        self.rule_dao = association_rule_dao
        self._init_ui()
        self._load_seasonal_vegetables()
        self._load_hot_ranking()
        self._update_user_status()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("蔬菜百科与推荐系统")
        self.setMinimumSize(1000, 700)
        self.resize(1100, 750)
        self.setStyleSheet(GLOBAL_STYLE)

        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 10, 15, 10)

        # === 顶部栏 ===
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        # 系统名称
        sys_name = QLabel("🥬 蔬菜百科")
        sys_name.setProperty("cssClass", "title")
        sys_name.setStyleSheet(
            f"color: {PRIMARY_COLOR}; font-size: 18px; padding-right: 10px;")
        top_bar.addWidget(sys_name)

        # 搜索区域
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索蔬菜名称/别名...")
        self.search_input.setMinimumWidth(180)
        self.search_input.setMaximumWidth(350)
        self.search_input.returnPressed.connect(self._on_search)
        top_bar.addWidget(self.search_input)

        self.search_btn = QPushButton("🔍")
        self.search_btn.setFixedWidth(45)
        self.search_btn.setToolTip("搜索")
        self.search_btn.clicked.connect(self._on_search)
        top_bar.addWidget(self.search_btn)

        top_bar.addStretch(1)

        # 刷新按钮
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedWidth(40)
        self.refresh_btn.setToolTip("刷新数据")
        self.refresh_btn.setStyleSheet(
            "QPushButton { background-color: white; color: #2E7D32; "
            "border: 2px solid #2E7D32; border-radius: 6px; "
            "font-size: 16px; font-weight: bold; } "
            "QPushButton:hover { background-color: #E8F5E9; }"
        )
        self.refresh_btn.clicked.connect(self._refresh_all)
        top_bar.addWidget(self.refresh_btn)

        # 个人中心按钮
        self.user_btn = QPushButton("👤 个人中心")
        self.user_btn.setProperty("cssClass", "secondary")
        self.user_btn.clicked.connect(self._open_user_center)
        top_bar.addWidget(self.user_btn)

        # 后台管理按钮
        self.admin_btn = QPushButton("⚙ 后台管理")
        self.admin_btn.setProperty("cssClass", "secondary")
        self.admin_btn.clicked.connect(self._open_admin)
        top_bar.addWidget(self.admin_btn)

        main_layout.addLayout(top_bar)

        # === 时令蔬菜板块 ===
        season_label = QLabel("🌿 当月时令蔬菜")
        season_label.setProperty("cssClass", "section-title")
        main_layout.addWidget(season_label)

        self.season_area = QScrollArea()
        self.season_area.setFixedHeight(185)
        self.season_area.setWidgetResizable(True)
        self.season_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.season_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.season_widget = QWidget()
        self.season_layout = QHBoxLayout(self.season_widget)
        self.season_layout.setSpacing(12)
        self.season_layout.setContentsMargins(5, 5, 5, 5)
        self.season_layout.addStretch()

        self.season_area.setWidget(self.season_widget)
        main_layout.addWidget(self.season_area)

        # === 中部：分类导航 + 热门榜单 ===
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(15)

        # 左侧：分类导航
        cat_frame = QFrame()
        cat_frame.setFixedWidth(180)
        cat_frame.setStyleSheet(
            f"background-color: {CARD_BG}; border-radius: 8px; "
            "border: 1px solid #E0E0E0;"
        )
        cat_layout = QVBoxLayout(cat_frame)
        cat_layout.setSpacing(2)
        cat_layout.setContentsMargins(0, 0, 0, 0)

        cat_title = QLabel("📂 蔬菜分类")
        cat_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 14px 16px; "
            f"background-color: {PRIMARY_COLOR}; color: white; "
            "border-top-left-radius: 8px; border-top-right-radius: 8px;"
        )
        cat_layout.addWidget(cat_title)

        self.category_list = QListWidget()
        categories = ['叶菜类', '根茎类', '瓜茄类', '菌菇类', '豆类', '其他']
        for cat in categories:
            item = QListWidgetItem(f"  {cat}")
            self.category_list.addItem(item)
        self.category_list.currentRowChanged.connect(self._on_category_changed)
        self.category_list.setStyleSheet(
            "QListWidget { border: none; } "
            "QListWidget::item { padding: 12px 16px; }"
        )
        cat_layout.addWidget(self.category_list)

        mid_layout.addWidget(cat_frame)

        # 右侧：搜索结果列表 + 热门榜单
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        # 搜索结果/分类结果列表
        self.result_label = QLabel("全部蔬菜")
        self.result_label.setProperty("cssClass", "subtitle")
        right_layout.addWidget(self.result_label)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(
            ["名称", "品类", "时令", "价格(元/斤)", "浏览/收藏"]
        )
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.doubleClicked.connect(self._on_table_double_click)
        right_layout.addWidget(self.result_table)

        # 热门榜单
        hot_label = QLabel("🔥 热门蔬菜榜单 Top10")
        hot_label.setProperty("cssClass", "subtitle")
        hot_label.setStyleSheet(
            f"color: #FF6F00; font-size: 16px; font-weight: bold;"
        )
        right_layout.addWidget(hot_label)

        self.hot_table = QTableWidget()
        self.hot_table.setColumnCount(4)
        self.hot_table.setHorizontalHeaderLabels(
            ["排名", "名称", "品类", "浏览+收藏"]
        )
        self.hot_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.hot_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.hot_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.hot_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.hot_table.setMaximumHeight(320)
        self.hot_table.doubleClicked.connect(self._on_hot_table_double_click)
        right_layout.addWidget(self.hot_table)

        mid_layout.addLayout(right_layout)
        main_layout.addLayout(mid_layout)

        # === 状态栏 ===
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(
            f"background-color: {PRIMARY_COLOR}; color: white; "
            "padding: 4px 10px; font-size: 13px;"
        )

        self.login_status_label = QLabel("未登录")
        self.login_status_label.setStyleSheet("color: white;")
        self.status_bar.addWidget(self.login_status_label)

        self.status_bar.addPermanentWidget(QLabel("  |  "))

        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: white;")
        self.status_bar.addPermanentWidget(self.time_label)

        self.setStatusBar(self.status_bar)

        # 定时刷新时间
        self._update_time()
        timer = QTimer(self)
        timer.timeout.connect(self._update_time)
        timer.start(60000)  # 每分钟更新

        # 默认加载全部蔬菜
        self._display_vegetables(self.search_service.get_all_vegetables(),
                                 "全部蔬菜")

    def _update_time(self):
        """更新时间显示"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.time_label.setText(f"系统时间：{now}")

    def _update_user_status(self):
        """更新登录状态显示"""
        if self.user_service.is_logged_in:
            user = self.user_service.current_user
            self.login_status_label.setText(f"当前用户：{user.username}")
            self.collection_service.set_current_user(user.user_id)
        else:
            self.login_status_label.setText("未登录")
            self.collection_service.set_current_user(None)

    def _load_seasonal_vegetables(self):
        """加载当月时令蔬菜"""
        # 清除旧内容
        while self.season_layout.count() > 0:
            item = self.season_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        month = self.recommendation_service.get_current_month()
        season = self.recommendation_service.get_current_season()
        vegetables = self.recommendation_service.get_seasonal_vegetables(month)

        if not vegetables:
            empty_label = QLabel("暂无时令蔬菜数据")
            empty_label.setStyleSheet("color: #999; padding: 20px;")
            self.season_layout.addWidget(empty_label)
        else:
            for veg in vegetables[:15]:
                card = self._create_season_card(veg)
                self.season_layout.addWidget(card)

        self.season_layout.addStretch()

    def _create_season_card(self, vegetable) -> QFrame:
        """创建时令蔬菜卡片"""
        card = QFrame()
        card.setFixedSize(170, 155)
        card.setStyleSheet(
            f"background-color: {CARD_BG}; border-radius: 10px; "
            "border: 1px solid #E0E0E0;"
        )
        card.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(6, 8, 6, 8)
        layout.setSpacing(3)

        # 蔬菜图片
        from utils.image_utils import load_vegetable_image
        pixmap = load_vegetable_image(vegetable, 70)
        icon_label = QLabel()
        icon_label.setFixedSize(72, 72)
        icon_label.setAlignment(Qt.AlignCenter)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap)
            icon_label.setScaledContents(True)
        else:
            icon_label.setText("🥬")
            icon_label.setStyleSheet("font-size: 36px;")
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)

        # 名称（最多两行）
        name_label = QLabel(vegetable.name)
        name_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; color: #333;")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(32)
        layout.addWidget(name_label)

        price_text = f"¥{
            vegetable.price_ref:.1f}/斤" if vegetable.price_ref else ""
        price_label = QLabel(price_text)
        price_label.setStyleSheet("font-size: 11px; color: #FF6F00;")
        price_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(price_label)

        # 点击打开详情
        def on_click(checked=False, veg=vegetable):
            self._open_detail(veg)

        card.mousePressEvent = on_click
        return card

    def _on_search(self):
        """处理搜索（BR-01：模糊匹配名称和别名）"""
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.information(self, "提示", "请输入搜索关键词")
            return

        results = self.search_service.fuzzy_search(keyword)
        self._display_vegetables(
            results, f'搜索结果："{keyword}"（共{
                len(results)}条）')

    def _on_category_changed(self, index: int):
        """分类切换"""
        categories = ['叶菜类', '根茎类', '瓜茄类', '菌菇类', '豆类', '其他']
        if 0 <= index < len(categories):
            cat = categories[index]
            results = self.search_service.filter_by_category(cat)
            self._display_vegetables(results, f"分类浏览：{cat}（共{len(results)}条）")

    def _load_hot_ranking(self):
        """加载热门榜单"""
        hot_vegs = self.search_service.get_hot_ranking(10)
        self.hot_table.setRowCount(len(hot_vegs))
        for i, veg in enumerate(hot_vegs):
            rank_item = QTableWidgetItem(str(i + 1))
            if i == 0:
                rank_item.setText("🥇 1")
            elif i == 1:
                rank_item.setText("🥈 2")
            elif i == 2:
                rank_item.setText("🥉 3")
            self.hot_table.setItem(i, 0, rank_item)
            self.hot_table.setItem(i, 1, QTableWidgetItem(veg.name))
            self.hot_table.setItem(i, 2, QTableWidgetItem(veg.category))
            score = veg.view_count + veg.favorite_count
            self.hot_table.setItem(i, 3, QTableWidgetItem(str(score)))

    def _display_vegetables(self, vegetables, title: str):
        """在结果表格中展示蔬菜列表"""
        self.result_label.setText(title)
        self.result_table.setRowCount(len(vegetables))
        for i, veg in enumerate(vegetables):
            self.result_table.setItem(i, 0, QTableWidgetItem(veg.name))
            self.result_table.setItem(i, 1, QTableWidgetItem(veg.category))
            self.result_table.setItem(i, 2, QTableWidgetItem(veg.season))
            self.result_table.setItem(i, 3, QTableWidgetItem(
                f"¥{veg.price_ref:.2f}" if veg.price_ref else "-"
            ))
            self.result_table.setItem(i, 4, QTableWidgetItem(
                f"👁{veg.view_count} ❤{veg.favorite_count}"
            ))
        # 存储蔬菜数据用于双击打开详情
        self._displayed_vegetables = vegetables

    def _on_table_double_click(self, index):
        """双击结果表格行"""
        row = index.row()
        if hasattr(self, '_displayed_vegetables') and \
           row < len(self._displayed_vegetables):
            veg = self._displayed_vegetables[row]
            self._open_detail(veg)

    def _on_hot_table_double_click(self, index):
        """双击热门榜单行"""
        row = index.row()
        hot_vegs = self.search_service.get_hot_ranking(10)
        if row < len(hot_vegs):
            self._open_detail(hot_vegs[row])

    def _open_detail(self, vegetable):
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

        # 刷新数据
        self._load_hot_ranking()

    def _open_user_center(self):
        """打开个人中心（含退出后重新登录流程）"""
        # 未登录先弹登录窗
        if not self.user_service.is_logged_in:
            self._show_login_dialog()
            if not self.user_service.is_logged_in:
                return

        from ui.user_center_window import UserCenterWindow
        user_center = UserCenterWindow(
            self.user_service,
            self.collection_service,
            self.search_service,
            self.recommendation_service,
            browse_history_dao=self.browse_history_dao,
            parent=self,
        )
        user_center.exec()
        self._update_user_status()

        # 用户退出了 → 隐藏主窗口，弹登录窗。关登录窗=退出应用
        if not self.user_service.is_logged_in:
            self.hide()
            self._show_login_dialog()
            if self.user_service.is_logged_in:
                self._update_user_status()
                self.show()
            else:
                from PySide6.QtWidgets import QApplication
                QApplication.instance().quit()

    def _refresh_all(self):
        """刷新主页面所有数据"""
        self._load_seasonal_vegetables()
        self._load_hot_ranking()
        self._display_vegetables(
            self.search_service.get_all_vegetables(), "全部蔬菜")
        self._update_user_status()

    def _show_login_dialog(self):
        """弹出登录对话框"""
        from ui.login_window import LoginWindow
        login_dlg = LoginWindow(self.user_service, self)
        if login_dlg.exec() == LoginWindow.Accepted:
            self._update_user_status()

    def _open_admin(self):
        """打开后台管理（仅管理员可访问）"""
        if not self.user_service.is_logged_in:
            QMessageBox.warning(self, "权限不足", "请先登录！")
            return
        if not self.user_service.is_admin():
            QMessageBox.warning(self, "权限不足", "仅管理员可访问后台管理！\n请使用管理员账号登录。")
            return

        from ui.admin_window import AdminWindow
        admin_win = AdminWindow(
            self.vegetable_service,
            self.search_service,
            self.mining_service,
            self.recipe_dao,
            self.rule_dao,
            user_dao=self.user_dao,
            parent=self,
        )
        admin_win.exec()
