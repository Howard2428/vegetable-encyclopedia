"""
收藏服务类
封装蔬菜收藏和自定义清单的业务逻辑。
严格遵循BR-04（需登录）和BR-05（清单上限50种）。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Tuple, Optional
from entity.vegetable import Vegetable
from entity.favorites_list import FavoritesList
from entity.custom_list import CustomList
from dao.favorites_dao import FavoritesDAO
from dao.custom_list_dao import CustomListDAO


class CollectionService:
    """收藏业务逻辑服务"""

    MAX_LIST_ITEMS = 50  # BR-05：单个清单最多50种蔬菜

    def __init__(self):
        self.favorites_dao = FavoritesDAO()
        self.custom_list_dao = CustomListDAO()
        self._user_id: Optional[int] = None

    def set_current_user(self, user_id: Optional[int]) -> None:
        """设置当前操作的用户ID"""
        self._user_id = user_id

    def _check_login(self) -> Tuple[bool, str]:
        """检查登录状态（BR-04）"""
        if self._user_id is None:
            return False, "请先登录后再使用此功能"
        return True, ""

    # ========== 收藏夹操作 ==========

    def add_to_favorites(self, fav_list_id: int, veg_id: int) -> Tuple[bool, str]:
        """
        将蔬菜添加到收藏夹

        Args:
            fav_list_id: 收藏夹ID
            veg_id: 蔬菜ID

        Returns:
            (是否成功, 消息)
        """
        ok, msg = self._check_login()
        if not ok:
            return ok, msg

        try:
            result = self.favorites_dao.add_item(fav_list_id, veg_id)
            if result == 0:
                return False, "该蔬菜已在收藏夹中"
            return True, "已收藏"
        except Exception:
            return False, "收藏失败，请稍后重试"

    def remove_from_favorites(self, fav_list_id: int,
                              veg_id: int) -> Tuple[bool, str]:
        """
        从收藏夹移除蔬菜

        Args:
            fav_list_id: 收藏夹ID
            veg_id: 蔬菜ID

        Returns:
            (是否成功, 消息)
        """
        ok, msg = self._check_login()
        if not ok:
            return ok, msg

        try:
            self.favorites_dao.remove_item(fav_list_id, veg_id)
            return True, "已取消收藏"
        except Exception:
            return False, "取消收藏失败，请稍后重试"

    def get_user_favorites_lists(self) -> List[FavoritesList]:
        """获取当前用户的所有收藏夹"""
        if self._user_id is None:
            return []
        return self.favorites_dao.get_lists_by_user(self._user_id)

    def get_favorites_items(self, fav_list_id: int) -> List[Vegetable]:
        """获取收藏夹中的蔬菜列表"""
        return self.favorites_dao.get_items_by_list(fav_list_id)

    def delete_favorites_list(self, fav_list_id: int) -> Tuple[bool, str]:
        """删除收藏夹"""
        ok, msg = self._check_login()
        if not ok:
            return ok, msg
        try:
            self.favorites_dao.delete_list(fav_list_id)
            return True, "收藏夹已删除"
        except Exception:
            return False, "删除失败，请稍后重试"

    def get_favorited_veg_ids(self) -> List[int]:
        """获取当前用户所有收藏的蔬菜ID"""
        if self._user_id is None:
            return []
        return self.favorites_dao.get_favorited_veg_ids(self._user_id)

    # ========== 自定义清单操作 ==========

    def add_to_custom_list(self, list_id: int, veg_id: int) -> Tuple[bool, str]:
        """
        将蔬菜添加到自定义清单（BR-05：上限50种检查）

        Args:
            list_id: 清单ID
            veg_id: 蔬菜ID

        Returns:
            (是否成功, 消息)
        """
        ok, msg = self._check_login()
        if not ok:
            return ok, msg

        # BR-05：检查清单蔬菜数量上限
        current_count = self.custom_list_dao.count_items(list_id)
        if current_count >= self.MAX_LIST_ITEMS:
            return False, f"该清单已达到{self.MAX_LIST_ITEMS}种蔬菜的上限，无法继续添加"

        try:
            result = self.custom_list_dao.add_item(list_id, veg_id)
            if result == 0:
                return False, "该蔬菜已在清单中"
            return True, "已加入清单"
        except Exception:
            return False, "加入清单失败，请稍后重试"

    def remove_from_custom_list(self, list_id: int,
                                veg_id: int) -> Tuple[bool, str]:
        """
        从自定义清单移除蔬菜

        Args:
            list_id: 清单ID
            veg_id: 蔬菜ID

        Returns:
            (是否成功, 消息)
        """
        ok, msg = self._check_login()
        if not ok:
            return ok, msg

        try:
            self.custom_list_dao.remove_item(list_id, veg_id)
            return True, "已从清单移除"
        except Exception:
            return False, "移除失败，请稍后重试"

    def get_user_custom_lists(self) -> List[CustomList]:
        """获取当前用户的所有自定义清单"""
        if self._user_id is None:
            return []
        return self.custom_list_dao.get_lists_by_user(self._user_id)

    def get_custom_list_items(self, list_id: int) -> List[Vegetable]:
        """获取清单中的蔬菜列表"""
        return self.custom_list_dao.get_items_by_list(list_id)

    def delete_custom_list(self, list_id: int) -> Tuple[bool, str]:
        """删除自定义清单"""
        ok, msg = self._check_login()
        if not ok:
            return ok, msg
        try:
            self.custom_list_dao.delete_list(list_id)
            return True, "清单已删除"
        except Exception as e:
            return False, f"删除失败：{str(e)}"
