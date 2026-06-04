"""
浏览历史数据访问对象
负责veg_browse_history表的数据库操作。
"""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from dao.base_dao import BaseDAO
from entity.vegetable import Vegetable

logger = logging.getLogger(__name__)


class BrowseHistoryDAO(BaseDAO):
    """浏览历史数据访问对象"""

    def add_history(self, user_id: int, veg_id: int) -> None:
        """记录一条浏览历史"""
        try:
            # 去重：删除同一用户+同一蔬菜的旧记录
            sql_dedup = """
                DELETE FROM veg_browse_history
                WHERE user_id = ? AND veg_id = ?
            """
            self.execute_update(sql_dedup, (user_id, veg_id))

            # 插入新记录
            sql = """
                INSERT INTO veg_browse_history (user_id, veg_id, browse_time)
                VALUES (?, ?, datetime('now', 'localtime'))
            """
            self.execute_update(sql, (user_id, veg_id))

            # 只保留最近20条
            sql_trim = """
                DELETE FROM veg_browse_history
                WHERE history_id NOT IN (
                    SELECT history_id FROM veg_browse_history
                    WHERE user_id = ?
                    ORDER BY browse_time DESC
                    LIMIT 20
                ) AND user_id = ?
            """
            self.execute_update(sql_trim, (user_id, user_id))
        except RuntimeError as e:
            logger.error("记录浏览历史失败(user_id=%d, veg_id=%d): %s",
                         user_id, veg_id, e)

    def get_history(self, user_id: int, limit: int = 20) -> List[Vegetable]:
        """获取用户最近的浏览历史"""
        sql = """
            SELECT v.* FROM veg_vegetable v
            INNER JOIN veg_browse_history h ON v.veg_id = h.veg_id
            WHERE h.user_id = ?
            ORDER BY h.browse_time DESC
            LIMIT ?
        """
        rows = self.fetch_all(sql, (user_id, limit))
        return [Vegetable.from_row(r) for r in rows]

    def clear_history(self, user_id: int) -> int:
        """清除用户的浏览历史"""
        sql = "DELETE FROM veg_browse_history WHERE user_id = ?"
        return self.execute_update(sql, (user_id,))

    def get_count(self, user_id: int) -> int:
        """统计用户浏览历史条数"""
        sql = "SELECT COUNT(*) as cnt FROM veg_browse_history WHERE user_id = ?"
        row = self.fetch_one(sql, (user_id,))
        return row['cnt'] if row else 0
