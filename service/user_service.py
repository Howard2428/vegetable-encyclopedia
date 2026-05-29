"""
用户服务类
封装用户注册、登录及收藏夹/清单创建等业务逻辑。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Tuple
from entity.user import User
from dao.user_dao import UserDAO
from dao.favorites_dao import FavoritesDAO
from dao.custom_list_dao import CustomListDAO
from utils.password_utils import hash_password, verify_password


class UserService:
    """用户业务逻辑服务"""

    def __init__(self):
        self.user_dao = UserDAO()
        self.favorites_dao = FavoritesDAO()
        self.custom_list_dao = CustomListDAO()
        self._current_user: Optional[User] = None

    @property
    def current_user(self) -> Optional[User]:
        """获取当前登录用户"""
        return self._current_user

    @property
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self._current_user is not None

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户登录

        Args:
            username: 用户名
            password: 明文密码

        Returns:
            (是否成功, 消息)
        """
        user = self.user_dao.get_by_username(username)
        if user is None:
            return False, "用户不存在"

        if not verify_password(password, user.password_hash):
            return False, "密码错误"

        # 更新最后登录时间
        self.user_dao.update_last_login(user.user_id)
        self._current_user = user
        return True, f"欢迎回来，{user.username}！"

    def register(self, username: str, password: str,
                 email: str = '') -> Tuple[bool, str]:
        """
        用户注册（BR-08：密码bcrypt加密存储）

        Args:
            username: 用户名
            password: 明文密码
            email: 邮箱

        Returns:
            (是否成功, 消息)
        """
        # 验证用户名
        if not username or len(username.strip()) < 2:
            return False, "用户名至少需要2个字符"
        if len(username) > 50:
            return False, "用户名不能超过50个字符"

        # 验证密码
        if not password or len(password) < 6:
            return False, "密码至少需要6个字符"

        # 检查用户名是否已存在
        if self.user_dao.check_username_exists(username.strip()):
            return False, "用户名已被注册"

        # 检查邮箱
        if email and self.user_dao.check_email_exists(email.strip()):
            return False, "邮箱已被使用"

        # bcrypt加密密码
        password_hash = hash_password(password)

        # 创建用户
        user_id = self.user_dao.create_user(
            username=username.strip(),
            password_hash=password_hash,
            email=email.strip() if email else ''
        )

        if user_id:
            return True, "注册成功！请登录"
        return False, "注册失败，请重试"

    def change_password(self, old_password: str,
                         new_password: str) -> Tuple[bool, str]:
        """
        修改当前用户密码

        Args:
            old_password: 旧密码
            new_password: 新密码

        Returns:
            (是否成功, 消息)
        """
        if not self.is_logged_in:
            return False, "请先登录"

        user = self._current_user
        if not verify_password(old_password, user.password_hash):
            return False, "旧密码不正确"

        if len(new_password) < 8:
            return False, "新密码至少需要8个字符"

        new_hash = hash_password(new_password)
        self.user_dao.update_password(user.user_id, new_hash)
        # 更新当前用户对象中的密码哈希
        user.password_hash = new_hash
        return True, "密码修改成功！"

    def is_admin(self) -> bool:
        """检查当前用户是否为管理员"""
        return self._current_user is not None and self._current_user.is_admin

    def logout(self) -> None:
        """退出登录"""
        self._current_user = None

    def create_favorites_list(self, list_name: str) -> Tuple[bool, str]:
        """
        创建收藏夹

        Args:
            list_name: 收藏夹名称

        Returns:
            (是否成功, 消息)
        """
        if not self.is_logged_in:
            return False, "请先登录"

        if not list_name or not list_name.strip():
            return False, "收藏夹名称不能为空"

        try:
            self.favorites_dao.create_list(
                self._current_user.user_id, list_name.strip()
            )
            return True, f"收藏夹「{list_name}」创建成功"
        except Exception as e:
            return False, f"创建失败：{str(e)}"

    def create_custom_list(self, list_name: str,
                           description: str = '') -> Tuple[bool, str]:
        """
        创建自定义清单（BR-05：检查名称重复）

        Args:
            list_name: 清单名称
            description: 清单描述

        Returns:
            (是否成功, 消息)
        """
        if not self.is_logged_in:
            return False, "请先登录"

        if not list_name or not list_name.strip():
            return False, "清单名称不能为空"

        # BR-05：同一用户下清单名称不能重复
        if self.custom_list_dao.check_name_duplicate(
            self._current_user.user_id, list_name.strip()
        ):
            return False, f"清单名称「{list_name}」已存在，请使用其他名称"

        try:
            self.custom_list_dao.create_list(
                self._current_user.user_id,
                list_name.strip(),
                description.strip() if description else ''
            )
            return True, f"清单「{list_name}」创建成功"
        except Exception as e:
            return False, f"创建失败：{str(e)}"
