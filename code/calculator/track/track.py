from abc import ABC

from code.calculator.entity.cog import Signal
from code.calculator.track.turn import Turn


class AttackParameters:
    def __init__(self, tgt=-1, level=0, prestige=False):
        self.target = tgt
        self.level = level
        self.prestige = prestige


class TrackParameters:
    def __init__(self, name, base_acc):
        self.id = name
        self.base_acc = base_acc


class Track(Turn, ABC):
    def __init__(self, tp, ap):
        super().__init__()
        self.id = tp.id
        self.base_acc = tp.base_acc
        self.target = ap.target
        self.level = ap.level
        self.prestige = ap.prestige

    def get_priority2(self):
        return self.level * 0.1

    def __repr__(self):
        return f'{self.id} [{self.level}]'

    def get_targets(self):
        letter = 'O' if self.prestige else 'X'
        nonletter = '-'
        if self.target == -1:
            return letter * 4
        else:
            return nonletter * (3 - self.target) + letter + nonletter * self.target

    def is_valid(self, state):
        if self.level not in [0, 1, 2, 3, 4, 5, 6, 7]:
            return False
        cogs = [x for x in state.entities.values() if x.entity_type == 'Cog']
        return cogs and (self.target == -1 or self.target < len(cogs)) and f'Cog{self.target}' in state.entities

    def calculate_accuracy(self, state, other_turns):
        targeted_cogs = [x for x in state.entities.values() if x.entity_type == 'Cog' and
                         (self.target == -1 or x.cog_id == self.target)]
        max_def = max([x.calculate_defense() for x in targeted_cogs])
        base_acc = min([x.em.process_data(Signal.BASE_ACCURACY, self.base_acc) for x in targeted_cogs])
        return min(0.95, -max_def / 100 + 0.7 + base_acc)
