"""
关联规则数据访问对象
负责veg_association_rule表的数据库操作。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from dao.base_dao import BaseDAO
from entity.association_rule import AssociationRule


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
        批量插入关联规则

        Args:
            rules: 规则字典列表，每个字典包含 ante_veg_id, post_veg_id,
                   support, confidence, lift

        Returns:
            插入的记录数
        """
        sql = """
            INSERT INTO veg_association_rule
            (ante_veg_id, post_veg_id, support, confidence, lift, create_time)
            VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
        """
        count = 0
        conn = self.get_connection()
        cursor = conn.cursor()
        for rule in rules:
            cursor.execute(sql, (
                rule['ante_veg_id'],
                rule['post_veg_id'],
                rule['support'],
                rule['confidence'],
                rule['lift'],
            ))
            count += 1
        conn.commit()
        return count

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

    def count(self) -> int:
        """统计关联规则总数"""
        sql = "SELECT COUNT(*) as cnt FROM veg_association_rule"
        row = self.fetch_one(sql)
        return row['cnt'] if row else 0
