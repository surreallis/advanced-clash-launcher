from code.calculator.track.turn import FunctionTurn


class State:
    def __init__(self):
        self.entities = {}
        self.substates = {}
        self.turn_number = 0

    def spawn_cog(self, cog):
        cogs = [x for x in self.entities.values() if x.entity_type == 'Cog']
        cog.cog_id = len(cogs)
        self.entities[f'Cog{cog.cog_id}'] = cog

    def save(self, name):
        self.substates[name] = {'entities': {x: y.copy() for x, y in self.entities.items()}, 'turn': self.turn_number}

    def load(self, name):
        if name not in self.substates:
            return
        ss = self.substates[name]
        self.entities = {x: y.copy() for x, y in ss['entities'].items()}
        self.turn_number = ss['turn']

    def run(self, turns):
        accuracy = 1
        acc_calculated = set()

        for i in turns:
            if not i.is_valid(self):
                return

        turns = sorted(turns, key=lambda t: t.get_priority() + t.get_priority2())
        j = 1
        while j < len(turns):
            if turns[j].get_priority() > turns[j - 1].get_priority():
                local_j = j - 1  # bruh
                turns.insert(j, FunctionTurn(lambda state: turns[local_j].cleanup(state)))
                j += 1
            j += 1
        local_len = len(turns) - 1
        turns.append(FunctionTurn(lambda state: turns[local_len].cleanup(state)))

        for i in turns:
            acc_key = i.get_identifier() + '__' + i.get_targets()
            if acc_key not in acc_calculated:
                acc_calculated.add(acc_key)
                accuracy *= i.calculate_accuracy(self, turns)
            i.apply(self)

        return accuracy

    def cleanup(self):
        for i in self.entities.values():
            i.cleanup()
