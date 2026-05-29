"""
关联规则实体类
存储离线挖掘生成的蔬菜搭配关联规则。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AssociationRule:
    """关联规则实体"""

    rule_id: Optional[int] = None
    ante_veg_id: int = 0          # 前项蔬菜ID（A→B中的A）
    post_veg_id: int = 0          # 后项蔬菜ID（A→B中的B）
    support: float = 0.0          # 支持度
    confidence: float = 0.0       # 置信度（排序依据）
    lift: float = 0.0             # 提升度
    create_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        """将实体转换为字典"""
        return {
            'rule_id': self.rule_id,
            'ante_veg_id': self.ante_veg_id,
            'post_veg_id': self.post_veg_id,
            'support': self.support,
            'confidence': self.confidence,
            'lift': self.lift,
            'create_time': self.create_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AssociationRule':
        """从字典创建实体"""
        return cls(
            rule_id=data.get('rule_id'),
            ante_veg_id=data.get('ante_veg_id', 0),
            post_veg_id=data.get('post_veg_id', 0),
            support=float(data.get('support', 0) or 0),
            confidence=float(data.get('confidence', 0) or 0),
            lift=float(data.get('lift', 0) or 0),
            create_time=data.get('create_time'),
        )

    @classmethod
    def from_row(cls, row) -> 'AssociationRule':
        """从数据库行对象创建实体"""
        if row is None:
            return None
        return cls(
            rule_id=row['rule_id'],
            ante_veg_id=row['ante_veg_id'],
            post_veg_id=row['post_veg_id'],
            support=float(row['support'] or 0),
            confidence=float(row['confidence'] or 0),
            lift=float(row['lift'] or 0),
            create_time=row['create_time'],
        )
