from enum import Enum
from math import sqrt

from code.calculator.entity.entity import Entity, Signal


class CogType(Enum):
    NORMAL = 0
    ATTACK = -10
    DEFENSE = 10


def guess_level_normal(max_hp, force=False):
    discr = 1 + 4 * max_hp
    x = (sqrt(discr) - 0.99) // 2
    if force or x * x + x == max_hp:
        return int(x - 1)
    return False


def guess_level(max_hp):
    possibilities = [
        (max_hp, False, CogType.NORMAL, 0),
        (max_hp * 2 // 3, True, CogType.NORMAL, 0),
        (max_hp - 1, False, CogType.ATTACK, 1),
        (max_hp + 2, False, CogType.DEFENSE, -1),
        ((max_hp + 3) * 2 // 3, True, CogType.DEFENSE, -1),
        ((max_hp - 1) * 2 // 3, True, CogType.ATTACK, 1)
    ]
    for hp, exe, ctype, delta in possibilities:
        calc = guess_level_normal(hp)
        if calc:
            return calc + delta, exe, ctype
    return guess_level_normal(max_hp, True) + 1, False, CogType.NORMAL


class Cog(Entity):
    def __init__(self, hp, max_hp):
        super().__init__(hp, max_hp)
        self.level, self.exe, self.subtype = guess_level(max_hp)
        self.entity_type = 'Cog'
        self.defense = max(2, min(13, self.level - 1) * 5 + self.subtype.value + (5 if self.exe else 0))

    def copy(self):
        rv = Cog(self.hp, self.max_hp)
        if hasattr(self, 'cog_id'):
            rv.cog_id = self.cog_id
        for i in self.em.effects:
            rv.add_effect(i.copy())
        return rv

    def calculate_defense(self):
        return max(0, self.em.process_data(Signal.COG_DEFENSE, self.defense))

    def add_combo_damage(self, key, coeff):
        queue_elements = [y for x, y in self.damage_queue if x == key]
        if len(queue_elements) > 1:
            self.append_to_queue('Combo', sum(queue_elements) * coeff)

    def __repr__(self):
        return f'Cog [{self.level}|{self.hp}/{self.max_hp}]'
