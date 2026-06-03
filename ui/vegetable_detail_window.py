"""
蔬菜详情窗口
展示蔬菜的完整百科信息，支持收藏和关联推荐。
"""

from ui.styles import GLOBAL_STYLE, PRIMARY_COLOR, CARD_BG
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QScrollArea, QWidget, QFrame, QMessageBox,
    QListWidget, QInputDialog
)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class VegetableDetailWindow(QDialog):
    """蔬菜详情窗口"""

    def __init__(self, vegetable, search_service, recommendation_service,
                 collection_service, user_service, browse_history_dao=None,
                 parent=None):
        super().__init__(parent)
        self.vegetable = vegetable
        self.search_service = search_service
        self.recommendation_service = recommendation_service
        self.collection_service = collection_service
        self.user_service = user_service
        self.browse_history_dao = browse_history_dao
        self._history = []
        self._init_ui()
        self._load_data()
        self._record_history()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"{self.vegetable.name} - 蔬菜详情")
        self.setMinimumSize(700, 600)
        self.resize(750, 650)
        self.setStyleSheet(GLOBAL_STYLE)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 15, 20, 15)

        # === 顶部：返回 + 名称 + 别名 ===
        top_layout = QHBoxLayout()

        self.back_btn = QPushButton("← 返回")
        self.back_btn.setStyleSheet(
            "QPushButton { background-color: white; color: #2E7D32; "
            "border: 2px solid #2E7D32; border-radius: 6px; padding: 6px 14px; "
            "font-size: 13px; font-weight: bold; } "
            "QPushButton:hover { background-color: #E8F5E9; }"
        )
        self.back_btn.setFixedWidth(80)
        self.back_btn.clicked.connect(self._go_back)
        top_layout.addWidget(self.back_btn)

        name_layout = QVBoxLayout()
        self.name_label = QLabel(self.vegetable.name)
        self.name_label.setProperty("cssClass", "title")
        name_layout.addWidget(self.name_label)

        self.alias_label = QLabel(f"别名：{self.vegetable.alias or '无'}")
        self.alias_label.setStyleSheet("color: #888; font-size: 13px;")
        name_layout.addWidget(self.alias_label)

        top_layout.addLayout(name_layout)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)

        # === 中部：图片 + 基本信息 + 操作按钮 ===
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(20)

        # 左侧：蔬菜图片
        from utils.image_utils import load_vegetable_image
        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet(
            "background-color: #E8F5E9; border-radius: 12px; "
            "border: 2px solid #C8E6C9;"
        )
        pixmap = load_vegetable_image(self.vegetable, 190)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("🥬")
            self.image_label.setStyleSheet(
                "background-color: #E8F5E9; border-radius: 12px; "
                "border: 2px solid #C8E6C9; font-size: 64px;"
            )
        mid_layout.addWidget(self.image_label)

        # 右侧：基本信息 + 操作按钮
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        info_frame = QFrame()
        info_frame.setStyleSheet(
            f"background-color: {CARD_BG}; border-radius: 8px; "
            f"border: 1px solid #E0E0E0; padding: 12px;"
        )
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(6)

        self.category_label = QLabel()
        info_layout.addWidget(self.category_label)

        self.season_label = QLabel()
        info_layout.addWidget(self.season_label)

        self.price_label = QLabel()
        info_layout.addWidget(self.price_label)

        self.stats_label = QLabel()
        info_layout.addWidget(self.stats_label)

        right_layout.addWidget(info_frame)

        # 收藏按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.favorite_btn = QPushButton("☆ 收藏")
        self.favorite_btn.setProperty("cssClass", "accent")
        self.favorite_btn.clicked.connect(self._on_favorite)
        btn_layout.addWidget(self.favorite_btn)

        self.list_btn = QPushButton("📋 加入清单")
        self.list_btn.clicked.connect(self._on_add_to_list)
        btn_layout.addWidget(self.list_btn)

        right_layout.addLayout(btn_layout)
        right_layout.addStretch()

        mid_layout.addLayout(right_layout)
        main_layout.addLayout(mid_layout)

        # === 下部：标签页 ===
        self.tab_widget = QTabWidget()

        self.nutrition_tab = QLabel()
        self.nutrition_tab.setWordWrap(True)
        self.nutrition_tab.setAlignment(Qt.AlignTop)
        self.nutrition_tab.setStyleSheet(
            "padding: 15px; font-size: 14px; line-height: 1.6;")
        self.tab_widget.addTab(self.nutrition_tab, "🥗 营养功效")

        self.purchase_tab = QLabel()
        self.purchase_tab.setWordWrap(True)
        self.purchase_tab.setAlignment(Qt.AlignTop)
        self.purchase_tab.setStyleSheet(
            "padding: 15px; font-size: 14px; line-height: 1.6;")
        self.tab_widget.addTab(self.purchase_tab, "🛒 选购技巧")

        self.storage_tab = QLabel()
        self.storage_tab.setWordWrap(True)
        self.storage_tab.setAlignment(Qt.AlignTop)
        self.storage_tab.setStyleSheet(
            "padding: 15px; font-size: 14px; line-height: 1.6;")
        self.tab_widget.addTab(self.storage_tab, "📦 储存方法")

        main_layout.addWidget(self.tab_widget)

        # === 底部：关联推荐 ===
        rec_label = QLabel("💡 你可能还喜欢")
        rec_label.setProperty("cssClass", "section-title")
        main_layout.addWidget(rec_label)

        # 空状态提示（无推荐时显示，不会被截断）
        self.rec_empty_label = QLabel("暂无推荐数据，请先在后台管理中执行规则挖掘")
        self.rec_empty_label.setStyleSheet(
            "color: #999; font-size: 13px; padding: 10px 0px;")
        self.rec_empty_label.setVisible(False)
        main_layout.addWidget(self.rec_empty_label)

        # 推荐卡片滚动区（有推荐时显示）
        self.rec_area = QScrollArea()
        self.rec_area.setFixedHeight(165)
        self.rec_area.setWidgetResizable(False)
        self.rec_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.rec_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.rec_area.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }")
        self.rec_area.setVisible(False)

        self.rec_widget = QWidget()
        self.rec_widget.setFixedHeight(160)
        self.rec_widget.setStyleSheet("background: transparent;")
        self.rec_layout = QHBoxLayout(self.rec_widget)
        self.rec_layout.setSpacing(12)
        self.rec_layout.setContentsMargins(5, 10, 15, 10)

        self.rec_area.setWidget(self.rec_widget)
        main_layout.addWidget(self.rec_area)

        self.setLayout(main_layout)

    def _load_data(self):
        """加载数据显示（跳转时复用）"""
        veg = self.vegetable
        self.setWindowTitle(f"{veg.name} - 蔬菜详情")

        # 顶部名称+别名
        self.name_label.setText(veg.name)
        self.alias_label.setText(f"别名：{veg.alias or '无'}")

        # 图片
        from utils.image_utils import load_vegetable_image
        pixmap = load_vegetable_image(veg, 190)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap)
            self.image_label.setStyleSheet(
                "background-color: #E8F5E9; border-radius: 12px; "
                "border: 2px solid #C8E6C9;"
            )
        else:
            self.image_label.setText("🥬")
            self.image_label.setStyleSheet(
                "background-color: #E8F5E9; border-radius: 12px; "
                "border: 2px solid #C8E6C9; font-size: 64px;"
            )

        # 基本信息
        self.category_label.setText(f"📂 品类：{veg.category}")
        self.season_label.setText(f"🌤 时令：{veg.season}")
        self.price_label.setText(
            f"💰 参考价格：{veg.price_ref:.2f} 元/斤" if veg.price_ref else "💰 参考价格：暂无"
        )
        self.stats_label.setText(
            f"👁 浏览 {veg.view_count} 次  |  ❤ 收藏 {veg.favorite_count} 次"
        )

        # 标签页内容
        self.nutrition_tab.setText(veg.nutrition or "暂无营养功效信息")
        self.purchase_tab.setText(veg.purchase_tips or "暂无选购技巧信息")
        self.storage_tab.setText(veg.storage_method or "暂无储存方法信息")

        # 更新收藏按钮状态
        self._update_favorite_btn()

        # 加载关联推荐
        self._load_recommendations()

    def _update_favorite_btn(self):
        """更新收藏按钮状态"""
        if not self.user_service.is_logged_in:
            return

        fav_veg_ids = self.collection_service.get_favorited_veg_ids()
        if self.vegetable.veg_id in fav_veg_ids:
            self.favorite_btn.setText("★ 已收藏")
            self.favorite_btn.setStyleSheet(
                "background-color: #D32F2F; color: white; border: none; "
                "border-radius: 6px; padding: 8px 20px; font-size: 14px; font-weight: bold;"
            )
        else:
            self.favorite_btn.setText("☆ 收藏")
            self.favorite_btn.setProperty("cssClass", "accent")
            self.favorite_btn.setStyleSheet("")

    def _on_favorite(self):
        """处理收藏/取消收藏"""
        if not self.user_service.is_logged_in:
            QMessageBox.information(self, "提示", "请先登录后再使用收藏功能")
            return

        fav_veg_ids = self.collection_service.get_favorited_veg_ids()
        veg_id = self.vegetable.veg_id

        if veg_id in fav_veg_ids:
            # 已收藏 → 取消收藏
            lists = self.collection_service.get_user_favorites_lists()
            for fav_list in lists:
                self.collection_service.remove_from_favorites(
                    fav_list.fav_list_id, veg_id
                )
            self.recommendation_service.decrement_favorite_count(veg_id)
            QMessageBox.information(self, "提示", "已取消收藏")
        else:
            # 未收藏 → 自动创建默认收藏夹（如果还没有的话）
            lists = self.collection_service.get_user_favorites_lists()
            if not lists:
                self.user_service.create_favorites_list("默认收藏夹")
        lists = self.collection_service.get_user_favorites_lists()

        # 弹出选择收藏夹对话框
        dlg = QDialog(self)
        dlg.setWindowTitle("选择收藏夹")
        dlg.setFixedSize(380, 340)
        dlg.setStyleSheet(GLOBAL_STYLE)
        dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.addWidget(QLabel("请选择要收藏到哪个收藏夹："))

        list_widget = QListWidget()
        for fl in lists:
            list_widget.addItem(fl.list_name)
        list_widget.setCurrentRow(0)
        layout.addWidget(list_widget)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("收藏到此夹")
        ok_btn.clicked.connect(dlg.accept)
        btn_layout.addWidget(ok_btn)

        new_btn = QPushButton("+ 新建收藏夹")
        new_btn.setStyleSheet(
            "QPushButton { background-color: white; color: #2E7D32; "
            "border: 2px solid #2E7D32; border-radius: 6px; padding: 8px 14px; "
            "font-size: 14px; font-weight: bold; min-height: 30px; } "
            "QPushButton:hover { background-color: #E8F5E9; }"
        )
        btn_layout.addWidget(new_btn)
        layout.addLayout(btn_layout)

        def create_new():
            name, ok = QInputDialog.getText(dlg, "新建收藏夹", "收藏夹名称：")
            if ok and name.strip():
                success, msg = self.user_service.create_favorites_list(
                    name.strip())
                if success:
                    lists.clear()
                    lists.extend(
                        self.collection_service.get_user_favorites_lists())
                list_widget.clear()
                for fl in lists:
                    list_widget.addItem(fl.list_name)
                list_widget.setCurrentRow(list_widget.count() - 1)
            else:
                QMessageBox.warning(dlg, "失败", msg)
        new_btn.clicked.connect(create_new)

        if dlg.exec() == QDialog.Accepted and list_widget.currentRow() >= 0:
            fl = lists[list_widget.currentRow()]
            success, msg = self.collection_service.add_to_favorites(
                fl.fav_list_id, veg_id
            )
            if success:
                self.recommendation_service.increment_favorite_count(veg_id)
                QMessageBox.information(self, "提示", f"已收藏到「{fl.list_name}」！")
            else:
                QMessageBox.warning(self, "提示", msg)
        else:
            return

        self._update_favorite_btn()
        self.vegetable = self.search_service.get_by_id(veg_id)
        self.stats_label.setText(
            f"👁 浏览 {self.vegetable.view_count} 次  |  "
            f"❤ 收藏 {self.vegetable.favorite_count} 次"
        )

    def _on_add_to_list(self):
        """加入自定义清单（可当场新建）"""
        if not self.user_service.is_logged_in:
            QMessageBox.information(self, "提示", "请先登录后再使用此功能")
            return

        lists = self.collection_service.get_user_custom_lists()

        dlg = QDialog(self)
        dlg.setWindowTitle("加入清单")
        dlg.setFixedSize(380, 360)
        dlg.setStyleSheet(GLOBAL_STYLE)
        dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.addWidget(QLabel("请选择或新建清单："))

        list_widget = QListWidget()
        for cl in lists:
            text = cl.list_name
            if cl.description:
                text += f"  ({cl.description})"
            list_widget.addItem(text)
        if lists:
            list_widget.setCurrentRow(0)
        else:
            list_widget.addItem("（暂无清单，请点击下方新建）")
            list_widget.item(0).setFlags(Qt.NoItemFlags)  # 不可选
        layout.addWidget(list_widget)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("加入此清单")
        ok_btn.clicked.connect(dlg.accept)
        btn_layout.addWidget(ok_btn)

        new_btn = QPushButton("+ 新建清单")
        new_btn.setStyleSheet(
            "QPushButton { background-color: white; color: #2E7D32; "
            "border: 2px solid #2E7D32; border-radius: 6px; padding: 8px 14px; "
            "font-size: 14px; font-weight: bold; min-height: 30px; } "
            "QPushButton:hover { background-color: #E8F5E9; }"
        )
        btn_layout.addWidget(new_btn)
        layout.addLayout(btn_layout)

        def create_new():
            name, ok = QInputDialog.getText(dlg, "新建清单", "清单名称：")
            if ok and name.strip():
                desc, ok2 = QInputDialog.getText(dlg, "清单描述", "描述（可选）：")
                description = desc.strip() if ok2 else ''
                success, msg = self.user_service.create_custom_list(
                    name.strip(), description
                )
                if success:
                    lists.clear()
                    lists.extend(self.collection_service.get_user_custom_lists())
                    list_widget.clear()
                    for cl in lists:
                        text = cl.list_name
                        if cl.description:
                            text += f"  ({cl.description})"
                        list_widget.addItem(text)
                    list_widget.setCurrentRow(list_widget.count() - 1)
                else:
                    QMessageBox.warning(dlg, "失败", msg)
        new_btn.clicked.connect(create_new)

        if dlg.exec() == QDialog.Accepted and lists and list_widget.currentRow() >= 0:
            cl = lists[list_widget.currentRow()]
            success, msg = self.collection_service.add_to_custom_list(
                cl.list_id, self.vegetable.veg_id
            )
            if success:
                QMessageBox.information(self, "提示", f"已加入「{cl.list_name}」！")
            else:
                QMessageBox.warning(self, "提示", msg)

    def _load_recommendations(self):
        """加载关联推荐（BR-03：最多5条，按置信度降序）"""
        rec_vegs = self.recommendation_service.get_association_vegetables(
            self.vegetable.veg_id, limit=5
        )

        if not rec_vegs:
            # 无推荐 → 显示纯文本，隐藏滚动区
            self.rec_area.setVisible(False)
            self.rec_empty_label.setVisible(True)
            return

        # 有推荐 → 隐藏空文本，显示滚动区
        self.rec_empty_label.setVisible(False)
        self.rec_area.setVisible(True)

        # 清除旧卡片
        while self.rec_layout.count() > 0:
            item = self.rec_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for veg in rec_vegs:
            card = self._create_veg_card(veg)
            self.rec_layout.addWidget(card)

        # 更新widget宽度以适应卡片数量
        self.rec_widget.setMinimumWidth(
            len(rec_vegs) * (170 + 12) + 20
        )

    def _create_veg_card(self, vegetable) -> QFrame:
        """创建蔬菜推荐卡片"""
        card = QFrame()
        card.setFixedSize(170, 130)
        card.setStyleSheet(
            f"background-color: {CARD_BG}; border-radius: 8px; "
            "border: 1px solid #E0E0E0;"
        )
        card.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        name_label = QLabel(vegetable.name)
        name_label.setStyleSheet(
            "font-weight: bold; font-size: 13px; color: #333;")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(36)
        layout.addWidget(name_label)

        cat_label = QLabel(f"{vegetable.category} | {vegetable.season}")
        cat_label.setStyleSheet("font-size: 11px; color: #999;")
        cat_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(cat_label)

        price_label = QLabel(
            f"¥{vegetable.price_ref:.1f}/斤" if vegetable.price_ref else ""
        )
        price_label.setStyleSheet("font-size: 12px; color: #FF6F00;")
        price_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(price_label)

        # 点击事件
        def on_click(checked=False, veg=vegetable):
            self._navigate_to(veg)

        card.mousePressEvent = on_click
        return card

    def _go_back(self):
        """返回上一页蔬菜，历史为空则关闭窗口"""
        if self._history:
            self.vegetable = self._history.pop()
            self._load_data()
        else:
            self.reject()

    def _record_history(self):
        """记录浏览历史（登录用户）"""
        if self.user_service.is_logged_in and self.browse_history_dao:
            self.browse_history_dao.add_history(
                self.user_service.current_user.user_id,
                self.vegetable.veg_id
            )

    def _navigate_to(self, vegetable):
        """在当前窗口内跳转到新蔬菜"""
        self.search_service.increment_view_count(vegetable.veg_id)
        vegetable.view_count += 1
        self._history.append(self.vegetable)
        self.vegetable = vegetable
        self._load_data()
        self._record_history()
