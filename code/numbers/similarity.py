import os
from difflib import SequenceMatcher


def _ld_loader():
    data = []
    learning_data_files = ['learning_data.txt', 'learning_data_hd.txt']

    def _load_ld():
        if not data:
            for u in learning_data_files:
                ld_path = os.path.join(os.path.dirname(__file__), '../..', 'learning', u)
                with open(ld_path) as f:
                    f_split = f.read().split('\n\n')
                    for i in f_split:
                        if not i:
                            continue
                        s1 = i.split('\n')
                        answer = s1.pop()
                        if ' ' in answer:
                            s2 = answer.split(' ')
                            answer = s2[0]
                            mult = float(s2[1])
                        else:
                            mult = 1
                        data.append((s1, answer, mult))
        return data

    return _load_ld


load_ld = _ld_loader()


def detect_number_by_similarity(matrix, debug=False):
    matrix_strings = [''.join(['.' if not y else 'o' for y in x]) for x in matrix]
    learning_data = load_ld()
    min_ratio = ('', len(matrix) / 2)
    for inp, outp, mult in learning_data:
        cs = abs(len(matrix_strings) - len(inp))
        for i, j in zip(matrix_strings, inp):
            cs += 1 - SequenceMatcher(None, i, j).ratio()
        cs *= mult
        if cs < min_ratio[1]:
            min_ratio = (outp, cs)

    if debug:
        for i in matrix:
            print(i)
        print(min_ratio)
        print('')
    return min_ratio[0]
