#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

from xliee_sentry_telegram import __version__


with open('README.rst', 'r') as f:
    long_description = f.read()


setup(
    name='xliee_sentry_telegram',
    version=__version__,
    packages=['xliee_sentry_telegram'],
    url='https://github.com/xliee/sentry-telegram',
    author='Xliee',
    author_email='info@xliee.es',
    description='Plugin for Sentry which allows sending notification via Telegram messenger.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='MIT',
    entry_points={
        'sentry.plugins': [
            'xliee_sentry_telegram = xliee_sentry_telegram.plugin:TelegramNotificationsPlugin',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: System :: Monitoring',
    ],
    include_package_data=True,
)
