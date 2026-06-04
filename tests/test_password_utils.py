"""Unit tests for utils/password_utils.py."""

from utils.password_utils import hash_password, verify_password


class TestPasswordUtils:

    def test_hash_returns_string(self):
        h = hash_password("Test1234")
        assert isinstance(h, str)
        assert h.startswith("$2")  # bcrypt prefix

    def test_hash_different_each_time(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2

    def test_verify_correct(self):
        pw = "MySecret99"
        h = hash_password(pw)
        assert verify_password(pw, h) is True

    def test_verify_wrong(self):
        h = hash_password("correct")
        assert verify_password("wrong", h) is False

    def test_unicode_password(self):
        pw = "密码abc123"
        h = hash_password(pw)
        assert verify_password(pw, h) is True

    def test_empty_password(self):
        h = hash_password("")
        assert verify_password("", h) is True
        assert verify_password("x", h) is False
