"""
收藏夹数据访问对象
负责veg_favorites_list和veg_favorite_item表的数据库操作。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from dao.base_dao import BaseDAO
from entity.favorites_list import FavoritesList
from entity.vegetable import Vegetable


class FavoritesDAO(BaseDAO):
    """收藏夹数据访问对象"""

    # ---------- 收藏夹操作 ----------

    def create_list(self, user_id: int, list_name: str) -> int:
        """创建收藏夹"""
        sql = """
            INSERT INTO veg_favorites_list (user_id, list_name, create_time)
            VALUES (?, ?, datetime('now', 'localtime'))
        """
        return self.execute_update(sql, (user_id, list_name))

    def get_lists_by_user(self, user_id: int) -> List[FavoritesList]:
        """获取用户所有收藏夹"""
        sql = """
            SELECT * FROM veg_favorites_list
            WHERE user_id = ?
            ORDER BY create_time DESC
        """
        rows = self.fetch_all(sql, (user_id,))
        return [FavoritesList.from_row(r) for r in rows]

    def get_list_by_id(self, fav_list_id: int) -> FavoritesList:
        """根据ID获取收藏夹"""
        sql = "SELECT * FROM veg_favorites_list WHERE fav_list_id = ?"
        row = self.fetch_one(sql, (fav_list_id,))
        return FavoritesList.from_row(row) if row else None

    def delete_list(self, fav_list_id: int) -> int:
        """删除收藏夹（同时删除其中的收藏项）"""
        # 先删除收藏明细
        self.execute_update(
            "DELETE FROM veg_favorite_item WHERE fav_list_id = ?",
            (fav_list_id,)
        )
        # 再删除收藏夹
        sql = "DELETE FROM veg_favorites_list WHERE fav_list_id = ?"
        return self.execute_update(sql, (fav_list_id,))

    # ---------- 收藏明细操作 ----------

    def add_item(self, fav_list_id: int, veg_id: int) -> int:
        """向收藏夹添加蔬菜"""
        # 检查是否已存在
        check_sql = """
            SELECT COUNT(*) as cnt FROM veg_favorite_item
            WHERE fav_list_id = ? AND veg_id = ?
        """
        row = self.fetch_one(check_sql, (fav_list_id, veg_id))
        if row and row['cnt'] > 0:
            return 0  # 已存在，不重复添加

        sql = """
            INSERT INTO veg_favorite_item (fav_list_id, veg_id, create_time)
            VALUES (?, ?, datetime('now', 'localtime'))
        """
        return self.execute_update(sql, (fav_list_id, veg_id))

    def remove_item(self, fav_list_id: int, veg_id: int) -> int:
        """从收藏夹移除蔬菜"""
        sql = """
            DELETE FROM veg_favorite_item
            WHERE fav_list_id = ? AND veg_id = ?
        """
        return self.execute_update(sql, (fav_list_id, veg_id))

    def get_items_by_list(self, fav_list_id: int) -> List[Vegetable]:
        """获取收藏夹中的所有蔬菜"""
        sql = """
            SELECT v.* FROM veg_vegetable v
            INNER JOIN veg_favorite_item fi ON v.veg_id = fi.veg_id
            WHERE fi.fav_list_id = ?
            ORDER BY fi.create_time DESC
        """
        rows = self.fetch_all(sql, (fav_list_id,))
        return [Vegetable.from_row(r) for r in rows]

    def is_favorited(self, fav_list_id: int, veg_id: int) -> bool:
        """检查蔬菜是否已在收藏夹中"""
        sql = """
            SELECT COUNT(*) as cnt FROM veg_favorite_item
            WHERE fav_list_id = ? AND veg_id = ?
        """
        row = self.fetch_one(sql, (fav_list_id, veg_id))
        return row['cnt'] > 0 if row else False

    def get_favorited_veg_ids(self, user_id: int) -> List[int]:
        """获取用户所有收藏的蔬菜ID列表（用于UI状态同步）"""
        sql = """
            SELECT DISTINCT fi.veg_id FROM veg_favorite_item fi
            INNER JOIN veg_favorites_list fl ON fi.fav_list_id = fl.fav_list_id
            WHERE fl.user_id = ?
        """
        rows = self.fetch_all(sql, (user_id,))
        return [row['veg_id'] for row in rows]
