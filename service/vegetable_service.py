"""
蔬菜管理服务类
封装蔬菜信息CRUD操作的业务逻辑。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Tuple, Optional
from entity.vegetable import Vegetable
from dao.vegetable_dao import VegetableDAO


class VegetableService:
    """蔬菜管理业务逻辑服务"""

    VALID_CATEGORIES = ['叶菜类', '根茎类', '瓜茄类', '菌菇类', '豆类', '其他']

    def __init__(self):
        self.vegetable_dao = VegetableDAO()

    def get_vegetable_by_id(self, veg_id: int) -> Optional[Vegetable]:
        """根据ID获取蔬菜"""
        return self.vegetable_dao.get_by_id(veg_id)

    def add_vegetable(self, vegetable: Vegetable) -> Tuple[bool, str]:
        """
        新增蔬菜

        Args:
            vegetable: 蔬菜实体

        Returns:
            (是否成功, 消息)
        """
        # 验证必填字段
        if not vegetable.name or not vegetable.name.strip():
            return False, "蔬菜名称不能为空"

        # 检查名称唯一性
        existing = self.vegetable_dao.get_by_name(vegetable.name.strip())
        if existing:
            return False, f"蔬菜「{vegetable.name}」已存在"

        # 验证品类
        if vegetable.category not in self.VALID_CATEGORIES:
            return False, f"无效的品类：{vegetable.category}"

        try:
            vegetable.name = vegetable.name.strip()
            vegetable.alias = vegetable.alias.strip() if vegetable.alias else ''
            self.vegetable_dao.insert(vegetable)
            return True, f"蔬菜「{vegetable.name}」添加成功"
        except Exception as e:
            return False, f"添加失败：{str(e)}"

    def update_vegetable(self, vegetable: Vegetable) -> Tuple[bool, str]:
        """
        编辑蔬菜信息

        Args:
            vegetable: 蔬菜实体（需包含veg_id）

        Returns:
            (是否成功, 消息)
        """
        if not vegetable.veg_id:
            return False, "蔬菜ID不能为空"
        if not vegetable.name or not vegetable.name.strip():
            return False, "蔬菜名称不能为空"

        # 验证品类
        if vegetable.category not in self.VALID_CATEGORIES:
            return False, f"无效的品类：{vegetable.category}"

        try:
            self.vegetable_dao.update(vegetable)
            return True, f"蔬菜「{vegetable.name}」更新成功"
        except Exception as e:
            return False, f"更新失败：{str(e)}"

    def delete_vegetable(self, veg_id: int) -> Tuple[bool, str]:
        """
        删除蔬菜

        Args:
            veg_id: 蔬菜ID

        Returns:
            (是否成功, 消息)
        """
        veg = self.vegetable_dao.get_by_id(veg_id)
        if not veg:
            return False, "蔬菜不存在"

        try:
            self.vegetable_dao.delete(veg_id)
            return True, f"蔬菜「{veg.name}」已删除"
        except Exception as e:
            return False, f"删除失败：{str(e)}"

    def get_all_vegetables(self) -> List[Vegetable]:
        """获取所有蔬菜"""
        return self.vegetable_dao.get_all()

    @classmethod
    def get_valid_categories(cls) -> List[str]:
        """获取有效品类列表"""
        return cls.VALID_CATEGORIES
