"""
烹饪方法实体类
承载蔬菜的推荐烹饪方式、时间和辅料信息。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CookingMethod:
    """烹饪方法实体"""

    method_id: Optional[int] = None
    veg_id: int = 0
    method_name: str = ''
    cooking_time: str = ''
    ingredients: str = ''
    create_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        """将实体转换为字典"""
        return {
            'method_id': self.method_id,
            'veg_id': self.veg_id,
            'method_name': self.method_name,
            'cooking_time': self.cooking_time,
            'ingredients': self.ingredients,
            'create_time': self.create_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CookingMethod':
        """从字典创建实体"""
        return cls(
            method_id=data.get('method_id'),
            veg_id=int(data.get('veg_id', 0) or 0),
            method_name=data.get('method_name', ''),
            cooking_time=data.get('cooking_time', ''),
            ingredients=data.get('ingredients', ''),
            create_time=data.get('create_time'),
        )

    @classmethod
    def from_row(cls, row) -> 'CookingMethod':
        """从数据库行对象创建实体"""
        if row is None:
            return None
        return cls(
            method_id=row['method_id'],
            veg_id=row['veg_id'],
            method_name=row['method_name'],
            cooking_time=row['cooking_time'] or '',
            ingredients=row['ingredients'] or '',
            create_time=row['create_time'],
        )
