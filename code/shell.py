from cmd import Cmd
import subprocess
from typing import List
from threading import Timer

from pywinauto import Application

from code import config
from code.calculator.entity.cog import Cog
from code.calculator.generator import zap_test
from code.calculator.state import State
from code.imagery import separate_image_into_health_values, sanctify_health_values
from code.util import monkey, load_toons, launch, App


def unfreeze(app):
    def _unfreeze():
        print(f'\n! Unfreezing {app.user.friendly_name}\n')
        app.proc.resume()
    return _unfreeze


@monkey('mc', 'multicontroller')
@monkey('ds', 'district')
@monkey('lc', 'launch')
@monkey('ls', 'list')
@monkey('cr', 'recognize')
@monkey('rc', 'rcombos')
@monkey('dc', 'disconnect')
class ACLShell(Cmd):
    intro = 'Welcome to Advanced Clash Launcher v0.1.'
    district = config.default_district
    apps: List[App] = []
    multicontroller: Application = False

    def __init__(self):
        super().__init__()
        self.toons = load_toons()
        self.update_prompt()

    def update_prompt(self):
        small_district = self.district.split(' ')[0]
        self.prompt = f'[{small_district}] ACL> '

    def update_apps(self):
        self.apps = [x for x in self.apps if x.uia.is_process_running()]

    def do_multicontroller(self, arg):
        """
            Launches the multicontroller.
            Example usage: multicontroller
        """
        if not self.multicontroller or not self.multicontroller.is_process_running():
            print('Starting multicontroller...')
            popen = subprocess.Popen(config.multicontroller_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.multicontroller = Application(backend='uia').connect(process=popen.pid)
        self.multicontroller.top_window().set_focus()

    def do_district(self, arg):
        """
            Changes the current district.
            Example usage: district tesla
        """
        if arg not in config.district_list:
            print('Unknown district:', arg)
            return

        print('Setting current district to', config.district_list[arg])
        self.district = config.district_list[arg]
        self.update_prompt()

    def do_launch(self, arg):
        """
            Launches toons.
            Example usage: launch toon_alias1 toon_alias2
        """
        self.update_apps()
        for i in arg.split(' '):
            if not i:
                continue
            if i not in self.toons:
                print(f'! Could not find toon {i}')
                continue

            acc = self.toons[i]
            if [x for x in self.apps if x.user.login == acc.login]:
                print(f'! Account {acc.login} is already in use. Stop it first.')
                continue
            app = launch(acc, self.district)
            if not app:
                print(f'! Error launching {acc.friendly_name}')
                continue
            self.apps.append(app)
            print(f'Launched {acc.friendly_name}')

    def do_list(self, arg):
        """
            Prints the list of launched toons.
            Example usage: list
        """
        self.update_apps()
        if not self.apps:
            print('No toons running')
        else:
            print('Toons running:')
            for i in self.apps:
                print('*', i.user.friendly_name)

    def do_disconnect(self, arg):
        """
            Disconnects toons.
            Example usage: disconnect toon_alias1 toon_alias2
        """
        arg_split = arg.split(' ')
        windows_to_close = [x for x in self.apps if [y for y in x.user.aliases if y in arg_split]]
        for i in windows_to_close:
            if i.uia.is_process_running():
                print(f'Disconnecting {i.user.friendly_name}')
                i.uia.top_window().close()
        self.update_apps()

    def do_recognize(self, arg):
        """
            Uses screen recognition-adjacent techniques to get the cog HP values.
            Example usage: recognize
        """
        debug = 'debug' in arg
        func = separate_image_into_health_values if debug or not arg else sanctify_health_values
        self.update_apps()
        for app in self.apps:
            img = app.uia.top_window().capture_as_image()
            print(app.user.friendly_name, func(img, debug))

    def do_freeze(self, arg):
        """
            Freezes a toon for a specified time period (in seconds). Use at your own risk.
            Note that long intervals may cause heartbeat crash. Also I don't suggest using this with mods nearby.
            Example usage: freeze toon_alias1 6
        """
        s1 = arg.split()
        if len(s1) != 2:
            print('Incorrect arguments.')
            return
        toon, time = s1[0], int(s1[1])

        for app in self.apps:
            if toon in app.user.aliases:
                print(f'Freezing {app.user.friendly_name} for {time} seconds')
                app.proc.suspend()
                Timer(time, unfreeze(app)).start()

    def do_rcombos(self, arg):
        """
            Uses screen recognition to find zap combos.
            Example usage: rcombos
        """
        self.update_apps()
        already_used = set()
        for app in self.apps:
            hvs = sanctify_health_values(app.uia.top_window().capture_as_image())
            print(app.user.friendly_name, hvs if hvs else '(not in battle)')
            if not hvs:
                continue

            key = ' '.join(['-'.join(str(y)) for y in hvs])
            if key in already_used:
                continue
            already_used.add(key)

            state = State()
            for i in reversed(hvs):
                state.spawn_cog(Cog(i[0], i[1]))
            print(zap_test(state))

    def do_zap(self, arg):
        """Finds zap combos."""
        cogs = reversed(arg.split(' '))
        state = State()
        for i in cogs:
            hp = int(i.replace('e', ''))
            if hp < 20:
                hp = (hp + 1) * (hp + 2) * (1.5 if 'e' in i else 1)
            state.spawn_cog(Cog(hp, hp))
        print(zap_test(state))
