"""Unit tests for service/mining_service.py.

Uses a real in-memory SQLite DB and the actual Apriori pipeline.
"""

import json

from dao.vegetable_dao import VegetableDAO
from dao.recipe_dao import RecipeDAO
from dao.association_rule_dao import AssociationRuleDAO
from entity.vegetable import Vegetable
from service.mining_service import MiningService


def _seed_vegetables(dao: VegetableDAO):
    """Seed several vegetables and return a {name: id} mapping."""
    names = [
        ('番茄', '瓜茄类', '夏'),
        ('鸡蛋', '其他', '全年'),
        ('白菜', '叶菜类', '冬'),
        ('豆腐', '豆类', '全年'),
        ('黄瓜', '瓜茄类', '夏'),
        ('辣椒', '瓜茄类', '夏'),
    ]
    mapping = {}
    for name, cat, season in names:
        v = Vegetable(name=name, category=cat, season=season, price_ref=3.0)
        vid = dao.insert(v)
        mapping[name] = vid
    return mapping


def _seed_recipes(dao: RecipeDAO, tmp_path):
    """Import test recipes from a temp JSON file."""
    recipes = [
        {"name": "番茄炒蛋", "ingredients": ["番茄", "鸡蛋"]},
        {"name": "白菜豆腐汤", "ingredients": ["白菜", "豆腐"]},
        {"name": "番茄黄瓜沙拉", "ingredients": ["番茄", "黄瓜"]},
        {"name": "辣椒炒鸡蛋", "ingredients": ["辣椒", "鸡蛋"]},
        {"name": "白菜炒鸡蛋", "ingredients": ["白菜", "鸡蛋"]},
        {"name": "番茄豆腐", "ingredients": ["番茄", "豆腐"]},
        {"name": "辣椒豆腐", "ingredients": ["辣椒", "豆腐"]},
        {"name": "黄瓜鸡蛋", "ingredients": ["黄瓜", "鸡蛋"]},
    ]
    json_file = tmp_path / "recipes.json"
    json_file.write_text(json.dumps(recipes, ensure_ascii=False),
                         encoding='utf-8')
    dao.import_from_json(str(json_file))


class TestMiningService:

    def test_extract_vegetable_pairs(self):
        svc = MiningService()
        recipes = [
            {'ingredients': ['番茄', '鸡蛋']},
            {'ingredients': ['白菜', '豆腐', '辣椒']},
        ]
        pairs = svc.extract_vegetable_pairs(recipes)
        # First recipe: 1 pair × 2 directions = 2
        # Second recipe: 3 pairs × 2 directions = 6
        assert len(pairs) == 8
        assert ('番茄', '鸡蛋') in pairs
        assert ('鸡蛋', '番茄') in pairs

    def test_extract_vegetable_pairs_empty(self):
        svc = MiningService()
        assert svc.extract_vegetable_pairs([]) == []

    def test_extract_vegetable_pairs_single_ingredient(self):
        svc = MiningService()
        pairs = svc.extract_vegetable_pairs([{'ingredients': ['番茄']}])
        assert pairs == []

    def test_generate_rules_no_recipes(self):
        _seed_vegetables(VegetableDAO())
        svc = MiningService()
        count, msg = svc.generate_association_rules()
        assert count == 0
        assert '没有菜谱数据' in msg

    def test_generate_rules_success(self, tmp_path):
        veg_dao = VegetableDAO()
        _seed_vegetables(veg_dao)
        recipe_dao = RecipeDAO()
        _seed_recipes(recipe_dao, tmp_path)

        svc = MiningService()
        progress_steps = []
        count, msg = svc.generate_association_rules(
            min_support=0.01,
            min_confidence=0.1,
            progress_callback=lambda step, m: progress_steps.append(step),
        )
        assert count > 0
        assert '完成' in msg
        # Verify progress was called
        assert len(progress_steps) > 0

        # Verify rules stored in DB
        rule_dao = AssociationRuleDAO()
        assert rule_dao.count() == count

    def test_generate_rules_clears_old(self, tmp_path):
        """BR-07: old rules should be cleared before inserting new ones."""
        veg_dao = VegetableDAO()
        veg_map = _seed_vegetables(veg_dao)
        recipe_dao = RecipeDAO()
        _seed_recipes(recipe_dao, tmp_path)

        rule_dao = AssociationRuleDAO()
        # Insert a dummy old rule
        rule_dao.batch_insert([{
            'ante_veg_id': veg_map['番茄'],
            'post_veg_id': veg_map['白菜'],
            'support': 0.99, 'confidence': 0.99, 'lift': 9.0,
        }])
        old_count = rule_dao.count()
        assert old_count == 1

        svc = MiningService()
        count, _ = svc.generate_association_rules(
            min_support=0.01, min_confidence=0.1)
        # Old dummy rule should be gone — count reflects only new rules
        assert rule_dao.count() == count

    def test_generate_rules_insufficient_transactions(self, tmp_path):
        """Only 1 valid recipe with known vegs → should return 0."""
        veg_dao = VegetableDAO()
        _seed_vegetables(veg_dao)

        recipe_dao = RecipeDAO()
        recipes = [{"name": "solo", "ingredients": ["番茄", "鸡蛋"]}]
        json_file = tmp_path / "r.json"
        json_file.write_text(json.dumps(recipes), encoding='utf-8')
        recipe_dao.import_from_json(str(json_file))

        svc = MiningService()
        count, msg = svc.generate_association_rules(
            min_support=0.8, min_confidence=0.8)
        # With very high thresholds and only 1 transaction, expect 0 or a
        # message about insufficient data
        assert count == 0 or '不足' in msg or '未发现' in msg

    def test_generate_rules_recipes_with_unknown_vegs(self, tmp_path):
        """Recipes referencing non-existent vegetables should be filtered."""
        veg_dao = VegetableDAO()
        _seed_vegetables(veg_dao)

        recipe_dao = RecipeDAO()
        # Only 'unknownA' and 'unknownB' are not in DB
        recipes = [
            {"name": "mystery1", "ingredients": ["unknownA", "unknownB"]},
            {"name": "mystery2", "ingredients": ["unknownA", "番茄"]},
        ]
        json_file = tmp_path / "r.json"
        json_file.write_text(json.dumps(recipes, ensure_ascii=False),
                             encoding='utf-8')
        recipe_dao.import_from_json(str(json_file))

        svc = MiningService()
        count, msg = svc.generate_association_rules()
        assert count == 0
