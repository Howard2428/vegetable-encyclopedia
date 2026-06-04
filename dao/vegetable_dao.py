"""
蔬菜数据访问对象
负责veg_vegetable表的所有数据库操作。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional
from dao.base_dao import BaseDAO
from entity.vegetable import Vegetable


class VegetableDAO(BaseDAO):
    """蔬菜表数据访问对象"""

    def get_by_id(self, veg_id: int) -> Optional[Vegetable]:
        """根据ID查询蔬菜"""
        sql = "SELECT * FROM veg_vegetable WHERE veg_id = ?"
        row = self.fetch_one(sql, (veg_id,))
        return Vegetable.from_row(row) if row else None

    def get_by_name(self, name: str) -> Optional[Vegetable]:
        """根据名称精确查询蔬菜"""
        sql = "SELECT * FROM veg_vegetable WHERE veg_name = ?"
        row = self.fetch_one(sql, (name,))
        return Vegetable.from_row(row) if row else None

    def get_all(self) -> List[Vegetable]:
        """获取所有蔬菜"""
        sql = "SELECT * FROM veg_vegetable ORDER BY veg_name"
        rows = self.fetch_all(sql)
        return [Vegetable.from_row(r) for r in rows]

    def get_by_category(self, category: str) -> List[Vegetable]:
        """按品类查询蔬菜"""
        sql = "SELECT * FROM veg_vegetable WHERE category = ? ORDER BY veg_name"
        rows = self.fetch_all(sql, (category,))
        return [Vegetable.from_row(r) for r in rows]

    @staticmethod
    def _escape_like(value: str) -> str:
        """Escape SQL LIKE wildcard characters to prevent LIKE injection."""
        return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

    def get_by_season(self, season: str) -> List[Vegetable]:
        """
        按季节查询蔬菜

        Args:
            season: 季节名称（春/夏/秋/冬）

        Returns:
            匹配季节的蔬菜列表（包含全年蔬菜）
        """
        sql = """
            SELECT * FROM veg_vegetable
            WHERE season LIKE ? ESCAPE '\\' OR season = '全年'
            ORDER BY
                CASE WHEN season = ? THEN 0 ELSE 1 END,
                veg_name
        """
        season_pattern = f'%{self._escape_like(season)}%'
        rows = self.fetch_all(sql, (season_pattern, season))
        return [Vegetable.from_row(r) for r in rows]

    def fuzzy_search(self, keyword: str) -> List[Vegetable]:
        """
        模糊搜索蔬菜（BR-01：支持名称和别名模糊匹配，不区分大小写）
        按相关度排序：精确名称 > 名称开头匹配 > 名称包含 > 别名包含

        Args:
            keyword: 搜索关键词

        Returns:
            按相关度排序的蔬菜列表
        """
        sql = """
            SELECT * FROM veg_vegetable
            WHERE LOWER(veg_name) LIKE LOWER(?) ESCAPE '\\'
               OR LOWER(alias) LIKE LOWER(?) ESCAPE '\\'
            ORDER BY
                CASE
                    WHEN LOWER(veg_name) = LOWER(?) THEN 0
                    WHEN LOWER(veg_name) LIKE LOWER(?) ESCAPE '\\' THEN 1
                    WHEN LOWER(veg_name) LIKE LOWER(?) ESCAPE '\\' THEN 2
                    ELSE 3
                END,
                veg_name
        """
        escaped = self._escape_like(keyword)
        pattern = f'%{escaped}%'
        prefix_pattern = f'{escaped}%'
        rows = self.fetch_all(sql, (
            pattern, pattern,           # WHERE: 名称或别名包含
            keyword,                     # ORDER 0: 名称精确匹配
            prefix_pattern,              # ORDER 1: 名称以关键词开头
            pattern,                     # ORDER 2: 名称包含关键词
        ))
        return [Vegetable.from_row(r) for r in rows]

    def get_hot_ranking(self, limit: int = 10) -> List[Vegetable]:
        """
        获取热门蔬菜榜单（BR-06：按浏览量+收藏量综合排序）

        Args:
            limit: 返回数量

        Returns:
            热门蔬菜列表
        """
        sql = """
            SELECT * FROM veg_vegetable
            ORDER BY (view_count + favorite_count) DESC, veg_name
            LIMIT ?
        """
        rows = self.fetch_all(sql, (limit,))
        return [Vegetable.from_row(r) for r in rows]

    def get_value_ranking(self, limit: int = 10) -> List[Vegetable]:
        """
        获取最具性价比蔬菜排行榜
        性价比公式：(收藏数 + 浏览数 × 0.5 + 1) / (参考价格)²
        以价格为主导因素（平方放大低价优势），人气作为辅助调节。
        白菜、豆芽、土豆等低价高营养蔬菜自然排在前面。

        Args:
            limit: 返回数量

        Returns:
            按性价比从高到低排序的蔬菜列表
        """
        sql = """
            SELECT * FROM veg_vegetable
            ORDER BY
                CASE WHEN price_ref > 0
                     THEN (favorite_count + view_count * 0.5 + 1) / (price_ref * price_ref)
                     ELSE 0
                END DESC,
                veg_name
            LIMIT ?
        """
        rows = self.fetch_all(sql, (limit,))
        return [Vegetable.from_row(r) for r in rows]

    def increment_view_count(self, veg_id: int) -> None:
        """增加蔬菜浏览量（BR-06：实时更新）"""
        sql = """
            UPDATE veg_vegetable
            SET view_count = view_count + 1,
                update_time = datetime('now', 'localtime')
            WHERE veg_id = ?
        """
        self.execute_update(sql, (veg_id,))

    def increment_favorite_count(self, veg_id: int) -> None:
        """增加蔬菜收藏量"""
        sql = """
            UPDATE veg_vegetable
            SET favorite_count = favorite_count + 1,
                update_time = datetime('now', 'localtime')
            WHERE veg_id = ?
        """
        self.execute_update(sql, (veg_id,))

    def decrement_favorite_count(self, veg_id: int) -> None:
        """减少蔬菜收藏量"""
        sql = """
            UPDATE veg_vegetable
            SET favorite_count = MAX(favorite_count - 1, 0),
                update_time = datetime('now', 'localtime')
            WHERE veg_id = ?
        """
        self.execute_update(sql, (veg_id,))

    def insert(self, vegetable: Vegetable) -> int:
        """新增蔬菜"""
        sql = """
            INSERT INTO veg_vegetable
            (veg_name, alias, category, season, image_path, nutrition, purchase_tips,
             storage_method, price_ref, create_time, update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'), datetime('now', 'localtime'))
        """
        return self.execute_update(sql, (
            vegetable.name, vegetable.alias, vegetable.category,
            vegetable.season, vegetable.image_path,
            vegetable.nutrition, vegetable.purchase_tips,
            vegetable.storage_method, vegetable.price_ref
        ))

    def update(self, vegetable: Vegetable) -> int:
        """更新蔬菜信息"""
        sql = """
            UPDATE veg_vegetable
            SET veg_name = ?, alias = ?, category = ?, season = ?,
                image_path = ?, nutrition = ?, purchase_tips = ?, storage_method = ?,
                price_ref = ?, update_time = datetime('now', 'localtime')
            WHERE veg_id = ?
        """
        return self.execute_update(sql, (
            vegetable.name, vegetable.alias, vegetable.category,
            vegetable.season, vegetable.image_path,
            vegetable.nutrition, vegetable.purchase_tips,
            vegetable.storage_method, vegetable.price_ref, vegetable.veg_id
        ))

    def delete(self, veg_id: int) -> int:
        """删除蔬菜"""
        sql = "DELETE FROM veg_vegetable WHERE veg_id = ?"
        return self.execute_update(sql, (veg_id,))

    def reset_all_stats(self) -> int:
        """重置所有蔬菜的浏览量和收藏量（系统重置）"""
        sql = """
            UPDATE veg_vegetable
            SET view_count = 0, favorite_count = 0,
                update_time = datetime('now', 'localtime')
        """
        return self.execute_update(sql)

    def count(self, table='veg_vegetable', where='', params=()):
        """统计蔬菜总数"""
        return super().count(table, where, params)
