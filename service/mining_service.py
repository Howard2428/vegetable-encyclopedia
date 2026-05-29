"""
数据挖掘服务类
使用Apriori关联规则算法从菜谱数据中挖掘蔬菜搭配规则。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Tuple
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from dao.recipe_dao import RecipeDAO
from dao.vegetable_dao import VegetableDAO
from dao.association_rule_dao import AssociationRuleDAO


class MiningService:
    """数据挖掘业务逻辑服务"""

    def __init__(self):
        self.recipe_dao = RecipeDAO()
        self.vegetable_dao = VegetableDAO()
        self.rule_dao = AssociationRuleDAO()

    def extract_vegetable_pairs(self, recipes: List[Dict]) -> List[Tuple[str, str]]:
        """
        从菜谱中提取蔬菜共现对

        Args:
            recipes: 菜谱列表

        Returns:
            蔬菜对列表 [(蔬菜A, 蔬菜B), ...]
        """
        pairs = []
        for recipe in recipes:
            ingredients = recipe.get('ingredients', [])
            # 两个蔬菜的搭配组合
            for i in range(len(ingredients)):
                for j in range(i + 1, len(ingredients)):
                    pairs.append((ingredients[i], ingredients[j]))
                    pairs.append((ingredients[j], ingredients[i]))
        return pairs

    def generate_association_rules(
        self,
        min_support: float = 0.01,
        min_confidence: float = 0.1,
        progress_callback=None
    ) -> Tuple[int, str]:
        """
        使用Apriori算法生成关联规则（BR-07：先清空旧规则再写入）

        Args:
            min_support: 最小支持度阈值
            min_confidence: 最小置信度阈值
            progress_callback: 进度回调函数 (step, message)

        Returns:
            (规则数量, 消息)
        """
        try:
            # 步骤1：拉取菜谱数据
            if progress_callback:
                progress_callback(1, "正在拉取菜谱数据...")
            recipes = self.recipe_dao.get_all_recipes()

            if len(recipes) == 0:
                return 0, "没有菜谱数据，请先导入菜谱JSON文件"

            # 步骤2：构建One-Hot编码矩阵
            if progress_callback:
                progress_callback(2, "正在构建事务矩阵...")

            # 获取所有蔬菜名称列表
            all_vegetables = self.vegetable_dao.get_all()
            veg_name_to_id = {v.name: v.veg_id for v in all_vegetables}

            # 构建事务列表（每个菜谱的蔬菜集合）
            transactions = []
            for recipe in recipes:
                ingredients = recipe.get('ingredients', [])
                # 只保留在蔬菜数据库中有记录的食材
                valid_ingredients = [
                    ing for ing in ingredients if ing in veg_name_to_id
                ]
                if len(valid_ingredients) >= 2:
                    transactions.append(set(valid_ingredients))

            if len(transactions) < 2:
                return 0, "有效菜谱数据不足（至少需要2个包含≥2种已知蔬菜的菜谱）"

            # 构建One-Hot编码DataFrame
            all_veg_names = list(veg_name_to_id.keys())
            # 只保留在事务中出现过的蔬菜
            appearing_vegs = set()
            for t in transactions:
                appearing_vegs.update(t)
            veg_list = sorted(appearing_vegs)

            if len(veg_list) < 2:
                return 0, "涉及的蔬菜种类不足（至少需要2种）"

            df_data = []
            for t in transactions:
                row = [1 if veg in t else 0 for veg in veg_list]
                df_data.append(row)

            df = pd.DataFrame(df_data, columns=veg_list)

            # 步骤3：Apriori算法挖掘频繁项集
            if progress_callback:
                progress_callback(3, "正在计算频繁项集（Apriori算法）...")

            frequent_itemsets = apriori(
                df, min_support=min_support, use_colnames=True
            )

            if frequent_itemsets.empty:
                return 0, f"未发现满足最小支持度（{min_support}）的频繁项集"

            # 步骤4：生成关联规则
            if progress_callback:
                progress_callback(4, "正在生成关联规则...")

            rules = association_rules(
                frequent_itemsets, metric="confidence",
                min_threshold=min_confidence
            )

            if rules.empty:
                return 0, f"未发现满足最小置信度（{min_confidence}）的关联规则"

            # 步骤5：过滤和整理规则
            if progress_callback:
                progress_callback(5, "正在过滤和存储规则...")

            # 只保留单前项→单后项的规则
            prepared_rules = []
            for _, row in rules.iterrows():
                antecedents = list(row['antecedents'])
                consequents = list(row['consequents'])
                # 只取长度为1的前项和后项
                if len(antecedents) == 1 and len(consequents) == 1:
                    ante_name = antecedents[0]
                    post_name = consequents[0]
                    ante_id = veg_name_to_id.get(ante_name)
                    post_id = veg_name_to_id.get(post_name)
                    if ante_id and post_id:
                        prepared_rules.append({
                            'ante_veg_id': ante_id,
                            'post_veg_id': post_id,
                            'support': round(row['support'], 6),
                            'confidence': round(row['confidence'], 6),
                            'lift': round(row['lift'], 6) if not pd.isna(row['lift']) else 0.0,
                        })

            if not prepared_rules:
                return 0, "无有效的单对单关联规则生成"

            # BR-07：先清空旧规则库
            if progress_callback:
                progress_callback(6, "正在清空旧规则库...")
            self.rule_dao.clear_all()

            # 批量写入新规则
            if progress_callback:
                progress_callback(7, f"正在写入{len(prepared_rules)}条新规则...")
            count = self.rule_dao.batch_insert(prepared_rules)

            if progress_callback:
                progress_callback(8, f"挖掘完成！共生成{count}条关联规则")

            return count, f"关联规则挖掘完成！共生成{count}条有效规则"

        except Exception as e:
            return 0, f"挖掘过程出错：{str(e)}"
