"""
搜索服务类
封装蔬菜搜索、分类筛选、热门榜单等业务逻辑。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from entity.vegetable import Vegetable
from dao.vegetable_dao import VegetableDAO


class SearchService:
    """搜索业务逻辑服务"""

    def __init__(self):
        self.vegetable_dao = VegetableDAO()

    def fuzzy_search(self, keyword: str) -> List[Vegetable]:
        """
        模糊搜索蔬菜（BR-01：支持名称和别名模糊匹配，不区分大小写）

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的蔬菜列表
        """
        if not keyword or not keyword.strip():
            return []
        return self.vegetable_dao.fuzzy_search(keyword.strip())

    def filter_by_category(self, category: str) -> List[Vegetable]:
        """
        按品类筛选蔬菜

        Args:
            category: 品类名称

        Returns:
            该品类下的蔬菜列表
        """
        if not category:
            return self.vegetable_dao.get_all()
        return self.vegetable_dao.get_by_category(category)

    def filter_by_season(self, season: str) -> List[Vegetable]:
        """
        按季节筛选蔬菜

        Args:
            season: 季节名称

        Returns:
            匹配季节的蔬菜列表
        """
        if not season:
            return self.vegetable_dao.get_all()
        return self.vegetable_dao.get_by_season(season)

    def get_hot_ranking(self, limit: int = 10) -> List[Vegetable]:
        """
        获取热门蔬菜榜单（BR-06：按浏览量+收藏量排序）

        Args:
            limit: 返回数量

        Returns:
            热门蔬菜列表
        """
        return self.vegetable_dao.get_hot_ranking(limit)

    def increment_view_count(self, veg_id: int) -> None:
        """
        增加蔬菜浏览量（BR-06：实时更新）

        Args:
            veg_id: 蔬菜ID
        """
        self.vegetable_dao.increment_view_count(veg_id)

    def get_all_vegetables(self) -> List[Vegetable]:
        """获取所有蔬菜"""
        return self.vegetable_dao.get_all()

    def get_by_id(self, veg_id: int) -> Vegetable:
        """根据ID获取蔬菜"""
        return self.vegetable_dao.get_by_id(veg_id)
