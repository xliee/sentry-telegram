# coding: utf-8
import logging
from collections import defaultdict

from django import forms
from django.utils.translation import gettext_lazy as _

from sentry.plugins.bases import notify
from sentry.http import safe_urlopen
from sentry_plugins.base import CorePluginMixin
from sentry.utils.safe import safe_execute

from . import __version__, __doc__ as package_doc


class TelegramNotificationsOptionsForm(notify.NotificationConfigurationForm):
    api_origin = forms.CharField(
        label=_('Telegram API origin'),
        widget=forms.TextInput(attrs={'placeholder': 'https://api.telegram.org'}),
        initial='https://api.telegram.org'
    )
    api_token = forms.CharField(
        label=_('BotAPI token'),
        widget=forms.TextInput(attrs={'placeholder': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'}),
        help_text=_('Read more: https://core.telegram.org/bots/api#authorizing-your-bot'),
    )
    receivers = forms.CharField(
        label=_('Receivers'),
        widget=forms.Textarea(attrs={'class': 'span6'}),
        help_text=_('Enter receivers IDs (one per line). Personal messages, group chats and channels also available.'))

    message_template = forms.CharField(
        label=_('Message template'),
        widget=forms.Textarea(attrs={'class': 'span4'}),
        help_text=_('Set in standard python\'s {}-format convention, available names are: '
                    '{project_name}, {url}, {title}, {message}, {tag[%your_tag%]}'),
        initial='*[Sentry]* {project_name} {tag[level]}: *{title}*\n```{message}```\n{url}'
    )

    disable_web_preview = forms.BooleanField(
        label=_('Disable web preview'),
        help_text=_('Disable web preview for links in messages'),
        widget=forms.CheckboxInput(),
        initial=False,  
    )



class TelegramNotificationsPlugin(CorePluginMixin, notify.NotificationPlugin):
    title = 'Telegram Notifications (xliee)'
    slug = 'xliee_sentry_telegram'
    description = package_doc
    version = __version__
    author = 'xliee'
    author_url = 'https://github.com/xliee/sentry-telegram'
    resource_links = [
        ('Source', 'https://github.com/xliee/sentry-telegram'),
    ]

    conf_key = 'xliee_sentry_telegram'
    conf_title = title

    project_conf_form = TelegramNotificationsOptionsForm

    logger = logging.getLogger('sentry.plugins.xliee_sentry_telegram')

    def is_configured(self, project, **kwargs):
        return bool(self.get_option('api_token', project) and self.get_option('receivers', project))

    def get_config(self, project, **kwargs):
        return [
            {
                'name': 'api_origin',
                'label': 'Telegram API origin',
                'type': 'text',
                'placeholder': 'https://api.telegram.org',
                'validators': [],
                'required': True,
                'default': 'https://api.telegram.org'
            },
            {
                'name': 'api_token',
                'label': 'BotAPI token',
                'type': 'text',
                'help': 'Read more: https://core.telegram.org/bots/api#authorizing-your-bot',
                'placeholder': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
                'validators': [],
                'required': True,
            },
            {
                'name': 'receivers',
                'label': 'Receivers',
                'type': 'textarea',
                'help': 'Enter receivers IDs (one per line). Personal messages, group chats and channels also available. \n(Optional) Enter the topic id separated by a semicolon (;)',
                'placeholder': '-123456789;2',
                'validators': [],
                'required': True,
            },
            {
                'name': 'message_template',
                'label': 'Message Template',
                'type': 'textarea',
                'help': 'Set in standard python\'s {}-format convention, available names are: '
                    '{project_name}, {url}, {title}, {message}, {tag[%your_tag%]}. Undefined tags will be shown as [NA]',
                'validators': [],
                'required': True,
                'default': '*[Sentry]* {project_name} {tag[level]}: *{title}*\n```{message}```\n{url}'
            },
            {
                'name': 'disable_web_preview',
                'label': 'Disable web preview',
                'type': 'bool',
                'help': 'Disable web preview for links in messages',
                'validators': [],
                'required': False,
                'default': False,
            },

        ]

    def build_message(self, group, event):
        the_tags = defaultdict(lambda: '[NA]')
        the_tags.update({k:v for k, v in event.tags})
        names = {
            'title': event.title,
            'tag': the_tags,
            'message': event.message,
            'culprit': group.culprit,
            'project_name': group.project.name,
            'url': group.get_absolute_url(),
        }

        template = self.get_message_template(group.project)

        text = template.format(**names)
        return {
            'text': text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': self.get_option('disable_web_preview', group.project) or False,
        }

    def build_url(self, project):
        return '%s/bot%s/sendMessage' % (self.get_option('api_origin', project), self.get_option('api_token', project))

    def get_message_template(self, project):
        return self.get_option('message_template', project)

    def get_receivers(self, project):
        receivers = self.get_option('receivers', project)
        if not receivers:
            return []
        return list(filter(bool, receivers.strip().splitlines()))

    def send_message(self, url, payload, chat_id, message_thread_id):
        payload['chat_id'] = chat_id
        self.logger.debug('Sending message to chat_id: %s ' % chat_id)
        if message_thread_id:
            payload['message_thread_id'] = message_thread_id
            self.logger.debug('Sending message to message_thread_id: %s ' % message_thread_id)
            
        response = safe_urlopen(
            method='POST',
            url=url,
            json=payload,
        )
        self.logger.debug('Response code: %s, content: %s' % (response.status_code, response.content))

    def notify_users(self, group, event, **kwargs):
        self.logger.debug('Received notification for event: %s' % event)
        receivers = self.get_receivers(group.project)
        self.logger.debug('for receivers: %s' % ', '.join(receivers or ()))
        payload = self.build_message(group, event)
        self.logger.debug('Built payload: %s' % payload)
        url = self.build_url(group.project)
        self.logger.debug('Built url: %s' % url)
        for receiver in receivers:
            receiver_info = receiver.split(";")
            chat_id = receiver_info[0]
            message_thread_id = receiver_info[1] if len(receiver_info) == 2 else None
            safe_execute(self.send_message, url, payload, chat_id, message_thread_id, _with_transaction=False)
