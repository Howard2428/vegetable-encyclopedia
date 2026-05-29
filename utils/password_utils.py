"""
密码工具模块
使用bcrypt对用户密码进行哈希加密和验证。
"""

import bcrypt


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
