from itertools import combinations_with_replacement, product

from code.calculator.track.track import AttackParameters
from code.calculator.track.tracks import Squirt, Zap


def zap_traversal(n):
    zap_iter = combinations_with_replacement([4, 5, 6, 7], 2)
    zap_targets = product(range(n), range(n))
    squirt_iter = combinations_with_replacement([4, 5, 6, 7], 2)
    squirt_targets = product(range(n), range(n))
    yield from product(zap_iter, squirt_iter, zap_targets, squirt_targets)


def prettyprint(turn):
    return ', '.join([x.names[x.level] + ' ' + x.get_targets() for x in reversed(turn)])


track_costs = {'zap': 12, 'squirt': 3}
level_costs = [1, 2, 3, 5, 8, 30, 75, 150]


def get_cost(turn):
    start = sum([track_costs[x.id] * level_costs[x.level] for x in turn])
    if isinstance(turn[0], Squirt) and isinstance(turn[1], Squirt) and (turn[0].target - turn[1].target) ** 2 != 4:
        start += 1
    return start


def zap_test(state):
    state.save('zap-test')
    min_cost = 1000000
    min_combo = None

    for zap, squirt, zt, st in zap_traversal(len(state.entities)):
        turn = [
            Squirt(AttackParameters(st[0], squirt[0], 1)),
            Squirt(AttackParameters(st[1], squirt[1], 1)),
            Zap(AttackParameters(zt[0], zap[0], 1)),
            Zap(AttackParameters(zt[1], zap[1], 1)),
        ]
        cost = get_cost(turn)
        if cost < min_cost:
            state.run(turn)
            state.cleanup()
            if not [x for x in state.entities.values() if x.hp > 0]:
                min_cost = cost
                min_combo = prettyprint(turn)
            state.load('zap-test')
    return min_combo
