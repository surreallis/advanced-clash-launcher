from abc import abstractmethod, ABC

ident = 0


class Turn(ABC):
    def __init__(self):
        global ident
        self.id = ident
        ident += 1

    def is_valid(self, state):
        return True

    def get_identifier(self):
        return str(self.id)

    def get_targets(self):
        return ''

    def calculate_accuracy(self, state, other_turns):
        return 0.95

    def get_priority(self):
        return 0

    def get_priority2(self):
        return 0

    @abstractmethod
    def apply(self, state):
        pass

    @abstractmethod
    def cleanup(self, state):
        pass


class FunctionTurn(Turn):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def __repr__(self):
        return f'Func[]'

    def apply(self, state):
        v = self.func
        v(state)

    def cleanup(self, state):
        pass
