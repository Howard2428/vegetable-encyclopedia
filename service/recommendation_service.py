"""
推荐服务类
封装时令推荐、关联推荐等业务逻辑。
"""

import sys
import os
import logging
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from entity.vegetable import Vegetable
from dao.vegetable_dao import VegetableDAO
from dao.association_rule_dao import AssociationRuleDAO

logger = logging.getLogger(__name__)


class RecommendationService:
    """推荐业务逻辑服务"""

    # 月份到季节的映射
    MONTH_SEASON_MAP = {
        1: '冬', 2: '冬', 3: '春', 4: '春',
        5: '夏', 6: '夏', 7: '夏', 8: '夏',
        9: '秋', 10: '秋', 11: '秋',
        12: '冬',
    }

    def __init__(self):
        self.vegetable_dao = VegetableDAO()
        self.rule_dao = AssociationRuleDAO()

    def get_current_season(self) -> str:
        """获取当前系统月份对应的季节"""
        month = datetime.now().month
        return self.MONTH_SEASON_MAP.get(month, '全年')

    def get_current_month(self) -> int:
        """获取当前系统月份"""
        return datetime.now().month

    def get_seasonal_vegetables(self, month: int = None) -> List[Vegetable]:
        """
        获取当月时令蔬菜（BR-02：按当前系统月份自动匹配）

        Args:
            month: 月份（默认当前月份）

        Returns:
            当月时令蔬菜列表，当月应季蔬菜优先
        """
        if month is None:
            month = self.get_current_month()

        season = self.MONTH_SEASON_MAP.get(month, '全年')
        return self.vegetable_dao.get_by_season(season)

    def get_association_vegetables(self, veg_id: int,
                                   limit: int = 5) -> List[Vegetable]:
        """
        获取关联推荐蔬菜（BR-03：最多5条，按置信度降序）

        Args:
            veg_id: 当前蔬菜ID（作为前项）
            limit: 返回数量上限

        Returns:
            推荐的蔬菜列表
        """
        rules = self.rule_dao.get_by_ante_veg(veg_id, limit)
        vegetables = []
        seen_ids = set()

        for rule in rules:
            if rule.post_veg_id not in seen_ids:
                veg = self.vegetable_dao.get_by_id(rule.post_veg_id)
                if veg:
                    vegetables.append(veg)
                    seen_ids.add(rule.post_veg_id)

        return vegetables

    def increment_favorite_count(self, veg_id: int) -> None:
        """增加蔬菜收藏量（BR-06：实时更新）"""
        try:
            self.vegetable_dao.increment_favorite_count(veg_id)
        except RuntimeError as e:
            logger.error("更新收藏量失败(veg_id=%d): %s", veg_id, e)

    def decrement_favorite_count(self, veg_id: int) -> None:
        """减少蔬菜收藏量"""
        try:
            self.vegetable_dao.decrement_favorite_count(veg_id)
        except RuntimeError as e:
            logger.error("更新收藏量失败(veg_id=%d): %s", veg_id, e)

    def get_rule_count(self) -> int:
        """获取当前规则库数量"""
        return self.rule_dao.count()
