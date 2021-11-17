from abc import abstractmethod, ABC
from enum import Enum
from math import ceil
from typing import List


class Signal(Enum):
    TAKE_DAMAGE = 1
    DAMAGE_QUEUE = 2
    COG_DEFENSE = 3
    BASE_ACCURACY = 4


class Entity:
    def __init__(self, hp, max_hp):
        self.em = EffectManager()
        self.hp = hp
        self.max_hp = max_hp
        self.damage_queue = []
        self.entity_type = 'Unknown'

    def copy(self):
        rv = Entity(self.hp, self.max_hp)
        for i in self.em.effects:
            rv.add_effect(i.copy())
        return rv

    def add_effect(self, eff):
        self.em.add_effect(eff)

    def append_to_queue(self, name, dmg):
        self.damage_queue.append((name, self.em.process_data(Signal.TAKE_DAMAGE, dmg)))

    def process_queue(self):
        self.damage_queue = self.em.process_data(Signal.DAMAGE_QUEUE, self.damage_queue)

    def explode_queue(self):
        self.process_queue()
        for i in self.damage_queue:
            self.deal_damage(i[1])
        self.damage_queue = []

    def deal_damage(self, val):
        self.hp -= ceil(val)

    def cleanup(self):
        self.em.cleanup()


class EffectManager:
    effects: List['Effect']

    def __init__(self):
        self.effects = []

    def add_effect(self, e):
        found = self.find_effect(e.name)
        if not found:
            e.manager = self
            self.effects.append(e)
        else:
            found.update_with(e)

    def dispatch_signal(self, sid, data):
        for i in self.effects:
            i.receive_signal(sid, data)

    def process_data(self, sid, data):
        for i in self.effects:
            if i.can_process(sid):
                data = i.process(sid, data)
        return data

    def find_effect(self, name):
        found = [x for x in self.effects if name == x.name]
        if not found:
            return False
        return found[0]

    def cleanup(self):
        self.effects = [x for x in self.effects if x.cleanup()]


class Effect(ABC):
    manager = False
    name = ''

    @abstractmethod
    def receive_signal(self, sid, data):
        pass

    @abstractmethod
    def copy(self):
        pass

    def process(self, sid, data):
        return data

    def can_process(self, sid):
        return False

    def update_with(self, other):
        pass

    def cleanup(self):
        return True
