#!/usr/bin/env python

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import re
import sys

from bs4 import BeautifulSoup
import requests


EMAIL = '<YOUR EMAIL ADDRESS>'
PASSWORD = '<YOUR PASSWORD>'


class LoginError(Exception):
    pass


class LoginBot(object):

    LOGIN_URL = 'https://stackoverflow.com/users/login'

    def __init__(self):
        self._session = requests.Session()

    def login(self, email, password):
        fkey = self._get_fkey()
        try:
            user_id = self._login(email, password, fkey)
        except LoginError as error:
            sys.exit(error)
        else:
            num_days = self._parse_progress(user_id)
            print(
                'User {} visited stackoverflow for {} consecutive days'.format(
                    user_id, num_days
                )
            )

    def _get_fkey(self):
        login_page = self._session.get(LoginBot.LOGIN_URL)
        html = BeautifulSoup(login_page.content)

        return html.find(
            id='se-login-form'
        ).find(
            'input',
            {'type': 'hidden', 'name': 'fkey'}
        )['value']

    def _login(self, email, password, fkey):
        credentials = {
            'email': email,
            'password': password,
            'fkey': fkey,
        }

        login_response = self._session.post(
            LoginBot.LOGIN_URL,
            data=credentials
        )
        html = BeautifulSoup(login_response.content)

        try:
            profile_link = html.find('a', {'class': 'profile-me'})['href']
        except TypeError:
            problem = self._parse_error_message(html)
            raise LoginError('Failed to login: {}'.format(problem))
        else:
            parsed_link = re.match(r'/users/(?P<user_id>\d+)/.+', profile_link)
            return parsed_link.group('user_id')

    def _parse_error_message(self, html):
        error_script_pattern = re.compile(
            'StackExchange.helpers.showMessage\(.+?,(.+?),.+?\)',
            re.DOTALL
        )

        script = html.find(text=error_script_pattern)
        message = error_script_pattern.search(script).group(1)

        return message.strip('\n \'')

    def _parse_progress(self, user_id):
        progress_pattern = re.compile('Fanatic - (\d+)/100')

        badge_popup = self._session.get(
            'https://stackoverflow.com/users/activity/next-badge-popup?'
            'userId={}'.format(user_id)
        )
        html = BeautifulSoup(badge_popup.content)
        label = html.find(text=progress_pattern)

        return progress_pattern.match(label).group(1)


if __name__ == '__main__':
    LoginBot().login(EMAIL, PASSWORD)
