"""
用户服务类
封装用户注册、登录及收藏夹/清单创建等业务逻辑。
"""

import sys
import os
import re
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Tuple, Dict
from entity.user import User
from dao.user_dao import UserDAO
from dao.favorites_dao import FavoritesDAO
from dao.custom_list_dao import CustomListDAO
from utils.password_utils import hash_password, verify_password


class UserService:
    """用户业务逻辑服务"""

    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_SECONDS = 300  # 5 minutes

    def __init__(self):
        self.user_dao = UserDAO()
        self.favorites_dao = FavoritesDAO()
        self.custom_list_dao = CustomListDAO()
        self._current_user: Optional[User] = None
        self._failed_attempts: Dict[str, list] = {}  # {username: [timestamps]}

    @property
    def current_user(self) -> Optional[User]:
        """获取当前登录用户"""
        return self._current_user

    @property
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self._current_user is not None

    @staticmethod
    def _validate_password_strength(password: str) -> Tuple[bool, str]:
        """Validate password meets minimum strength requirements."""
        if not password or len(password) < 8:
            return False, "密码至少需要8个字符"
        if not re.search(r'[a-z]', password):
            return False, "密码需要包含小写字母"
        if not re.search(r'[A-Z]', password):
            return False, "密码需要包含大写字母"
        if not re.search(r'\d', password):
            return False, "密码需要包含数字"
        return True, ""

    @staticmethod
    def _validate_email(email: str) -> bool:
        """Validate email format using a basic regex."""
        if not email:
            return True  # email is optional
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _check_rate_limit(self, username: str) -> Tuple[bool, str]:
        """Check if login attempts are rate-limited for a user."""
        now = time.time()
        attempts = self._failed_attempts.get(username, [])
        # Keep only attempts within the lockout window
        attempts = [t for t in attempts if now - t < self.LOCKOUT_SECONDS]
        self._failed_attempts[username] = attempts

        if len(attempts) >= self.MAX_LOGIN_ATTEMPTS:
            remaining = int(self.LOCKOUT_SECONDS - (now - attempts[0]))
            return False, f"登录尝试次数过多，请在{remaining}秒后重试"
        return True, ""

    def _record_failed_attempt(self, username: str) -> None:
        """Record a failed login attempt."""
        if username not in self._failed_attempts:
            self._failed_attempts[username] = []
        self._failed_attempts[username].append(time.time())

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户登录

        Args:
            username: 用户名
            password: 明文密码

        Returns:
            (是否成功, 消息)
        """
        # Rate limiting check
        ok, msg = self._check_rate_limit(username)
        if not ok:
            return False, msg

        user = self.user_dao.get_by_username(username)
        if user is None:
            self._record_failed_attempt(username)
            return False, "用户名或密码错误"

        if not verify_password(password, user.password_hash):
            self._record_failed_attempt(username)
            return False, "用户名或密码错误"

        # Clear failed attempts on success
        self._failed_attempts.pop(username, None)
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

        # 验证密码强度
        ok, pwd_msg = self._validate_password_strength(password)
        if not ok:
            return False, pwd_msg

        # 检查用户名是否已存在
        if self.user_dao.check_username_exists(username.strip()):
            return False, "用户名已被注册"

        # 检查邮箱格式和唯一性
        if email and not self._validate_email(email.strip()):
            return False, "邮箱格式不正确"
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

        ok, pwd_msg = self._validate_password_strength(new_password)
        if not ok:
            return False, pwd_msg

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
        except Exception:
            return False, "创建失败，请稍后重试"

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
        except Exception:
            return False, "创建失败，请稍后重试"
