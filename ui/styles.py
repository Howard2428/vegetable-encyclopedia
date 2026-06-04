"""
全局样式表（QSS）
统一所有窗口的颜色、字体、按钮、输入框样式。
"""

# 主色调
PRIMARY_COLOR = "#2E7D32"      # 深绿色（蔬菜主题）
PRIMARY_LIGHT = "#4CAF50"      # 浅绿色
ACCENT_COLOR = "#FF6F00"       # 橙色（强调色）
BG_COLOR = "#F5F5F5"           # 背景浅灰
CARD_BG = "#FFFFFF"            # 卡片白色
TEXT_PRIMARY = "#212121"       # 主文字（深灰黑，确保在白色背景上可读）
TEXT_SECONDARY = "#757575"     # 次要文字
TEXT_ON_DARK = "#FFFFFF"       # 深色背景上的白色文字
BORDER_COLOR = "#E0E0E0"       # 边框色

# 全局样式表
GLOBAL_STYLE = f"""
* {{
    font-family: "Microsoft YaHei", "SimHei", "Noto Sans SC", sans-serif;
    font-size: 14px;
    color: {TEXT_PRIMARY};
}}

QMainWindow {{
    background-color: {BG_COLOR};
}}

QDialog {{
    background-color: {BG_COLOR};
}}

QPushButton {{
    background-color: {PRIMARY_COLOR};
    color: {TEXT_ON_DARK};
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 14px;
    font-weight: bold;
    min-height: 32px;
    min-width: 60px;
}}
QPushButton:hover {{
    background-color: {PRIMARY_LIGHT};
}}
QPushButton:pressed {{
    background-color: #1B5E20;
}}
QPushButton:disabled {{
    background-color: #BDBDBD;
    color: #9E9E9E;
}}

/* 次要按钮（白底绿字） */
QPushButton[cssClass="secondary"] {{
    background-color: white;
    color: {PRIMARY_COLOR};
    border: 2px solid {PRIMARY_COLOR};
}}
QPushButton[cssClass="secondary"]:hover {{
    background-color: #E8F5E9;
    color: {PRIMARY_COLOR};
}}

/* 强调按钮（橙色，收藏用） */
QPushButton[cssClass="accent"] {{
    background-color: {ACCENT_COLOR};
    color: white;
}}
QPushButton[cssClass="accent"]:hover {{
    background-color: #FF8F00;
}}

/* 危险按钮（红色，删除用） */
QPushButton[cssClass="danger"] {{
    background-color: #D32F2F;
    color: white;
}}
QPushButton[cssClass="danger"]:hover {{
    background-color: #E53935;
}}

QLineEdit {{
    border: 2px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 14px;
    background-color: white;
    color: {TEXT_PRIMARY};
    min-height: 20px;
}}
QLineEdit:focus {{
    border-color: {PRIMARY_COLOR};
}}

QTextEdit {{
    border: 2px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 14px;
    background-color: white;
    color: {TEXT_PRIMARY};
}}
QTextEdit:focus {{
    border-color: {PRIMARY_COLOR};
}}

QComboBox {{
    border: 2px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 14px;
    background-color: white;
    color: {TEXT_PRIMARY};
    min-height: 20px;
}}
QComboBox:focus {{
    border-color: {PRIMARY_COLOR};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: white;
    color: {TEXT_PRIMARY};
    selection-background-color: {PRIMARY_COLOR};
    selection-color: white;
}}

QLabel {{
    color: {TEXT_PRIMARY};
    background-color: transparent;
}}

/* 标题标签 */
QLabel[cssClass="title"] {{
    font-size: 22px;
    font-weight: bold;
    color: {PRIMARY_COLOR};
}}

QLabel[cssClass="subtitle"] {{
    font-size: 16px;
    font-weight: bold;
    color: {TEXT_PRIMARY};
}}

QLabel[cssClass="section-title"] {{
    font-size: 18px;
    font-weight: bold;
    color: {PRIMARY_COLOR};
    padding: 8px 0px;
}}

QListWidget {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    background-color: white;
    color: {TEXT_PRIMARY};
    outline: none;
}}
QListWidget::item {{
    padding: 10px 15px;
    border-bottom: 1px solid {BORDER_COLOR};
    color: {TEXT_PRIMARY};
}}
QListWidget::item:hover {{
    background-color: #E8F5E9;
}}
QListWidget::item:selected {{
    background-color: {PRIMARY_COLOR};
    color: white;
}}

QTableWidget {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    background-color: white;
    color: {TEXT_PRIMARY};
    gridline-color: {BORDER_COLOR};
    selection-background-color: #E8F5E9;
    selection-color: {TEXT_PRIMARY};
}}
QTableWidget::item {{
    padding: 6px 10px;
    color: {TEXT_PRIMARY};
}}
QHeaderView::section {{
    background-color: {PRIMARY_COLOR};
    color: white;
    padding: 8px 10px;
    border: none;
    font-weight: bold;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    background-color: white;
}}
QTabBar::tab {{
    background-color: #E0E0E0;
    color: {TEXT_PRIMARY};
    padding: 10px 25px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}
QTabBar::tab:selected {{
    background-color: {PRIMARY_COLOR};
    color: white;
}}
QTabBar::tab:hover:!selected {{
    background-color: #C8E6C9;
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QStatusBar {{
    background-color: {PRIMARY_COLOR};
    color: white;
    padding: 4px 10px;
}}
QStatusBar QLabel {{
    color: white;
    background-color: transparent;
}}
QStatusBar::item {{
    border: none;
}}

QGroupBox {{
    border: 2px solid {BORDER_COLOR};
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 20px;
    font-weight: bold;
    color: {TEXT_PRIMARY};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px;
    color: {TEXT_PRIMARY};
}}

QProgressBar {{
    border: 2px solid {BORDER_COLOR};
    border-radius: 6px;
    text-align: center;
    height: 25px;
    background-color: white;
    color: {TEXT_PRIMARY};
}}
QProgressBar::chunk {{
    background-color: {PRIMARY_COLOR};
    border-radius: 4px;
}}

QMessageBox {{
    background-color: white;
}}
QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
}}

QSpinBox, QDoubleSpinBox {{
    border: 2px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 14px;
    background-color: white;
    color: {TEXT_PRIMARY};
    min-height: 20px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {PRIMARY_COLOR};
}}
"""

# ====== 可复用内联样式（用于 setStyleSheet，不经过 QSS property 选择器） ======

SECONDARY_BTN_STYLE = (
    "QPushButton { background-color: white; color: #2E7D32; "
    "border: 2px solid #2E7D32; border-radius: 6px; padding: 8px 14px; "
    "font-size: 14px; font-weight: bold; min-height: 30px; } "
    "QPushButton:hover { background-color: #E8F5E9; }"
)

LINK_BTN_STYLE = (
    "QPushButton { background-color: transparent; color: #757575; "
    "border: none; font-size: 13px; text-decoration: underline; } "
    "QPushButton:hover { color: #424242; }"
)


def nav_btn_style(active: bool, active_bg: str = "#E8F5E9",
                  active_color: str = "#2E7D32") -> str:
    """生成侧边导航按钮样式

    Args:
        active: 是否为当前激活项
        active_bg: 激活态背景色
        active_color: 激活态文字色
    """
    if active:
        return (
            "text-align: left; padding: 12px 18px; border: none; "
            f"border-radius: 0; background-color: {active_bg}; "
            f"color: {active_color}; font-weight: bold; font-size: 14px;"
        )
    return (
        "text-align: left; padding: 12px 18px; border: none; "
        "border-radius: 0; background-color: transparent; "
        "color: #333; font-size: 14px;"
    )
