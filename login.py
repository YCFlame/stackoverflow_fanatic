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

    def login(self, email, password):
        fkey = self._get_fkey()
        try:
            self._login(email, password, fkey)
        except LoginError as error:
            sys.exit(error)

    def _get_fkey(self):
        login_page = requests.get(LoginBot.LOGIN_URL)
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

        login_response = requests.post(LoginBot.LOGIN_URL, data=credentials)
        html = BeautifulSoup(login_response.content)

        try:
            profile_link = html.find('a', {'class': 'profile-me'})['href']
        except TypeError:
            raise LoginError('Failed to login!')
        else:
            parsed_link = re.match(r'/users/(?P<user_id>\d+)/.+', profile_link)
            print('Logged in as user {}'.format(parsed_link.group('user_id')))


if __name__ == '__main__':
    LoginBot().login(EMAIL, PASSWORD)
