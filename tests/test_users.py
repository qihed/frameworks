"""Тесты класса User и функций работы с пользователями (models/users.py)."""

from models import User
from models.users import add_user, find_user, find_user_by_id


def test_user_creation():
    user = User(1, "Иван Петров", 20, "ivan@example.com")
    assert user.id == 1
    assert user.name == "Иван Петров"
    assert user.age == 20
    assert user.email == "ivan@example.com"


def test_user_from_data():
    data = {"id": 2, "name": "Анна Смирнова", "age": 25, "email": "anna@example.com"}
    user = User.from_data(data)
    assert user.id == 2
    assert user.name == "Анна Смирнова"


def test_add_user():
    users = []
    user = add_user(users, "Иван Петров", 20, "ivan@example.com")
    assert len(users) == 1
    assert user.id == 1


def test_find_user_by_id():
    users = []
    add_user(users, "Иван Петров", 20, "ivan@example.com")
    found = find_user_by_id(users, 1)
    assert found is not None
    assert found.name == "Иван Петров"
    assert find_user_by_id(users, 99) is None


def test_find_user_by_query():
    users = []
    add_user(users, "Иван Петров", 20, "ivan@example.com")
    add_user(users, "Анна Смирнова", 25, "anna@example.com")
    result = find_user(users, "анна")
    assert len(result) == 1
    assert result[0].name == "Анна Смирнова"
