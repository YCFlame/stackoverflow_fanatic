#!/usr/bin/env python

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import argparse
import logging
import os
import re
import sys

from bs4 import BeautifulSoup
import requests


PROJECT_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(PROJECT_NAME)


class LoginError(Exception):
    pass


class LoginBot(object):

    LOGIN_URL = 'https://stackoverflow.com/users/login'

    def __init__(self):
        self._session = requests.Session()
        logger.setLevel(logging.INFO)

    def login(self, email, password):
        fkey = self._get_fkey()
        try:
            user_id = self._login(email, password, fkey)
        except LoginError as error:
            logger.error(error)
            sys.exit(error)
        else:
            num_days = self._parse_progress(user_id)
            logger.info(
                'User %s visited stackoverflow for %s consecutive days',
                user_id,
                num_days,
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
            problem = self._parse_error_message(html.text)
            raise LoginError('Failed to login: {}'.format(problem))
        else:
            parsed_link = re.match(r'/users/(?P<user_id>\d+)/.+', profile_link)
            return parsed_link.group('user_id')

    def _parse_error_message(self, html):
        message = re.search(
            'StackExchange.helpers.showMessage\(.+?,(.+?),.+?\)',
            html,
            re.DOTALL
        ).group(1)

        return message.strip('\n \'')

    def _parse_progress(self, user_id):
        badge_popup = self._session.get(
            'https://stackoverflow.com/users/activity/next-badge-popup?'
            'userId={}'.format(user_id)
        )
        return re.search('Fanatic - (\d+)/100', badge_popup.content).group(1)


def _parse_commandline_arguments():
    program_description = (
        'Log into your stackoverflow account to increment your'
        ' `consecutive days logged in` counter.'
    )

    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument(
        'email',
        help='the email address registered with your account'
    )
    parser.add_argument(
        'password',
        help='the password to your account'
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_commandline_arguments()

    LoginBot().login(args.email, args.password)
