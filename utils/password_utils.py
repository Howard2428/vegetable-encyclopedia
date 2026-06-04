"""
密码工具模块
使用bcrypt对用户密码进行哈希加密和验证，并提供密码强度检测。
"""

import re
from typing import Tuple

import bcrypt


# 密码强度等级常量
STRENGTH_WEAK = 0
STRENGTH_FAIR = 1
STRENGTH_MEDIUM = 2
STRENGTH_STRONG = 3

STRENGTH_LABELS = ["弱", "较弱", "中等", "强"]
STRENGTH_COLORS = ["#D32F2F", "#FF6F00", "#FBC02D", "#4CAF50"]


def hash_password(password: str) -> str:
    """
    对明文密码进行bcrypt哈希加密

    Args:
        password: 明文密码

    Returns:
        加密后的密码哈希字符串
    """
    # 将密码编码为bytes，生成salt并加密
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    验证明文密码是否与哈希值匹配

    Args:
        password: 用户输入的明文密码
        password_hash: 数据库中存储的密码哈希

    Returns:
        True表示密码匹配，False表示不匹配
    """
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def check_password_strength(password: str) -> Tuple[int, int, str, str]:
    """
    检测密码强度

    规则：
    - 长度 ≥ 8：+25分
    - 同时包含大小写字母：+25分
    - 包含数字：+25分
    - 包含特殊符号：+25分

    Args:
        password: 密码明文

    Returns:
        (score, level, label, color)
        - score: 0-100 分值
        - level: 等级索引 0-3
        - label: "弱" / "较弱" / "中等" / "强"
        - color: 对应的十六进制颜色
    """
    score = 0
    if len(password) >= 8:
        score += 25
    if re.search(r'[a-z]', password) and re.search(r'[A-Z]', password):
        score += 25
    if re.search(r'\d', password):
        score += 25
    if re.search(r'[!@#$%^&*(),.?\":{}|<>_\-]', password):
        score += 25

    level = min(score // 25, 3) if score > 0 else 0
    return score, level, STRENGTH_LABELS[level], STRENGTH_COLORS[level]


def is_weak_password(password: str) -> bool:
    """
    检查密码是否为弱密码（长度<8 或 复杂度不足）

    复杂度要求至少满足以下2项：
    - 同时包含大小写字母
    - 包含数字
    - 包含特殊符号

    Args:
        password: 密码明文

    Returns:
        True 表示密码较弱
    """
    if len(password) < 8:
        return True
    _, level, _, _ = check_password_strength(password)
    return level < STRENGTH_MEDIUM
