"""
关联规则数据访问对象
负责veg_association_rule表的数据库操作。
"""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from dao.base_dao import BaseDAO
from entity.association_rule import AssociationRule

logger = logging.getLogger(__name__)


class AssociationRuleDAO(BaseDAO):
    """关联规则数据访问对象"""

    def clear_all(self) -> int:
        """
        清空所有关联规则（BR-07：挖掘前先清空旧规则）

        Returns:
            删除的记录数
        """
        sql = "DELETE FROM veg_association_rule"
        return self.execute_update(sql)

    def batch_insert(self, rules: List[dict]) -> int:
        """
        批量插入关联规则（事务安全：全部成功或全部回滚）

        Args:
            rules: 规则字典列表，每个字典包含 ante_veg_id, post_veg_id,
                   support, confidence, lift

        Returns:
            插入的记录数

        Raises:
            RuntimeError: 当批量插入失败时（已回滚）
        """
        sql = """
            INSERT INTO veg_association_rule
            (ante_veg_id, post_veg_id, support, confidence, lift, create_time)
            VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            for rule in rules:
                cursor.execute(sql, (
                    rule['ante_veg_id'],
                    rule['post_veg_id'],
                    rule['support'],
                    rule['confidence'],
                    rule['lift'],
                ))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error("关联规则批量插入失败，已回滚: %s", e)
            raise RuntimeError(f"关联规则批量插入失败: {e}") from e
        return len(rules)

    def get_by_ante_veg(self, veg_id: int, limit: int = 5) -> List[AssociationRule]:
        """
        根据前项蔬菜ID获取关联规则（BR-03：按置信度降序，最多5条）

        Args:
            veg_id: 前项蔬菜ID
            limit: 返回数量上限

        Returns:
            关联规则列表，按置信度降序排列
        """
        sql = """
            SELECT * FROM veg_association_rule
            WHERE ante_veg_id = ?
            ORDER BY confidence DESC
            LIMIT ?
        """
        rows = self.fetch_all(sql, (veg_id, limit))
        return [AssociationRule.from_row(r) for r in rows]

    def get_all(self) -> List[AssociationRule]:
        """获取所有关联规则"""
        sql = "SELECT * FROM veg_association_rule ORDER BY confidence DESC"
        rows = self.fetch_all(sql)
        return [AssociationRule.from_row(r) for r in rows]

    def count(self, table='veg_association_rule', where='', params=()):
        """统计关联规则总数"""
        return super().count(table, where, params)
