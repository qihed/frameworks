"""Корневой conftest.py.

Наличие файла в корне проекта обеспечивает добавление корня проекта
в sys.path при запуске pytest, что позволяет тестам импортировать
модули приложения (models, storage, utils и т. д.) без установки
проекта как пакета. Дополнительно инициализируется Django, чтобы
тесты веб-интерфейса могли пользоваться тестовым клиентом.
"""

import os

import django
from django.test.utils import setup_test_environment

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comicstracker.settings")
django.setup()
setup_test_environment()
