"""
烹饪方法数据访问对象
负责veg_cooking_method表的所有数据库操作。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional
from dao.base_dao import BaseDAO
from entity.cooking_method import CookingMethod


class CookingMethodDAO(BaseDAO):
    """烹饪方法表数据访问对象"""

    def get_by_veg_id(self, veg_id: int) -> List[CookingMethod]:
        """根据蔬菜ID查询所有烹饪方法"""
        sql = """
            SELECT * FROM veg_cooking_method
            WHERE veg_id = ?
            ORDER BY method_id
        """
        rows = self.fetch_all(sql, (veg_id,))
        return [CookingMethod.from_row(r) for r in rows]

    def get_by_id(self, method_id: int) -> Optional[CookingMethod]:
        """根据ID查询单条烹饪方法"""
        sql = "SELECT * FROM veg_cooking_method WHERE method_id = ?"
        row = self.fetch_one(sql, (method_id,))
        return CookingMethod.from_row(row) if row else None

    def insert(self, method: CookingMethod) -> int:
        """新增烹饪方法"""
        sql = """
            INSERT INTO veg_cooking_method
            (veg_id, method_name, cooking_time, ingredients, create_time)
            VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
        """
        return self.execute_update(sql, (
            method.veg_id, method.method_name,
            method.cooking_time, method.ingredients
        ))

    def update(self, method: CookingMethod) -> int:
        """更新烹饪方法"""
        sql = """
            UPDATE veg_cooking_method
            SET method_name = ?, cooking_time = ?, ingredients = ?
            WHERE method_id = ?
        """
        return self.execute_update(sql, (
            method.method_name, method.cooking_time,
            method.ingredients, method.method_id
        ))

    def delete(self, method_id: int) -> int:
        """删除单条烹饪方法"""
        sql = "DELETE FROM veg_cooking_method WHERE method_id = ?"
        return self.execute_update(sql, (method_id,))

    def delete_by_veg_id(self, veg_id: int) -> int:
        """删除某蔬菜的所有烹饪方法"""
        sql = "DELETE FROM veg_cooking_method WHERE veg_id = ?"
        return self.execute_update(sql, (veg_id,))

    def insert_batch(self, methods: List[CookingMethod]) -> int:
        """批量新增烹饪方法"""
        count = 0
        for method in methods:
            self.insert(method)
            count += 1
        return count

    def replace_all_for_veg(self, veg_id: int,
                            methods: List[CookingMethod]) -> int:
        """
        替换某个蔬菜的全部烹饪方法（先删后插）

        Args:
            veg_id: 蔬菜ID
            methods: 新的烹饪方法列表

        Returns:
            插入的条数
        """
        self.delete_by_veg_id(veg_id)
        count = 0
        for method in methods:
            method.veg_id = veg_id
            self.insert(method)
            count += 1
        return count
