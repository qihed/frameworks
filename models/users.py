"""Класс User и функции работы с коллекцией пользователей."""

from typing import List, Optional


class User:
    """Пользователь сервиса учёта комиксов."""

    def __init__(self, user_id: int, name: str, age: int, email: str) -> None:
        """Создать объект пользователя."""
        self.id = user_id
        self.name = name
        self.age = age
        self.email = email

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из набора данных, например словаря JSON."""
        return cls(data["id"], data["name"], data["age"], data["email"])

    def __str__(self) -> str:
        """Вернуть строковое представление пользователя."""
        return f"{self.name}, {self.age} лет, {self.email}"


def add_user(users: List[User], name: str, age: int, email: str) -> User:
    """Создать объект User, добавить его в коллекцию и вернуть."""
    new_id = max((user.id for user in users), default=0) + 1
    user = User(new_id, name, age, email)
    users.append(user)
    return user


def find_user_by_id(users: List[User], user_id: int) -> Optional[User]:
    """Найти пользователя по идентификатору."""
    for user in users:
        if user.id == user_id:
            return user
    return None


def find_user(users: List[User], query: str) -> List[User]:
    """Найти пользователей по подстроке имени или адреса почты."""
    query_lower = query.lower()
    return [
        user for user in users
        if query_lower in user.name.lower() or query_lower in user.email.lower()
    ]


def show_users(users: List[User]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Список пользователей пуст.")
        return
    for user in users:
        print(f"[{user.id}] {user}")
