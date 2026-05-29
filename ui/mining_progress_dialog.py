"""
挖掘进度对话框（模态）
显示关联规则挖掘的实时进度。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from ui.styles import GLOBAL_STYLE


class MiningProgressDialog(QDialog):
    """关联规则挖掘进度对话框"""

    def __init__(self, mining_service, parent=None):
        super().__init__(parent)
        self.mining_service = mining_service
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("关联规则挖掘")
        self.setFixedSize(450, 250)
        self.setStyleSheet(GLOBAL_STYLE)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint |
            Qt.CustomizeWindowHint | Qt.WindowTitleHint
        )
        # 模态，禁止关闭
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)

        # 标题
        self.title_label = QLabel("正在执行关联规则挖掘...")
        self.title_label.setProperty("cssClass", "subtitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # 当前步骤说明
        self.step_label = QLabel("准备中...")
        self.step_label.setAlignment(Qt.AlignCenter)
        self.step_label.setStyleSheet("color: #666;")
        layout.addWidget(self.step_label)

        # 关闭按钮（初始隐藏）
        self.close_btn = QPushButton("确 定")
        self.close_btn.setVisible(False)
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)

    def start_mining(self, min_support: float = 0.01,
                     min_confidence: float = 0.1) -> None:
        """
        开始挖掘

        Args:
            min_support: 最小支持度
            min_confidence: 最小置信度
        """
        # 步数到进度的映射（共8步）
        self._step_progress = {1: 5, 2: 15, 3: 35, 4: 50,
                               5: 65, 6: 75, 7: 90, 8: 100}

        def progress_callback(step: int, message: str) -> None:
            """进度回调"""
            progress = self._step_progress.get(step, step * 12)
            self.progress_bar.setValue(progress)
            self.step_label.setText(message)

        # 使用QTimer异步执行，避免阻塞UI
        def do_mining():
            count, msg = self.mining_service.generate_association_rules(
                min_support=min_support,
                min_confidence=min_confidence,
                progress_callback=progress_callback,
            )
            self._on_complete(count, msg)

        QTimer.singleShot(100, do_mining)

    def _on_complete(self, count: int, msg: str) -> None:
        """挖掘完成"""
        self.progress_bar.setValue(100)
        self.title_label.setText("挖掘完成！")
        self.step_label.setText(msg)
        self.close_btn.setVisible(True)

        if count > 0:
            QMessageBox.information(
                self, "挖掘成功",
                f"关联规则挖掘完成！\n共生成 {count} 条有效规则"
            )
        else:
            QMessageBox.warning(self, "提示", msg)
