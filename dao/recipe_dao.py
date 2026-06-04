"""
菜谱数据访问对象
负责菜谱数据的存取操作（SQLite中使用内存表或在文件中存储）。
菜谱数据主要用于关联规则挖掘，以JSON文件为主要存储形式。
"""

import sys
import os
import json
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict
from dao.base_dao import BaseDAO

logger = logging.getLogger(__name__)


class RecipeDAO(BaseDAO):
    """菜谱数据访问对象"""

    def __init__(self):
        super().__init__()
        # 创建菜谱表（如果数据库中不存在的话）
        self._ensure_table()

    def _ensure_table(self):
        """确保菜谱表存在（数据库未初始化时记录警告）"""
        sql = """
            CREATE TABLE IF NOT EXISTS veg_recipe (
                recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                ingredients TEXT NOT NULL,
                source VARCHAR(50) DEFAULT 'imported',
                create_time DATETIME DEFAULT (datetime('now', 'localtime'))
            )
        """
        try:
            self.execute_update(sql)
        except RuntimeError as e:
            logger.warning("菜谱表创建跳过（数据库可能尚未初始化）: %s", e)

    def import_from_json(self, filepath: str) -> int:
        """
        从JSON文件导入菜谱数据

        Args:
            filepath: JSON文件路径

        Returns:
            导入的菜谱数量

        Raises:
            FileNotFoundError: 当JSON文件不存在时
            json.JSONDecodeError: 当JSON文件格式无效时
        """
        self._ensure_table()  # 确保表存在
        with open(filepath, 'r', encoding='utf-8') as f:
            recipes = json.load(f)

        count = 0
        skipped = 0
        for recipe in recipes:
            name = recipe.get('name', '')
            if not name:
                skipped += 1
                logger.debug("跳过无名菜谱记录")
                continue
            ingredients = json.dumps(
                recipe.get('ingredients', []), ensure_ascii=False
            )
            sql = """
                INSERT INTO veg_recipe (name, ingredients, source)
                VALUES (?, ?, 'imported')
            """
            try:
                self.execute_update(sql, (name, ingredients))
                count += 1
            except RuntimeError as e:
                skipped += 1
                logger.debug("跳过菜谱记录 '%s': %s", name, e)

        if skipped > 0:
            logger.info("菜谱导入完成: %d条成功, %d条跳过", count, skipped)
        return count

    def get_all_recipes(self) -> List[Dict]:
        """
        获取所有菜谱数据

        Returns:
            菜谱列表，每个元素为 {'name': str, 'ingredients': list}
        """
        sql = "SELECT name, ingredients FROM veg_recipe"
        rows = self.fetch_all(sql)
        recipes = []
        for row in rows:
            recipes.append({
                'name': row['name'],
                'ingredients': json.loads(row['ingredients']),
            })
        return recipes

    def get_recipe_count(self) -> int:
        """获取菜谱总数"""
        sql = "SELECT COUNT(*) as cnt FROM veg_recipe"
        row = self.fetch_one(sql)
        return row['cnt'] if row else 0

    def clear_all(self) -> int:
        """清空所有菜谱数据"""
        sql = "DELETE FROM veg_recipe"
        return self.execute_update(sql)
