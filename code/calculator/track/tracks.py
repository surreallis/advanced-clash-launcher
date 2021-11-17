from code.calculator.entity.effects import EffectSoak, EffectJump
from code.calculator.track.track import Track, TrackParameters


class Squirt(Track):
    def __init__(self, ap):
        self.damage_values = [4, 8, 12, 21, 30, 56, 80, 115]
        self.soak_times = [3, 3, 4, 4, 5, 5, 6, 6]
        self.names = ['sq flower', 'glass', 'squirtgun', 'wb', 'seltzer', 'hose', 'cloud', 'geyser']
        tp = TrackParameters('squirt', 0.95)
        super().__init__(tp, ap)

    def try_add_soak(self, entities, key):
        if key in entities:
            entities[key].add_effect(EffectSoak(self.soak_times[self.level]))

    def get_priority(self):
        return 5 + self.level * 0.1

    def apply(self, state):
        cog = state.entities[f'Cog{self.target}']
        if cog.hp <= 0:
            return
        damage_value = self.damage_values[self.level]
        cog.append_to_queue('Squirt', damage_value)

        cog.add_effect(EffectSoak(self.soak_times[self.level]))
        if self.prestige:
            self.try_add_soak(state.entities, f'Cog{self.target - 1}')
            self.try_add_soak(state.entities, f'Cog{self.target + 1}')

    def cleanup(self, state):
        cogs = [x for x in state.entities.values() if x.entity_type == 'Cog']
        for cog in cogs:
            cog.process_queue()
            cog.add_combo_damage('Squirt', 0.2)
            cog.explode_queue()


class Zap(Track):
    def cleanup(self, state):
        pass

    def __init__(self, ap):
        tp = TrackParameters('zap', 0.3)
        super().__init__(tp, ap)
        self.names = ['joybuzzer', 'rug', 'balloon', 'kart', 'taser', 'tv', 'tesla', 'lightning']
        self.damage_values = [4, 6, 10, 16, 24, 40, 66, 80]

    def calculate_accuracy(self, state, other_turns):
        cog = state.entities[f'Cog{self.target}']
        if cog.em.find_effect('Soak'):
            return 1
        return super().calculate_accuracy(state, other_turns)

    def get_priority(self):
        return 6 + self.level * 0.1

    def damage(self, state, target, mult, jumped=False):
        soak = state.entities[f'Cog{target}'].em.find_effect('Soak')
        if soak and soak.turns > 0:
            soak.turns -= 1
        state.entities[f'Cog{target}'].deal_damage(self.damage_values[self.level] * mult)
        state.entities[f'Cog{target}'].already_hit = True
        if jumped:
            state.entities[f'Cog{target}'].jumped = True

    def find_next_target(self, state, target, mult):
        deltas = [+1, +2, -1, -2]
        for i in deltas:
            key = f'Cog{i + target}'
            if key in state.entities:
                cog = state.entities[key]
                if not hasattr(cog, 'already_hit') and cog.em.find_effect('Soak') and not cog.em.find_effect('Jump'):
                    cog.add_effect(EffectJump())
                    self.damage(state, i + target, mult, True)
                    return i
        return 0

    def apply(self, state):
        if not state.entities[f'Cog{self.target}'].em.find_effect('Soak'):
            state.entities[f'Cog{self.target}'].append_to_queue('Zap', self.damage_values[self.level])
            return

        self.damage(state, self.target, 3)
        delta = self.find_next_target(state, self.target, 2.5 if self.prestige else 2.25)
        if delta:
            self.find_next_target(state, self.target + delta, 2 if self.prestige else 1.5)

        cogs = [x for x in state.entities.values() if x.entity_type == 'Cog']
        for cog in cogs:
            if hasattr(cog, 'already_hit'):
                del cog.already_hit
