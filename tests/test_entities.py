"""Unit tests for all entity classes."""

import json
from datetime import datetime
from unittest.mock import MagicMock

from entity.vegetable import Vegetable
from entity.user import User
from entity.favorites_list import FavoritesList
from entity.custom_list import CustomList
from entity.association_rule import AssociationRule
from entity.recipe import Recipe
from entity.cooking_method import CookingMethod


# ────────────────── Vegetable ──────────────────


class TestVegetable:

    def test_defaults(self):
        v = Vegetable()
        assert v.veg_id is None
        assert v.name == ''
        assert v.view_count == 0
        assert v.favorite_count == 0
        assert v.price_ref == 0.0

    def test_to_dict(self):
        v = Vegetable(veg_id=1, name='白菜', category='叶菜类',
                      season='冬', price_ref=2.5)
        d = v.to_dict()
        assert d['veg_id'] == 1
        assert d['veg_name'] == '白菜'
        assert d['category'] == '叶菜类'
        assert d['price_ref'] == 2.5

    def test_from_dict_full(self):
        data = {
            'veg_id': 5,
            'veg_name': '番茄',
            'alias': '西红柿',
            'category': '瓜茄类',
            'season': '夏',
            'image_path': '/img/tomato.jpg',
            'nutrition': '维生素C',
            'purchase_tips': '选红色',
            'storage_method': '冷藏',
            'price_ref': 3.5,
            'view_count': 100,
            'favorite_count': 50,
        }
        v = Vegetable.from_dict(data)
        assert v.veg_id == 5
        assert v.name == '番茄'
        assert v.alias == '西红柿'
        assert v.price_ref == 3.5
        assert v.view_count == 100

    def test_from_dict_missing_fields(self):
        v = Vegetable.from_dict({})
        assert v.name == ''
        assert v.price_ref == 0.0
        assert v.view_count == 0

    def test_from_dict_none_values(self):
        data = {'price_ref': None, 'view_count': None, 'favorite_count': None}
        v = Vegetable.from_dict(data)
        assert v.price_ref == 0.0
        assert v.view_count == 0

    def test_from_row_none(self):
        assert Vegetable.from_row(None) is None

    def test_from_row(self):
        row = MagicMock()
        row.__getitem__ = lambda self, k: {
            'veg_id': 1, 'veg_name': '白菜', 'alias': '', 'category': '叶菜类',
            'season': '冬', 'nutrition': '维C', 'purchase_tips': '选绿色',
            'storage_method': '冷藏', 'price_ref': 2.0, 'view_count': 10,
            'favorite_count': 5, 'create_time': None, 'update_time': None,
            'image_path': '',
        }[k]
        row.keys = lambda: ['veg_id', 'veg_name', 'alias', 'category',
                            'season', 'nutrition', 'purchase_tips',
                            'storage_method', 'price_ref', 'view_count',
                            'favorite_count', 'create_time', 'update_time',
                            'image_path']
        v = Vegetable.from_row(row)
        assert v.veg_id == 1
        assert v.name == '白菜'

    def test_roundtrip_dict(self):
        v = Vegetable(veg_id=2, name='土豆', category='根茎类', season='秋')
        d = v.to_dict()
        v2 = Vegetable.from_dict(d)
        assert v2.veg_id == v.veg_id
        assert v2.name == v.name


# ────────────────── User ──────────────────


class TestUser:

    def test_defaults(self):
        u = User()
        assert u.role == 'user'
        assert u.is_admin is False

    def test_is_admin(self):
        u = User(role='admin')
        assert u.is_admin is True

    def test_to_dict(self):
        u = User(user_id=1, username='alice', role='user')
        d = u.to_dict()
        assert d['username'] == 'alice'
        assert d['role'] == 'user'

    def test_from_dict(self):
        data = {'user_id': 3, 'username': 'bob', 'role': 'admin'}
        u = User.from_dict(data)
        assert u.user_id == 3
        assert u.is_admin is True

    def test_from_dict_defaults(self):
        u = User.from_dict({})
        assert u.username == ''
        assert u.role == 'user'

    def test_from_row_none(self):
        assert User.from_row(None) is None

    def test_from_row(self):
        row = MagicMock()
        row.__getitem__ = lambda self, k: {
            'user_id': 1, 'username': 'test', 'password_hash': 'hash',
            'email': 'a@b.com', 'role': 'admin',
            'register_time': None, 'last_login_time': None,
        }[k]
        row.keys = lambda: ['user_id', 'username', 'password_hash', 'email',
                            'role', 'register_time', 'last_login_time']
        u = User.from_row(row)
        assert u.username == 'test'
        assert u.is_admin is True


# ────────────────── FavoritesList ──────────────────


class TestFavoritesList:

    def test_defaults(self):
        fl = FavoritesList()
        assert fl.user_id == 0
        assert fl.list_name == ''

    def test_to_dict(self):
        fl = FavoritesList(fav_list_id=1, user_id=2, list_name='my favs')
        d = fl.to_dict()
        assert d['fav_list_id'] == 1
        assert d['list_name'] == 'my favs'

    def test_from_dict(self):
        fl = FavoritesList.from_dict({'fav_list_id': 5, 'user_id': 3,
                                      'list_name': '蔬菜收藏'})
        assert fl.fav_list_id == 5

    def test_from_row_none(self):
        assert FavoritesList.from_row(None) is None


# ────────────────── CustomList ──────────────────


class TestCustomList:

    def test_defaults(self):
        cl = CustomList()
        assert cl.description == ''

    def test_to_dict(self):
        cl = CustomList(list_id=1, user_id=2, list_name='my list',
                        description='desc')
        d = cl.to_dict()
        assert d['list_name'] == 'my list'
        assert d['description'] == 'desc'

    def test_from_dict(self):
        cl = CustomList.from_dict({'list_id': 7, 'description': '测试'})
        assert cl.list_id == 7
        assert cl.description == '测试'

    def test_from_row_none(self):
        assert CustomList.from_row(None) is None


# ────────────────── AssociationRule ──────────────────


class TestAssociationRule:

    def test_defaults(self):
        ar = AssociationRule()
        assert ar.support == 0.0
        assert ar.confidence == 0.0
        assert ar.lift == 0.0

    def test_to_dict(self):
        ar = AssociationRule(rule_id=1, ante_veg_id=2, post_veg_id=3,
                             support=0.1, confidence=0.8, lift=1.2)
        d = ar.to_dict()
        assert d['confidence'] == 0.8

    def test_from_dict(self):
        ar = AssociationRule.from_dict({
            'ante_veg_id': 10, 'support': None, 'confidence': 0.5,
        })
        assert ar.ante_veg_id == 10
        assert ar.support == 0.0
        assert ar.confidence == 0.5

    def test_from_row_none(self):
        assert AssociationRule.from_row(None) is None


# ────────────────── Recipe ──────────────────


class TestRecipe:

    def test_defaults(self):
        r = Recipe()
        assert r.ingredients == []
        assert r.source == 'imported'

    def test_to_dict(self):
        r = Recipe(recipe_id=1, name='番茄炒蛋',
                   ingredients=['番茄', '鸡蛋'])
        d = r.to_dict()
        assert d['name'] == '番茄炒蛋'
        assert '番茄' in d['ingredients']

    def test_from_dict(self):
        r = Recipe.from_dict({'name': '蔬菜沙拉', 'ingredients': ['黄瓜']})
        assert r.name == '蔬菜沙拉'

    def test_from_row_none(self):
        assert Recipe.from_row(None) is None

    def test_from_row(self):
        row = MagicMock()
        row.__getitem__ = lambda self, k: {
            'recipe_id': 1, 'name': '菜', 'ingredients': '["白菜", "豆腐"]',
            'source': 'imported', 'create_time': None,
        }[k]
        row.get = lambda k, default=None: {
            'source': 'imported', 'create_time': None,
        }.get(k, default)
        r = Recipe.from_row(row)
        assert r.ingredients == ['白菜', '豆腐']


# ────────────────── CookingMethod ──────────────────


class TestCookingMethod:

    def test_defaults(self):
        cm = CookingMethod()
        assert cm.method_name == ''

    def test_to_dict(self):
        cm = CookingMethod(method_id=1, veg_id=2, method_name='清炒',
                           cooking_time='5分钟', ingredients='油、盐')
        d = cm.to_dict()
        assert d['method_name'] == '清炒'

    def test_from_dict(self):
        cm = CookingMethod.from_dict({
            'veg_id': None, 'method_name': '蒸',
        })
        assert cm.veg_id == 0
        assert cm.method_name == '蒸'

    def test_from_row_none(self):
        assert CookingMethod.from_row(None) is None
