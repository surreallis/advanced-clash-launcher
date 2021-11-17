from code.calculator.entity.entity import Effect


class EffectSoak(Effect):
    def __init__(self, turns):
        self.name = 'Soak'
        self.turns = turns

    def update_with(self, other):
        self.turns = max(self.turns, other.turns)

    def receive_signal(self, sid, data):
        pass

    def copy(self):
        return EffectSoak(self.turns)

    def cleanup(self):
        self.turns -= 1
        return self.turns > 0


class EffectJump(Effect):
    name = 'Jump'

    def receive_signal(self, sid, data):
        pass

    def copy(self):
        return EffectJump()

    def cleanup(self):
        return False
