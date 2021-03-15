# coding: utf-8
from mock import patch
from distutils.version import LooseVersion as V

import pytest

import sentry
from exam import fixture
import responses
from sentry.models import Rule
from sentry.plugins.base import plugins, Notification
from sentry.testutils import PluginTestCase
from sentry.utils.samples import create_sample_event


from sentry_telegram.plugin import TelegramNotificationsPlugin


class BaseTest(PluginTestCase):
    @fixture
    def initialized_plugin(self):
        return TelegramNotificationsPlugin()


    def test_conf_key(self):
        assert self.initialized_plugin.conf_key == "sentry_telegram_py3"

    @responses.activate
    def send_notification_helper(self):
        responses.add("POST", "https://api.telegram.org")
        self.initialized_plugin.set_option('api_origin', 'https://api.telegram.org', self.project)
        self.initialized_plugin.set_option('receivers', '123', self.project)
        self.initialized_plugin.set_option('api_token', 'api:token', self.project)
        self.initialized_plugin.set_option(
            'message_template',
            '*[Sentry]* {project_name} {tag[level]}: {title}\n{message}\n{url}',
            self.project,
        )

        rule = Rule.objects.create(project=self.project, label="my rule")
        event = self.store_event(
            data={
                "message": "Hello world", 
                "level": "warning",
                "platform": "python"
            }, 
            project_id=self.project.id
        )
        
        notification = Notification(event=event, rule=rule)

        with self.options({"system.url-prefix": "http://example.com"}):
            self.initialized_plugin.notify(notification)

        request = responses.calls[0].request
        return request        

    @staticmethod
    def assert_notification_helper(request_call, message_text):
        assert request_call == dict(
            allow_redirects=False,
            method='POST',
            headers={'Content-Type': 'application/json'},
            url='https://api.telegram.org/botapi:token/sendMessage',
            json={
                'text': message_text,
                'parse_mode': 'Markdown',
                'chat_id': '123',
            },
            timeout=30,
            verify=True,
        )

    @responses.activate
    def test_complex_send_notification(self):
        responses.add("POST", "https://api.telegram.org")
        self.initialized_plugin.set_option('api_origin', 'https://api.telegram.org', self.project)
        self.initialized_plugin.set_option('receivers', '123', self.project)
        self.initialized_plugin.set_option('api_token', 'api:token', self.project)
        self.initialized_plugin.set_option(
            'message_template',
            '*[Sentry]* {project_name} {tag[level]}: {title}\n{message}\n{url}',
            self.project,
        )

        event = self.store_event(
            data={
                "message": "Hello world", 
                "level": "warning",
                "platform": "python"
            }, 
            project_id=self.project.id
        )
        rule = Rule.objects.create(project=self.project, label="my rule")
        
        notification = Notification(event=event, rule=rule)

        with self.options({"system.url-prefix": "http://example.com"}):
            self.initialized_plugin.notify(notification)

        request = responses.calls[0].request

        assert request.call_count == 1

        message_text = '*[Sentry]* Bar error: This is an example %(platform)s exception\n' \
                            'This is an example %(platform)s exception raven.scripts.runner in main\n' \
                            'http://testserver/baz/bar/issues/1/' % {'platform': 'python'}
        self.assert_notification_helper(
            request.call_args_list[0][1],
            message_text,
        )

    def test_get_empty_receivers_list(self):
        self.initialized_plugin.set_option('receivers', '', self.project)
        assert self.initialized_plugin.get_receivers(self.project) == []

    def test_get_config(self):
        self.initialized_plugin.get_config(self.project)

    def test_is_configured(self):
        self.initialized_plugin.set_option('receivers', '123', self.project)
        self.initialized_plugin.set_option('api_token', 'api:token', self.project)
        assert self.initialized_plugin.is_configured(self.project)

    def test_is_not_configured(self):
        assert not self.initialized_plugin.is_configured(self.project)
