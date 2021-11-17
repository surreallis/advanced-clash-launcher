import subprocess
import os
import sys

import requests
import yaml
from psutil import Process
from pywinauto import Application

from code.config import app_exe, app_path, account_path, api_path, game_server


class Account:
    def __init__(self, toon_dict):
        self.login = toon_dict['login']
        self.password = toon_dict['password']
        self.toon_key = toon_dict['toon_key']
        self.friendly_name = toon_dict['friendly_name']
        self.aliases = toon_dict['aliases']


class App:
    user: Account

    def __init__(self, acc, pid):
        self.user = acc
        self.proc = Process(pid)
        self.uia = Application(backend='uia').connect(process=pid)


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


def launch(account, district):
    response = requests.post(api_path + account.login, data={'password': account.password}).json()
    if response['status']:
        env = dict(os.environ, TT_GAMESERVER=game_server, TT_PLAYCOOKIE=response['token'], FORCE_DISTRICT=district)
        if account.toon_key < 6:
            env['FORCE_TOON_SLOT'] = str(account.toon_key)
        app = subprocess.Popen(app_exe, env=env, cwd=app_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return App(account, app.pid)
    return False


load_toons = _create_toon_loader()
