"""Unit tests for the DAO layer (data access objects).

Every test uses a fresh in-memory SQLite DB via the conftest `_reset_db` fixture.
"""

import json
import os

from dao.user_dao import UserDAO
from dao.vegetable_dao import VegetableDAO
from dao.favorites_dao import FavoritesDAO
from dao.custom_list_dao import CustomListDAO
from dao.association_rule_dao import AssociationRuleDAO
from dao.recipe_dao import RecipeDAO
from dao.browse_history_dao import BrowseHistoryDAO
from dao.cooking_method_dao import CookingMethodDAO
from entity.vegetable import Vegetable
from entity.cooking_method import CookingMethod
from utils.password_utils import hash_password


# ────────────────── helpers ──────────────────

def _seed_user(dao: UserDAO, username='testuser') -> int:
    return dao.create_user(username, hash_password('Pass1234'))


def _seed_vegetable(dao: VegetableDAO, name='白菜', category='叶菜类',
                    season='冬', price_ref=2.0) -> int:
    v = Vegetable(name=name, category=category, season=season,
                  price_ref=price_ref)
    return dao.insert(v)


# ────────────────── UserDAO ──────────────────


class TestUserDAO:

    def test_create_and_get_by_username(self):
        dao = UserDAO()
        uid = _seed_user(dao, 'alice')
        assert uid > 0
        user = dao.get_by_username('alice')
        assert user is not None
        assert user.username == 'alice'

    def test_get_by_id(self):
        dao = UserDAO()
        uid = _seed_user(dao, 'bob')
        user = dao.get_by_id(uid)
        assert user.username == 'bob'

    def test_get_nonexistent(self):
        dao = UserDAO()
        assert dao.get_by_username('nobody') is None
        assert dao.get_by_id(9999) is None

    def test_check_username_exists(self):
        dao = UserDAO()
        _seed_user(dao, 'charlie')
        assert dao.check_username_exists('charlie') is True
        assert dao.check_username_exists('nobody') is False

    def test_check_email_exists(self):
        dao = UserDAO()
        dao.create_user('u1', hash_password('p'), 'a@b.com')
        assert dao.check_email_exists('a@b.com') is True
        assert dao.check_email_exists('x@y.com') is False
        assert dao.check_email_exists('') is False

    def test_update_password(self):
        dao = UserDAO()
        uid = _seed_user(dao, 'dave')
        new_hash = hash_password('NewPass99')
        dao.update_password(uid, new_hash)
        user = dao.get_by_id(uid)
        assert user.password_hash == new_hash

    def test_update_last_login(self):
        dao = UserDAO()
        uid = _seed_user(dao, 'eve')
        user_before = dao.get_by_id(uid)
        dao.update_last_login(uid)
        user_after = dao.get_by_id(uid)
        assert user_after.last_login_time is not None

    def test_get_user_count(self):
        dao = UserDAO()
        assert dao.get_user_count() == 0
        _seed_user(dao, 'u1')
        _seed_user(dao, 'u2')
        assert dao.get_user_count() == 2

    def test_get_all_users(self):
        dao = UserDAO()
        _seed_user(dao, 'u1')
        _seed_user(dao, 'u2')
        users = dao.get_all_users()
        assert len(users) == 2

    def test_delete_all_users(self):
        dao = UserDAO()
        _seed_user(dao, 'u1')
        _seed_user(dao, 'u2')
        count = dao.delete_all_users()
        assert count == 2
        assert dao.get_user_count() == 0


# ────────────────── VegetableDAO ──────────────────


class TestVegetableDAO:

    def test_insert_and_get_by_id(self):
        dao = VegetableDAO()
        vid = _seed_vegetable(dao, '白菜')
        veg = dao.get_by_id(vid)
        assert veg is not None
        assert veg.name == '白菜'

    def test_get_by_name(self):
        dao = VegetableDAO()
        _seed_vegetable(dao, '番茄', '瓜茄类', '夏')
        veg = dao.get_by_name('番茄')
        assert veg.category == '瓜茄类'

    def test_get_all(self):
        dao = VegetableDAO()
        _seed_vegetable(dao, '白菜')
        _seed_vegetable(dao, '番茄', '瓜茄类', '夏')
        all_vegs = dao.get_all()
        assert len(all_vegs) == 2

    def test_get_by_category(self):
        dao = VegetableDAO()
        _seed_vegetable(dao, '白菜', '叶菜类')
        _seed_vegetable(dao, '番茄', '瓜茄类', '夏')
        leafy = dao.get_by_category('叶菜类')
        assert len(leafy) == 1
        assert leafy[0].name == '白菜'

    def test_get_by_season(self):
        dao = VegetableDAO()
        _seed_vegetable(dao, '白菜', season='冬')
        _seed_vegetable(dao, '番茄', category='瓜茄类', season='夏')
        winter = dao.get_by_season('冬')
        assert any(v.name == '白菜' for v in winter)

    def test_fuzzy_search(self):
        dao = VegetableDAO()
        v = Vegetable(name='番茄', alias='西红柿', category='瓜茄类', season='夏')
        dao.insert(v)
        results = dao.fuzzy_search('番')
        assert len(results) == 1
        results = dao.fuzzy_search('西红')
        assert len(results) == 1

    def test_hot_ranking(self):
        dao = VegetableDAO()
        v1 = Vegetable(name='白菜', category='叶菜类', season='冬')
        v2 = Vegetable(name='番茄', category='瓜茄类', season='夏')
        vid1 = dao.insert(v1)
        vid2 = dao.insert(v2)
        # Bump v2 views
        for _ in range(5):
            dao.increment_view_count(vid2)
        ranking = dao.get_hot_ranking(10)
        assert ranking[0].name == '番茄'

    def test_value_ranking(self):
        dao = VegetableDAO()
        _seed_vegetable(dao, '白菜', price_ref=1.0)
        _seed_vegetable(dao, '松茸', category='菌菇类', season='秋', price_ref=50.0)
        ranking = dao.get_value_ranking(10)
        assert ranking[0].name == '白菜'

    def test_increment_view_count(self):
        dao = VegetableDAO()
        vid = _seed_vegetable(dao, '白菜')
        dao.increment_view_count(vid)
        dao.increment_view_count(vid)
        veg = dao.get_by_id(vid)
        assert veg.view_count == 2

    def test_increment_and_decrement_favorite_count(self):
        dao = VegetableDAO()
        vid = _seed_vegetable(dao, '白菜')
        dao.increment_favorite_count(vid)
        dao.increment_favorite_count(vid)
        assert dao.get_by_id(vid).favorite_count == 2
        dao.decrement_favorite_count(vid)
        assert dao.get_by_id(vid).favorite_count == 1

    def test_update(self):
        dao = VegetableDAO()
        vid = _seed_vegetable(dao, '白菜')
        veg = dao.get_by_id(vid)
        veg.nutrition = '维生素C很丰富'
        dao.update(veg)
        updated = dao.get_by_id(vid)
        assert updated.nutrition == '维生素C很丰富'

    def test_delete(self):
        dao = VegetableDAO()
        vid = _seed_vegetable(dao, '白菜')
        dao.delete(vid)
        assert dao.get_by_id(vid) is None


# ────────────────── FavoritesDAO ──────────────────


class TestFavoritesDAO:

    def test_create_and_get_lists(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'fav_user')
        fav_dao = FavoritesDAO()
        fav_dao.create_list(uid, '我的收藏')
        lists = fav_dao.get_lists_by_user(uid)
        assert len(lists) == 1
        assert lists[0].list_name == '我的收藏'

    def test_add_and_get_items(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'fav_user')
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        fav_dao = FavoritesDAO()
        fav_id = fav_dao.create_list(uid, '收藏夹A')
        fav_dao.add_item(fav_id, vid)
        items = fav_dao.get_items_by_list(fav_id)
        assert len(items) == 1
        assert items[0].name == '白菜'

    def test_add_duplicate_returns_zero(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'fav_user')
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        fav_dao = FavoritesDAO()
        fav_id = fav_dao.create_list(uid, '收藏夹A')
        fav_dao.add_item(fav_id, vid)
        result = fav_dao.add_item(fav_id, vid)
        assert result == 0

    def test_remove_item(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'fav_user')
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        fav_dao = FavoritesDAO()
        fav_id = fav_dao.create_list(uid, '收藏夹A')
        fav_dao.add_item(fav_id, vid)
        fav_dao.remove_item(fav_id, vid)
        assert len(fav_dao.get_items_by_list(fav_id)) == 0

    def test_is_favorited(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'fav_user')
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        fav_dao = FavoritesDAO()
        fav_id = fav_dao.create_list(uid, '收藏夹A')
        assert fav_dao.is_favorited(fav_id, vid) is False
        fav_dao.add_item(fav_id, vid)
        assert fav_dao.is_favorited(fav_id, vid) is True

    def test_delete_list(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'fav_user')
        fav_dao = FavoritesDAO()
        fav_id = fav_dao.create_list(uid, '收藏夹A')
        fav_dao.delete_list(fav_id)
        assert fav_dao.get_list_by_id(fav_id) is None

    def test_get_favorited_veg_ids(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'fav_user')
        veg_dao = VegetableDAO()
        vid1 = _seed_vegetable(veg_dao, '白菜')
        vid2 = _seed_vegetable(veg_dao, '番茄', '瓜茄类', '夏')

        fav_dao = FavoritesDAO()
        fav_id = fav_dao.create_list(uid, '收藏夹A')
        fav_dao.add_item(fav_id, vid1)
        fav_dao.add_item(fav_id, vid2)
        ids = fav_dao.get_favorited_veg_ids(uid)
        assert set(ids) == {vid1, vid2}


# ────────────────── CustomListDAO ──────────────────


class TestCustomListDAO:

    def test_create_and_get(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'cl_user')
        cl_dao = CustomListDAO()
        lid = cl_dao.create_list(uid, '每周购物')
        lists = cl_dao.get_lists_by_user(uid)
        assert len(lists) == 1

    def test_check_name_duplicate(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'cl_user')
        cl_dao = CustomListDAO()
        cl_dao.create_list(uid, '每周购物')
        assert cl_dao.check_name_duplicate(uid, '每周购物') is True
        assert cl_dao.check_name_duplicate(uid, '其他名称') is False

    def test_add_and_count_items(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'cl_user')
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        cl_dao = CustomListDAO()
        lid = cl_dao.create_list(uid, '每周购物')
        cl_dao.add_item(lid, vid)
        assert cl_dao.count_items(lid) == 1

    def test_add_duplicate_returns_zero(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'cl_user')
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        cl_dao = CustomListDAO()
        lid = cl_dao.create_list(uid, '每周购物')
        cl_dao.add_item(lid, vid)
        assert cl_dao.add_item(lid, vid) == 0

    def test_remove_item(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'cl_user')
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        cl_dao = CustomListDAO()
        lid = cl_dao.create_list(uid, '每周购物')
        cl_dao.add_item(lid, vid)
        cl_dao.remove_item(lid, vid)
        assert cl_dao.count_items(lid) == 0

    def test_is_in_list(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'cl_user')
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        cl_dao = CustomListDAO()
        lid = cl_dao.create_list(uid, '每周购物')
        assert cl_dao.is_in_list(lid, vid) is False
        cl_dao.add_item(lid, vid)
        assert cl_dao.is_in_list(lid, vid) is True

    def test_delete_list(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'cl_user')
        cl_dao = CustomListDAO()
        lid = cl_dao.create_list(uid, '每周购物')
        cl_dao.delete_list(lid)
        assert cl_dao.get_list_by_id(lid) is None


# ────────────────── AssociationRuleDAO ──────────────────


class TestAssociationRuleDAO:

    def test_batch_insert_and_count(self):
        veg_dao = VegetableDAO()
        vid1 = _seed_vegetable(veg_dao, '白菜')
        vid2 = _seed_vegetable(veg_dao, '豆腐', '豆类', '全年')

        rule_dao = AssociationRuleDAO()
        rules = [
            {'ante_veg_id': vid1, 'post_veg_id': vid2,
             'support': 0.1, 'confidence': 0.8, 'lift': 1.5},
        ]
        rule_dao.batch_insert(rules)
        assert rule_dao.count() == 1

    def test_get_by_ante_veg(self):
        veg_dao = VegetableDAO()
        vid1 = _seed_vegetable(veg_dao, '白菜')
        vid2 = _seed_vegetable(veg_dao, '豆腐', '豆类', '全年')
        vid3 = _seed_vegetable(veg_dao, '番茄', '瓜茄类', '夏')

        rule_dao = AssociationRuleDAO()
        rules = [
            {'ante_veg_id': vid1, 'post_veg_id': vid2,
             'support': 0.1, 'confidence': 0.8, 'lift': 1.5},
            {'ante_veg_id': vid1, 'post_veg_id': vid3,
             'support': 0.05, 'confidence': 0.5, 'lift': 1.2},
        ]
        rule_dao.batch_insert(rules)
        result = rule_dao.get_by_ante_veg(vid1, limit=5)
        assert len(result) == 2
        assert result[0].confidence >= result[1].confidence

    def test_clear_all(self):
        veg_dao = VegetableDAO()
        vid1 = _seed_vegetable(veg_dao, '白菜')
        vid2 = _seed_vegetable(veg_dao, '豆腐', '豆类', '全年')

        rule_dao = AssociationRuleDAO()
        rule_dao.batch_insert([
            {'ante_veg_id': vid1, 'post_veg_id': vid2,
             'support': 0.1, 'confidence': 0.8, 'lift': 1.5},
        ])
        rule_dao.clear_all()
        assert rule_dao.count() == 0

    def test_get_all(self):
        rule_dao = AssociationRuleDAO()
        assert rule_dao.get_all() == []


# ────────────────── RecipeDAO ──────────────────


class TestRecipeDAO:

    def test_import_and_get_all(self, tmp_path):
        recipes_data = [
            {"name": "番茄炒蛋", "ingredients": ["番茄", "鸡蛋"]},
            {"name": "白菜豆腐汤", "ingredients": ["白菜", "豆腐"]},
        ]
        json_file = tmp_path / "recipes.json"
        json_file.write_text(json.dumps(recipes_data, ensure_ascii=False),
                             encoding='utf-8')

        dao = RecipeDAO()
        count = dao.import_from_json(str(json_file))
        assert count == 2
        all_recipes = dao.get_all_recipes()
        assert len(all_recipes) == 2
        assert all_recipes[0]['name'] in ('番茄炒蛋', '白菜豆腐汤')

    def test_get_recipe_count(self):
        dao = RecipeDAO()
        assert dao.get_recipe_count() == 0

    def test_clear_all(self, tmp_path):
        recipes_data = [{"name": "test", "ingredients": ["a"]}]
        json_file = tmp_path / "r.json"
        json_file.write_text(json.dumps(recipes_data), encoding='utf-8')

        dao = RecipeDAO()
        dao.import_from_json(str(json_file))
        dao.clear_all()
        assert dao.get_recipe_count() == 0


# ────────────────── BrowseHistoryDAO ──────────────────


class TestBrowseHistoryDAO:

    def test_add_and_get_history(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'hist_user')
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        hist_dao = BrowseHistoryDAO()
        hist_dao.add_history(uid, vid)
        history = hist_dao.get_history(uid)
        assert len(history) == 1
        assert history[0].name == '白菜'

    def test_dedup_history(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'hist_user')
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        hist_dao = BrowseHistoryDAO()
        hist_dao.add_history(uid, vid)
        hist_dao.add_history(uid, vid)
        assert hist_dao.get_count(uid) == 1

    def test_clear_history(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'hist_user')
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        hist_dao = BrowseHistoryDAO()
        hist_dao.add_history(uid, vid)
        hist_dao.clear_history(uid)
        assert hist_dao.get_count(uid) == 0

    def test_history_limit_20(self):
        user_dao = UserDAO()
        uid = _seed_user(user_dao, 'hist_user')
        veg_dao = VegetableDAO()

        hist_dao = BrowseHistoryDAO()
        vids = []
        for i in range(25):
            vid = _seed_vegetable(veg_dao, f'蔬菜{i}',
                                  category='叶菜类', season='全年')
            vids.append(vid)

        for vid in vids:
            hist_dao.add_history(uid, vid)

        assert hist_dao.get_count(uid) == 20


# ────────────────── CookingMethodDAO ──────────────────


class TestCookingMethodDAO:

    def test_insert_and_get(self):
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        cm_dao = CookingMethodDAO()
        cm = CookingMethod(veg_id=vid, method_name='清炒',
                           cooking_time='5分钟', ingredients='油盐')
        cm_dao.insert(cm)
        methods = cm_dao.get_by_veg_id(vid)
        assert len(methods) == 1
        assert methods[0].method_name == '清炒'

    def test_update(self):
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        cm_dao = CookingMethodDAO()
        cm = CookingMethod(veg_id=vid, method_name='清炒')
        mid = cm_dao.insert(cm)
        method = cm_dao.get_by_id(mid)
        method.cooking_time = '10分钟'
        cm_dao.update(method)
        updated = cm_dao.get_by_id(mid)
        assert updated.cooking_time == '10分钟'

    def test_delete(self):
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        cm_dao = CookingMethodDAO()
        cm = CookingMethod(veg_id=vid, method_name='清炒')
        mid = cm_dao.insert(cm)
        cm_dao.delete(mid)
        assert cm_dao.get_by_id(mid) is None

    def test_replace_all_for_veg(self):
        veg_dao = VegetableDAO()
        vid = _seed_vegetable(veg_dao, '白菜')

        cm_dao = CookingMethodDAO()
        cm_dao.insert(CookingMethod(veg_id=vid, method_name='清炒'))
        new_methods = [
            CookingMethod(method_name='蒸'),
            CookingMethod(method_name='炖'),
        ]
        cm_dao.replace_all_for_veg(vid, new_methods)
        methods = cm_dao.get_by_veg_id(vid)
        assert len(methods) == 2
        names = {m.method_name for m in methods}
        assert names == {'蒸', '炖'}
