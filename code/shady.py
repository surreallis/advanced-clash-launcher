import random
from threading import Timer


def attach_keep_alive(app):
    def _run():
        if app.uia.is_process_running():
            t = random.uniform(60.0, 240.0)
            if app.shady.ka:
                k = random.choice(['{HOME down}{HOME up}', '{END down}{END up}'])
                app.uia.top_window().type_keys(k)
            Timer(t, _run).start()

    Timer(random.uniform(10.0, 20.0), _run).start()


class ShadyController:
    ka: bool = False

    def __init__(self, app):
        print('Connected shady controller to', app.user.friendly_name)
        attach_keep_alive(app)

    def modify(self, key):
        if key not in ['ka']:
            print('Unknown key:', key)
        setattr(self, key, not getattr(self, key))
        print('Key', key, 'set to', getattr(self, key))
