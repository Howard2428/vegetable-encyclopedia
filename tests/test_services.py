"""Unit tests for the service layer.

Uses a real (temporary) SQLite DB via the conftest `_reset_db` fixture.
"""

from unittest.mock import patch
from datetime import datetime

from dao.user_dao import UserDAO
from dao.vegetable_dao import VegetableDAO
from dao.association_rule_dao import AssociationRuleDAO
from entity.vegetable import Vegetable
from entity.cooking_method import CookingMethod
from utils.password_utils import hash_password

from service.user_service import UserService
from service.search_service import SearchService
from service.recommendation_service import RecommendationService
from service.vegetable_service import VegetableService
from service.collection_service import CollectionService


# ────────────────── helpers ──────────────────

def _create_user_via_dao(username='testuser', password='Test1234',
                         role='user'):
    dao = UserDAO()
    pw_hash = hash_password(password)
    uid = dao.create_user(username, pw_hash, role=role)
    return uid


def _create_vegetable_via_dao(name='白菜', category='叶菜类',
                              season='冬', price_ref=2.0):
    dao = VegetableDAO()
    v = Vegetable(name=name, category=category, season=season,
                  price_ref=price_ref)
    return dao.insert(v)


# ────────────────── UserService ──────────────────


class TestUserService:

    def test_register_success(self):
        svc = UserService()
        ok, msg = svc.register('alice', 'Pass1234')
        assert ok is True
        assert '成功' in msg

    def test_register_short_username(self):
        svc = UserService()
        ok, _ = svc.register('a', 'Pass1234')
        assert ok is False

    def test_register_long_username(self):
        svc = UserService()
        ok, _ = svc.register('a' * 51, 'Pass1234')
        assert ok is False

    def test_register_short_password(self):
        svc = UserService()
        ok, _ = svc.register('alice', '12345')
        assert ok is False

    def test_register_duplicate_username(self):
        svc = UserService()
        svc.register('alice', 'Pass1234')
        ok, msg = svc.register('alice', 'Pass5678')
        assert ok is False
        assert '已被注册' in msg

    def test_register_duplicate_email(self):
        svc = UserService()
        svc.register('alice', 'Pass1234', email='a@b.com')
        ok, msg = svc.register('bob', 'Pass5678', email='a@b.com')
        assert ok is False
        assert '邮箱' in msg

    def test_login_success(self):
        svc = UserService()
        svc.register('alice', 'Pass1234')
        ok, msg = svc.login('alice', 'Pass1234')
        assert ok is True
        assert svc.is_logged_in is True
        assert svc.current_user.username == 'alice'

    def test_login_wrong_password(self):
        svc = UserService()
        svc.register('alice', 'Pass1234')
        ok, msg = svc.login('alice', 'WrongPwd')
        assert ok is False
        assert '密码错误' in msg

    def test_login_nonexistent_user(self):
        svc = UserService()
        ok, msg = svc.login('nobody', 'Pass1234')
        assert ok is False
        assert '不存在' in msg

    def test_logout(self):
        svc = UserService()
        svc.register('alice', 'Pass1234')
        svc.login('alice', 'Pass1234')
        svc.logout()
        assert svc.is_logged_in is False

    def test_change_password_success(self):
        svc = UserService()
        svc.register('alice', 'OldPass1234')
        svc.login('alice', 'OldPass1234')
        ok, msg = svc.change_password('OldPass1234', 'NewPass12345')
        assert ok is True

    def test_change_password_not_logged_in(self):
        svc = UserService()
        ok, msg = svc.change_password('old', 'new12345')
        assert ok is False

    def test_change_password_wrong_old(self):
        svc = UserService()
        svc.register('alice', 'OldPass1234')
        svc.login('alice', 'OldPass1234')
        ok, _ = svc.change_password('WrongOld', 'NewPass12345')
        assert ok is False

    def test_change_password_too_short(self):
        svc = UserService()
        svc.register('alice', 'OldPass1234')
        svc.login('alice', 'OldPass1234')
        ok, _ = svc.change_password('OldPass1234', 'short')
        assert ok is False

    def test_is_admin(self):
        _create_user_via_dao('admin1', 'Admin1234', role='admin')
        svc = UserService()
        svc.login('admin1', 'Admin1234')
        assert svc.is_admin() is True

    def test_create_favorites_list_not_logged_in(self):
        svc = UserService()
        ok, _ = svc.create_favorites_list('test')
        assert ok is False

    def test_create_favorites_list_success(self):
        svc = UserService()
        svc.register('alice', 'Pass1234')
        svc.login('alice', 'Pass1234')
        ok, msg = svc.create_favorites_list('我的收藏')
        assert ok is True

    def test_create_favorites_list_empty_name(self):
        svc = UserService()
        svc.register('alice', 'Pass1234')
        svc.login('alice', 'Pass1234')
        ok, _ = svc.create_favorites_list('')
        assert ok is False

    def test_create_custom_list_not_logged_in(self):
        svc = UserService()
        ok, _ = svc.create_custom_list('test')
        assert ok is False

    def test_create_custom_list_success(self):
        svc = UserService()
        svc.register('alice', 'Pass1234')
        svc.login('alice', 'Pass1234')
        ok, msg = svc.create_custom_list('每周购物')
        assert ok is True

    def test_create_custom_list_duplicate(self):
        svc = UserService()
        svc.register('alice', 'Pass1234')
        svc.login('alice', 'Pass1234')
        svc.create_custom_list('每周购物')
        ok, msg = svc.create_custom_list('每周购物')
        assert ok is False
        assert '已存在' in msg


# ────────────────── SearchService ──────────────────


class TestSearchService:

    def test_fuzzy_search_empty(self):
        svc = SearchService()
        assert svc.fuzzy_search('') == []
        assert svc.fuzzy_search('   ') == []

    def test_fuzzy_search_results(self):
        _create_vegetable_via_dao('番茄', '瓜茄类', '夏')
        svc = SearchService()
        results = svc.fuzzy_search('番')
        assert len(results) == 1

    def test_filter_by_category(self):
        _create_vegetable_via_dao('白菜', '叶菜类')
        _create_vegetable_via_dao('番茄', '瓜茄类', '夏')
        svc = SearchService()
        leafy = svc.filter_by_category('叶菜类')
        assert len(leafy) == 1

    def test_filter_by_category_empty(self):
        _create_vegetable_via_dao('白菜')
        svc = SearchService()
        all_vegs = svc.filter_by_category('')
        assert len(all_vegs) >= 1

    def test_filter_by_season(self):
        _create_vegetable_via_dao('白菜', season='冬')
        svc = SearchService()
        winter = svc.filter_by_season('冬')
        assert len(winter) >= 1

    def test_filter_by_season_empty(self):
        _create_vegetable_via_dao('白菜')
        svc = SearchService()
        all_vegs = svc.filter_by_season('')
        assert len(all_vegs) >= 1

    def test_get_hot_ranking(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = SearchService()
        svc.increment_view_count(vid)
        ranking = svc.get_hot_ranking(5)
        assert len(ranking) >= 1

    def test_get_value_ranking(self):
        _create_vegetable_via_dao('白菜', price_ref=1.0)
        svc = SearchService()
        ranking = svc.get_value_ranking(5)
        assert len(ranking) >= 1

    def test_get_all_vegetables(self):
        _create_vegetable_via_dao('白菜')
        svc = SearchService()
        assert len(svc.get_all_vegetables()) >= 1

    def test_get_by_id(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = SearchService()
        veg = svc.get_by_id(vid)
        assert veg.name == '白菜'


# ────────────────── RecommendationService ──────────────────


class TestRecommendationService:

    def test_get_current_season(self):
        svc = RecommendationService()
        season = svc.get_current_season()
        assert season in ('春', '夏', '秋', '冬', '全年')

    def test_get_current_month(self):
        svc = RecommendationService()
        month = svc.get_current_month()
        assert 1 <= month <= 12

    def test_seasonal_vegetables(self):
        _create_vegetable_via_dao('白菜', season='冬')
        svc = RecommendationService()
        result = svc.get_seasonal_vegetables(month=12)
        assert any(v.name == '白菜' for v in result)

    def test_seasonal_vegetables_default_month(self):
        _create_vegetable_via_dao('白菜', season='全年')
        svc = RecommendationService()
        result = svc.get_seasonal_vegetables()
        assert len(result) >= 1

    def test_association_vegetables(self):
        veg_dao = VegetableDAO()
        vid1 = _create_vegetable_via_dao('白菜')
        vid2 = _create_vegetable_via_dao('豆腐', '豆类', '全年')

        rule_dao = AssociationRuleDAO()
        rule_dao.batch_insert([{
            'ante_veg_id': vid1, 'post_veg_id': vid2,
            'support': 0.1, 'confidence': 0.8, 'lift': 1.5,
        }])

        svc = RecommendationService()
        result = svc.get_association_vegetables(vid1)
        assert len(result) == 1
        assert result[0].name == '豆腐'

    def test_association_vegetables_empty(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = RecommendationService()
        result = svc.get_association_vegetables(vid)
        assert result == []

    def test_increment_favorite_count(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = RecommendationService()
        svc.increment_favorite_count(vid)
        veg = VegetableDAO().get_by_id(vid)
        assert veg.favorite_count == 1

    def test_decrement_favorite_count(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = RecommendationService()
        svc.increment_favorite_count(vid)
        svc.decrement_favorite_count(vid)
        veg = VegetableDAO().get_by_id(vid)
        assert veg.favorite_count == 0

    def test_get_rule_count(self):
        svc = RecommendationService()
        assert svc.get_rule_count() == 0

    def test_month_season_map_coverage(self):
        svc = RecommendationService()
        expected = {
            1: '冬', 2: '冬', 3: '春', 4: '春',
            5: '夏', 6: '夏', 7: '夏', 8: '夏',
            9: '秋', 10: '秋', 11: '秋', 12: '冬',
        }
        for month, season in expected.items():
            assert svc.MONTH_SEASON_MAP[month] == season


# ────────────────── VegetableService ──────────────────


class TestVegetableService:

    def test_add_vegetable_success(self):
        svc = VegetableService()
        v = Vegetable(name='菠菜', category='叶菜类', season='冬')
        ok, msg = svc.add_vegetable(v)
        assert ok is True

    def test_add_vegetable_empty_name(self):
        svc = VegetableService()
        v = Vegetable(name='', category='叶菜类', season='冬')
        ok, _ = svc.add_vegetable(v)
        assert ok is False

    def test_add_vegetable_duplicate(self):
        _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        v = Vegetable(name='白菜', category='叶菜类', season='冬')
        ok, msg = svc.add_vegetable(v)
        assert ok is False
        assert '已存在' in msg

    def test_add_vegetable_invalid_category(self):
        svc = VegetableService()
        v = Vegetable(name='神秘菜', category='无效类别', season='冬')
        ok, _ = svc.add_vegetable(v)
        assert ok is False

    def test_update_vegetable_success(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        veg = svc.get_vegetable_by_id(vid)
        veg.nutrition = '含大量维生素'
        ok, _ = svc.update_vegetable(veg)
        assert ok is True

    def test_update_vegetable_no_id(self):
        svc = VegetableService()
        v = Vegetable(name='白菜', category='叶菜类', season='冬')
        ok, _ = svc.update_vegetable(v)
        assert ok is False

    def test_update_vegetable_empty_name(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        veg = svc.get_vegetable_by_id(vid)
        veg.name = ''
        ok, _ = svc.update_vegetable(veg)
        assert ok is False

    def test_update_vegetable_invalid_category(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        veg = svc.get_vegetable_by_id(vid)
        veg.category = '无效'
        ok, _ = svc.update_vegetable(veg)
        assert ok is False

    def test_delete_vegetable(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        ok, msg = svc.delete_vegetable(vid)
        assert ok is True

    def test_delete_nonexistent(self):
        svc = VegetableService()
        ok, _ = svc.delete_vegetable(9999)
        assert ok is False

    def test_get_all_vegetables(self):
        _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        assert len(svc.get_all_vegetables()) >= 1

    def test_get_valid_categories(self):
        cats = VegetableService.get_valid_categories()
        assert '叶菜类' in cats
        assert '根茎类' in cats

    def test_add_cooking_method_success(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        cm = CookingMethod(veg_id=vid, method_name='清炒')
        ok, _ = svc.add_cooking_method(cm)
        assert ok is True
        methods = svc.get_cooking_methods(vid)
        assert len(methods) == 1

    def test_add_cooking_method_empty_name(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        cm = CookingMethod(veg_id=vid, method_name='')
        ok, _ = svc.add_cooking_method(cm)
        assert ok is False

    def test_add_cooking_method_no_veg_id(self):
        svc = VegetableService()
        cm = CookingMethod(method_name='清炒')
        ok, _ = svc.add_cooking_method(cm)
        assert ok is False

    def test_update_cooking_method_success(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        cm = CookingMethod(veg_id=vid, method_name='清炒')
        svc.add_cooking_method(cm)
        methods = svc.get_cooking_methods(vid)
        methods[0].cooking_time = '10分钟'
        ok, _ = svc.update_cooking_method(methods[0])
        assert ok is True

    def test_update_cooking_method_no_id(self):
        svc = VegetableService()
        cm = CookingMethod(method_name='清炒')
        ok, _ = svc.update_cooking_method(cm)
        assert ok is False

    def test_update_cooking_method_empty_name(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        svc.add_cooking_method(CookingMethod(veg_id=vid, method_name='清炒'))
        methods = svc.get_cooking_methods(vid)
        methods[0].method_name = ''
        ok, _ = svc.update_cooking_method(methods[0])
        assert ok is False

    def test_delete_cooking_method(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        svc.add_cooking_method(CookingMethod(veg_id=vid, method_name='清炒'))
        methods = svc.get_cooking_methods(vid)
        ok, _ = svc.delete_cooking_method(methods[0].method_id)
        assert ok is True

    def test_replace_cooking_methods(self):
        vid = _create_vegetable_via_dao('白菜')
        svc = VegetableService()
        svc.add_cooking_method(CookingMethod(veg_id=vid, method_name='清炒'))
        new_methods = [
            CookingMethod(method_name='蒸'),
            CookingMethod(method_name='炖'),
        ]
        ok, msg = svc.replace_cooking_methods(vid, new_methods)
        assert ok is True
        assert '2' in msg


# ────────────────── CollectionService ──────────────────


class TestCollectionService:

    def _setup_user_and_veg(self):
        uid = _create_user_via_dao('coll_user', 'Pass1234')
        vid = _create_vegetable_via_dao('白菜')
        return uid, vid

    def test_check_login_not_set(self):
        svc = CollectionService()
        ok, msg = svc._check_login()
        assert ok is False

    def test_check_login_set(self):
        svc = CollectionService()
        svc.set_current_user(1)
        ok, _ = svc._check_login()
        assert ok is True

    def test_add_to_favorites_not_logged_in(self):
        svc = CollectionService()
        ok, _ = svc.add_to_favorites(1, 1)
        assert ok is False

    def test_favorites_workflow(self):
        uid, vid = self._setup_user_and_veg()
        from dao.favorites_dao import FavoritesDAO
        fav_dao = FavoritesDAO()
        fav_id = fav_dao.create_list(uid, '收藏夹')

        svc = CollectionService()
        svc.set_current_user(uid)

        ok, _ = svc.add_to_favorites(fav_id, vid)
        assert ok is True

        # duplicate
        ok, _ = svc.add_to_favorites(fav_id, vid)
        assert ok is False

        items = svc.get_favorites_items(fav_id)
        assert len(items) == 1

        ids = svc.get_favorited_veg_ids()
        assert vid in ids

        ok, _ = svc.remove_from_favorites(fav_id, vid)
        assert ok is True

    def test_get_user_favorites_lists_not_logged_in(self):
        svc = CollectionService()
        assert svc.get_user_favorites_lists() == []

    def test_delete_favorites_list(self):
        uid, _ = self._setup_user_and_veg()
        from dao.favorites_dao import FavoritesDAO
        fav_dao = FavoritesDAO()
        fav_id = fav_dao.create_list(uid, '收藏夹')

        svc = CollectionService()
        svc.set_current_user(uid)
        ok, _ = svc.delete_favorites_list(fav_id)
        assert ok is True

    def test_custom_list_workflow(self):
        uid, vid = self._setup_user_and_veg()
        from dao.custom_list_dao import CustomListDAO
        cl_dao = CustomListDAO()
        lid = cl_dao.create_list(uid, '清单A')

        svc = CollectionService()
        svc.set_current_user(uid)

        ok, _ = svc.add_to_custom_list(lid, vid)
        assert ok is True

        # duplicate
        ok, _ = svc.add_to_custom_list(lid, vid)
        assert ok is False

        items = svc.get_custom_list_items(lid)
        assert len(items) == 1

        ok, _ = svc.remove_from_custom_list(lid, vid)
        assert ok is True

    def test_custom_list_max_items(self):
        uid, _ = self._setup_user_and_veg()
        from dao.custom_list_dao import CustomListDAO
        cl_dao = CustomListDAO()
        lid = cl_dao.create_list(uid, '清单B')

        veg_dao = VegetableDAO()
        vids = []
        for i in range(50):
            vid = _create_vegetable_via_dao(f'菜{i}', category='叶菜类',
                                            season='全年')
            vids.append(vid)

        svc = CollectionService()
        svc.set_current_user(uid)

        for vid in vids:
            svc.add_to_custom_list(lid, vid)

        # 51st should fail (BR-05)
        extra_vid = _create_vegetable_via_dao('超标菜', category='叶菜类',
                                              season='全年')
        ok, msg = svc.add_to_custom_list(lid, extra_vid)
        assert ok is False
        assert '上限' in msg

    def test_add_to_custom_list_not_logged_in(self):
        svc = CollectionService()
        ok, _ = svc.add_to_custom_list(1, 1)
        assert ok is False

    def test_get_user_custom_lists_not_logged_in(self):
        svc = CollectionService()
        assert svc.get_user_custom_lists() == []

    def test_delete_custom_list(self):
        uid, _ = self._setup_user_and_veg()
        from dao.custom_list_dao import CustomListDAO
        cl_dao = CustomListDAO()
        lid = cl_dao.create_list(uid, '清单C')

        svc = CollectionService()
        svc.set_current_user(uid)
        ok, _ = svc.delete_custom_list(lid)
        assert ok is True

    def test_delete_custom_list_not_logged_in(self):
        svc = CollectionService()
        ok, _ = svc.delete_custom_list(1)
        assert ok is False

    def test_remove_from_favorites_not_logged_in(self):
        svc = CollectionService()
        ok, _ = svc.remove_from_favorites(1, 1)
        assert ok is False

    def test_remove_from_custom_list_not_logged_in(self):
        svc = CollectionService()
        ok, _ = svc.remove_from_custom_list(1, 1)
        assert ok is False

    def test_get_favorited_veg_ids_not_logged_in(self):
        svc = CollectionService()
        assert svc.get_favorited_veg_ids() == []
