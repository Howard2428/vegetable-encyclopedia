"""
蔬菜管理服务类
封装蔬菜信息CRUD操作的业务逻辑。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Tuple, Optional
from entity.vegetable import Vegetable
from entity.cooking_method import CookingMethod
from dao.vegetable_dao import VegetableDAO
from dao.cooking_method_dao import CookingMethodDAO


class VegetableService:
    """蔬菜管理业务逻辑服务"""

    VALID_CATEGORIES = ['叶菜类', '根茎类', '瓜茄类', '菌菇类', '豆类', '其他']

    def __init__(self):
        self.vegetable_dao = VegetableDAO()
        self.cooking_method_dao = CookingMethodDAO()

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
        except Exception:
            return False, "添加失败，请稍后重试"

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
        except Exception:
            return False, "更新失败，请稍后重试"

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
        except Exception:
            return False, "删除失败，请稍后重试"

    def get_all_vegetables(self) -> List[Vegetable]:
        """获取所有蔬菜"""
        return self.vegetable_dao.get_all()

    # ==================== 烹饪方法管理 ====================

    def get_cooking_methods(self, veg_id: int) -> List[CookingMethod]:
        """获取某个蔬菜的所有烹饪方法"""
        return self.cooking_method_dao.get_by_veg_id(veg_id)

    def add_cooking_method(self, method: CookingMethod) -> Tuple[bool, str]:
        """添加一条烹饪方法"""
        if not method.method_name or not method.method_name.strip():
            return False, "烹饪方法名称不能为空"
        if not method.veg_id:
            return False, "蔬菜ID不能为空"
        try:
            method.method_name = method.method_name.strip()
            method.cooking_time = method.cooking_time.strip() if method.cooking_time else ''
            method.ingredients = method.ingredients.strip() if method.ingredients else ''
            self.cooking_method_dao.insert(method)
            return True, "烹饪方法添加成功"
        except Exception:
            return False, "添加失败，请稍后重试"

    def update_cooking_method(self, method: CookingMethod) -> Tuple[bool, str]:
        """更新一条烹饪方法"""
        if not method.method_id:
            return False, "烹饪方法ID不能为空"
        if not method.method_name or not method.method_name.strip():
            return False, "烹饪方法名称不能为空"
        try:
            method.method_name = method.method_name.strip()
            method.cooking_time = method.cooking_time.strip() if method.cooking_time else ''
            method.ingredients = method.ingredients.strip() if method.ingredients else ''
            self.cooking_method_dao.update(method)
            return True, "烹饪方法更新成功"
        except Exception:
            return False, "更新失败，请稍后重试"

    def delete_cooking_method(self, method_id: int) -> Tuple[bool, str]:
        """删除一条烹饪方法"""
        try:
            self.cooking_method_dao.delete(method_id)
            return True, "烹饪方法已删除"
        except Exception:
            return False, "删除失败，请稍后重试"

    def replace_cooking_methods(self, veg_id: int,
                                methods: List[CookingMethod]) -> Tuple[bool, str]:
        """批量替换某个蔬菜的烹饪方法"""
        try:
            self.cooking_method_dao.replace_all_for_veg(veg_id, methods)
            return True, f"已更新 {len(methods)} 条烹饪方法"
        except Exception as e:
            return False, f"更新失败：{str(e)}"

    @classmethod
    def get_valid_categories(cls) -> List[str]:
        """获取有效品类列表"""
        return cls.VALID_CATEGORIES
