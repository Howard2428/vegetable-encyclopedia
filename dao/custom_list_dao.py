"""
自定义清单数据访问对象
负责veg_custom_list和veg_list_item表的数据库操作。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from dao.base_dao import BaseDAO
from entity.custom_list import CustomList
from entity.vegetable import Vegetable


class CustomListDAO(BaseDAO):
    """自定义清单数据访问对象"""

    # ---------- 清单操作 ----------

    def create_list(self, user_id: int, list_name: str,
                    description: str = '') -> int:
        """创建自定义清单"""
        sql = """
            INSERT INTO veg_custom_list (user_id, list_name, description, create_time)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
        """
        return self.execute_update(sql, (user_id, list_name, description))

    def get_lists_by_user(self, user_id: int) -> List[CustomList]:
        """获取用户所有自定义清单"""
        sql = """
            SELECT * FROM veg_custom_list
            WHERE user_id = ?
            ORDER BY create_time DESC
        """
        rows = self.fetch_all(sql, (user_id,))
        return [CustomList.from_row(r) for r in rows]

    def get_list_by_id(self, list_id: int) -> CustomList:
        """根据ID获取清单"""
        sql = "SELECT * FROM veg_custom_list WHERE list_id = ?"
        row = self.fetch_one(sql, (list_id,))
        return CustomList.from_row(row) if row else None

    def check_name_duplicate(self, user_id: int, list_name: str) -> bool:
        """
        检查清单名称是否重复（BR-05：同一用户下不能重复）

        Args:
            user_id: 用户ID
            list_name: 清单名称

        Returns:
            True表示已存在（重复）
        """
        return self.count('veg_custom_list',
                         'user_id = ? AND list_name = ?',
                         (user_id, list_name)) > 0

    def delete_list(self, list_id: int) -> int:
        """删除自定义清单（同时删除其中的明细项）"""
        self.execute_update(
            "DELETE FROM veg_list_item WHERE list_id = ?",
            (list_id,)
        )
        sql = "DELETE FROM veg_custom_list WHERE list_id = ?"
        return self.execute_update(sql, (list_id,))

    # ---------- 清单明细操作 ----------

    def add_item(self, list_id: int, veg_id: int) -> int:
        """向清单添加蔬菜"""
        if self.count('veg_list_item',
                     'list_id = ? AND veg_id = ?',
                     (list_id, veg_id)) > 0:
            return 0

        sql = """
            INSERT INTO veg_list_item (list_id, veg_id, create_time)
            VALUES (?, ?, datetime('now', 'localtime'))
        """
        return self.execute_update(sql, (list_id, veg_id))

    def remove_item(self, list_id: int, veg_id: int) -> int:
        """从清单移除蔬菜"""
        sql = """
            DELETE FROM veg_list_item
            WHERE list_id = ? AND veg_id = ?
        """
        return self.execute_update(sql, (list_id, veg_id))

    def get_items_by_list(self, list_id: int) -> List[Vegetable]:
        """获取清单中的所有蔬菜"""
        sql = """
            SELECT v.* FROM veg_vegetable v
            INNER JOIN veg_list_item li ON v.veg_id = li.veg_id
            WHERE li.list_id = ?
            ORDER BY li.create_time DESC
        """
        rows = self.fetch_all(sql, (list_id,))
        return [Vegetable.from_row(r) for r in rows]

    def count_items(self, list_id: int) -> int:
        """
        统计清单中的蔬菜数量（BR-05：上限50种检查用）

        Args:
            list_id: 清单ID

        Returns:
            蔬菜数量
        """
        return self.count('veg_list_item', 'list_id = ?', (list_id,))

    def is_in_list(self, list_id: int, veg_id: int) -> bool:
        """检查蔬菜是否已在清单中"""
        return self.count('veg_list_item',
                         'list_id = ? AND veg_id = ?',
                         (list_id, veg_id)) > 0
