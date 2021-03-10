# coding: utf-8
import os


os.environ.setdefault('DB', 'postgres')
pytest_plugins = [
    'sentry.utils.pytest',
]
