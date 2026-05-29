"""
图片工具模块 — 加载蔬菜图片
"""

import os
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


def get_image_dir() -> str:
    """获取图片存储目录"""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data', 'images'
    )


def load_vegetable_image(vegetable, size: int = 200) -> QPixmap:
    """
    加载蔬菜图片，找不到返回空QPixmap

    查找顺序：
    1. vegetable.image_path（数据库绝对/相对路径）
    2. data/images/{veg_name}.jpg/.png
    3. data/images/{veg_id}.jpg/.png
    """
    candidates = []

    if vegetable.image_path and os.path.exists(vegetable.image_path):
        candidates.append(vegetable.image_path)

    img_dir = get_image_dir()
    name = vegetable.name
    veg_id = vegetable.veg_id

    for base in [name, str(veg_id)]:
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            path = os.path.join(img_dir, base + ext)
            if os.path.exists(path):
                candidates.append(path)

    for path in candidates:
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            return pixmap.scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

    return QPixmap()
