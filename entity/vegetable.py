"""
蔬菜实体类
承载蔬菜的所有百科信息，是系统的核心数据单元。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Vegetable:
    """蔬菜实体"""

    veg_id: Optional[int] = None
    name: str = ''
    alias: str = ''
    category: str = ''
    season: str = ''
    image_path: str = ''
    nutrition: str = ''
    purchase_tips: str = ''
    storage_method: str = ''
    price_ref: float = 0.0
    view_count: int = 0
    favorite_count: int = 0
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        """将实体转换为字典"""
        return {
            'veg_id': self.veg_id,
            'veg_name': self.name,
            'alias': self.alias,
            'category': self.category,
            'season': self.season,
            'image_path': self.image_path,
            'nutrition': self.nutrition,
            'purchase_tips': self.purchase_tips,
            'storage_method': self.storage_method,
            'price_ref': self.price_ref,
            'view_count': self.view_count,
            'favorite_count': self.favorite_count,
            'create_time': self.create_time,
            'update_time': self.update_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Vegetable':
        """从字典创建实体"""
        return cls(
            veg_id=data.get('veg_id'),
            name=data.get('veg_name', ''),
            alias=data.get('alias', ''),
            category=data.get('category', ''),
            season=data.get('season', ''),
            image_path=data.get('image_path', ''),
            nutrition=data.get('nutrition', ''),
            purchase_tips=data.get('purchase_tips', ''),
            storage_method=data.get('storage_method', ''),
            price_ref=float(data.get('price_ref', 0) or 0),
            view_count=int(data.get('view_count', 0) or 0),
            favorite_count=int(data.get('favorite_count', 0) or 0),
            create_time=data.get('create_time'),
            update_time=data.get('update_time'),
        )

    @classmethod
    def from_row(cls, row) -> 'Vegetable':
        """从数据库行对象创建实体"""
        if row is None:
            return None
        return cls(
            veg_id=row['veg_id'],
            name=row['veg_name'],
            alias=row['alias'] or '',
            category=row['category'],
            season=row['season'],
            image_path=row['image_path'] if 'image_path' in row.keys() else '',
            nutrition=row['nutrition'] or '',
            purchase_tips=row['purchase_tips'] or '',
            storage_method=row['storage_method'] or '',
            price_ref=float(row['price_ref'] or 0),
            view_count=int(row['view_count'] or 0),
            favorite_count=int(row['favorite_count'] or 0),
            create_time=row['create_time'],
            update_time=row['update_time'],
        )
