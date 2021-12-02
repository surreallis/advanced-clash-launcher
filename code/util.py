import subprocess
import os
import sys

import requests
import yaml
from psutil import Process
from pywinauto import Application

from code.config import game_data, account_path


class Account:
    def __init__(self, toon_dict):
        self.login = toon_dict['login']
        self.password = toon_dict['password']
        self.toon_key = toon_dict['toon_key']
        self.friendly_name = toon_dict['friendly_name']
        self.aliases = toon_dict['aliases']
        self.game = toon_dict.get('game', 'clash')


class App:
    user: Account

    def __init__(self, acc, pid):
        self.user = acc
        self.proc = Process(pid)
        self.uia = Application(backend='uia').connect(process=pid)
        self.shady = False


def _create_toon_loader():
    accounts = {}

    def _load_toons():
        if not accounts:
            with open(account_path) as file:
                loaded_accounts = yaml.load(file, Loader=yaml.SafeLoader)
                for i in loaded_accounts:
                    account_object = Account(i)
                    for j in i['aliases']:
                        if j in accounts:
                            print(f'Error: account {j} added twice')
                            sys.exit(1)
                        accounts[j] = account_object
        return accounts
    return _load_toons


def monkey(see, do):
    def decorate(cls):
        setattr(cls, f'do_{see}', getattr(cls, f'do_{do}'))
        return cls
    return decorate


def launch(account, district, queue=False):
    api_path = game_data[account.game]['api_path']
    if account.game == 'clash':
        response = requests.post(api_path, data={'password': account.password}).json()
    else:
        if queue:
            response = requests.post(api_path, data={'queueToken': queue}).json()
        else:
            response = requests.post(api_path, data={'username': account.login, 'password': account.password}).json()
            if response['success'] == 'partial':
                print('Two-partial authentication detected. Enter the authenticator token below.')
                auth = input()
                if not auth:
                    return False
                response = requests.post(api_path, data={'appToken': auth, 'authToken': response['responseToken']})
        if response['success'] == 'delayed':
            print('Login delayed. You\'re at position', response['position'], 'relogging in 15 seconds.')
            return 15, lambda: launch(account, district, response['queueToken'])

    if response.get('status', response.get('success', None)):
        if account.game == 'clash':
            env = dict(os.environ, TT_GAMESERVER=game_data[account.game]['game_server'],
                       TT_PLAYCOOKIE=response['token'], FORCE_DISTRICT=district)
            if account.toon_key < 6:
                env['FORCE_TOON_SLOT'] = str(account.toon_key)
        else:
            env = dict(os.environ, TTR_GAMESERVER=response['gameserver'], TTR_PLAYCOOKIE=response['cookie'])
        app = subprocess.Popen(game_data[account.game]['app_exe'], env=env, stderr=subprocess.DEVNULL,
                               cwd=game_data[account.game]['app_path'], stdout=subprocess.DEVNULL)
        return App(account, app.pid)
    return False


load_toons = _create_toon_loader()
