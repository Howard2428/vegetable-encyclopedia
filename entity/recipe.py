"""
菜谱实体类
关联规则挖掘的数据源，记录菜谱与食材的关系。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Recipe:
    """菜谱实体"""

    recipe_id: Optional[int] = None
    name: str = ''
    ingredients: List[str] = field(default_factory=list)
    source: str = 'imported'
    create_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        """将实体转换为字典"""
        return {
            'recipe_id': self.recipe_id,
            'name': self.name,
            'ingredients': self.ingredients,
            'source': self.source,
            'create_time': self.create_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Recipe':
        """从字典创建实体"""
        return cls(
            recipe_id=data.get('recipe_id'),
            name=data.get('name', ''),
            ingredients=data.get('ingredients', []),
            source=data.get('source', 'imported'),
            create_time=data.get('create_time'),
        )

    @classmethod
    def from_row(cls, row) -> 'Recipe':
        """从数据库行对象创建实体"""
        if row is None:
            return None
        import json
        return cls(
            recipe_id=row['recipe_id'],
            name=row['name'],
            ingredients=json.loads(row['ingredients'] or '[]'),
            source=row.get('source', 'imported'),
            create_time=row.get('create_time'),
        )
