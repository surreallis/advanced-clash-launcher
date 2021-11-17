def get_average_k(k, stuff):
    arr = [x[k] for x in stuff]
    return sum(arr) / len(arr) if arr else 0


def get_compounds(matrix):
    w = len(matrix[0])
    h = len(matrix)
    mc = [x[:] for x in matrix]
    compounds = []
    q = []
    while True:
        start = False
        bb = False
        for row in range(h):
            for col in range(w):
                if not mc[row][col]:
                    start = (row, col)
                    bb = True
                    break
            if bb:
                break

        if not start:
            return compounds
        current_compound = []
        q.append(start)
        while q:
            v = q.pop()
            if mc[v[0]][v[1]]:
                continue
            current_compound.append(v)
            mc[v[0]][v[1]] = True
            if v[0] > 0:
                q.append((v[0] - 1, v[1]))
            if v[0] < h - 1:
                q.append((v[0] + 1, v[1]))
            if v[1] > 0:
                q.append((v[0], v[1] - 1))
            if v[1] < w - 1:
                q.append((v[0], v[1] + 1))
        compounds.append(current_compound)


def print_matrix(matrix):
    print('_' * (len(matrix[0]) + 2))
    print(*['|' + ''.join(['o' if y else ' ' for y in x]) + '|' for x in matrix], sep='\n')
    print('_' * (len(matrix[0]) + 2))


def detect_number_topologically(submatrix, debug=False):
    def d():
        full_count = len([x for y in submatrix for x in y if x])
        if full_count <= 5:
            return ''
        matrix_size = (len(submatrix), len(submatrix[0]))
        if (matrix_size[1] - 2) * 2.5 <= matrix_size[0] - 2:
            return '1'

        wide_rows = [x for x in range(matrix_size[0]) if len([y for y in submatrix[x] if y]) > matrix_size[1] / 3]
        if wide_rows and len(wide_rows) <= 2 and 1 in wide_rows and (len(wide_rows) == 1 or 2 in wide_rows):
            return '7'
        join_compounds = get_compounds(submatrix)
        if len(join_compounds) >= 3:
            return '8'

        if len(join_compounds) == 1:
            shrink_compounds = get_compounds([u[1:-1] for u in submatrix[1:-1]])
            if len(shrink_compounds) <= 2:
                return '7'
            da_row = [x for x in submatrix[-2][1:-1] if not x]
            da_row2 = [x for x in submatrix[-3][1:-1] if not x]
            da_row3 = [x for x in submatrix[1][1:-1] if not x]
            da_row4 = [x for x in submatrix[-4][1:-1] if not x]
            if not da_row2 or len(da_row) <= 2 or not da_row4:
                return '2'
            if not da_row3:
                return '5'
            if len(shrink_compounds) >= 5 or len(get_compounds([u[2:-2] for u in submatrix[1:-1]])) >= 5:
                return '3'
            return '5'

        prop = (matrix_size[0] - 2) * (matrix_size[1] - 2) / len(join_compounds[1])
        if prop <= 4:
            return '0'
        avg_y = get_average_k(0, join_compounds[1])
        if avg_y > matrix_size[0] / 2:
            return '6'
        if prop <= 7 and len(join_compounds[1]) >= 6:  # why do i need to do the second check
            return '9'
        return '4'

    ans = d()
    if debug:
        print_matrix(submatrix)
        print(ans)
        print('')
    return ans

