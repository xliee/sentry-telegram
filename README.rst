Sentry Telegram |travis| |codecov| |pypi|
=========================================

Plugin for Sentry which allows sending notification via `Telegram <https://telegram.org/>`_ messenger.

Presented plugin tested with Sentry 23.8.0.dev0

    **DISCLAIMER**: Sentry API is under development and `is not frozen <https://docs.sentry.io/server/plugins/>`_.


How will it look like
---------------------

.. image:: https://raw.githubusercontent.com/xliee/sentry-telegram/master/docs/images/telegram-window.png
   :target: https://github.com/xliee/sentry-telegram/blob/master/docs/images/telegram-window.png
   :alt: How will it look like

Installation
------------

1. Install this package

.. code-block:: bash

    pip install xliee-sentry-telegram

2. Restart your Sentry instance.
3. Go to your Sentry web interface. Open ``Settings`` page of one of your projects.
4. On ``Integrations`` (or ``Legacy Integrations``) page, find ``Telegram Notifications Python3`` plugin and enable it.
5. Configure plugin on ``Configure plugin`` page.

   See `Telegram's documentation <https://core.telegram.org/bots#3-how-do-i-create-a-bot>`_ to know how to create ``BotAPI Token``.

6. Done!

.. |travis| image:: https://app.travis-ci.com/xliee/sentry-telegram.svg?branch=master
   :target: https://app.travis-ci.com/xliee/sentry-telegram
   :alt: Build Status

.. |codecov| image:: https://codecov.io/gh/xliee/sentry-telegram/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/xliee/sentry-telegram?branch=master
   :alt: Coverage Status

.. |pypi| image:: https://badge.fury.io/py/xliee-sentry-telegram.svg
   :target: https://pypi.python.org/pypi/xliee-sentry-telegram
