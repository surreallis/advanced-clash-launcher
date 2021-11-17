from code.numbers.similarity import detect_number_by_similarity
from code.numbers.topology import detect_number_topologically

slant_shift = 3


def color_similarity(color, delta):
    return (color[0] - delta[0]) ** 2 + (color[1] - delta[1]) ** 2 + (color[2] - delta[2]) ** 2


def is_dark(color):
    return int(color[0]) + int(color[1]) + int(color[2]) <= 90


def is_bright_or_dark(color):
    return color[2] <= 5 and color[1] + color[2] >= 60


def is_bright_dark_gray(color):
    return is_bright_or_dark(color) or color_similarity(color, (170, 170, 170)) < 300


def cog_hp_value(color):
    if is_bright_or_dark(color):
        return 2
    if is_dark(color) or color_similarity(color, (170, 170, 170)) < 300:
        return 1
    return 0


def load_img(img):
    w, h = img.size
    pix = list(img.getdata())
    return [pix[n:n+w] for n in range(0, w*h, w)]


def better_len(arr, threshold, width):  # it just works
    return len(arr) + len([x for x in arr if x - 1 not in arr]) - \
           len([x for x in arr if x + width > threshold > x - width])


def find_separating_height2(matrix):
    window_bar_height = 30
    matrix = matrix[window_bar_height:]
    window_height = len(matrix)
    if window_height < 100:
        return False
    window_width = len(matrix[0])

    starting_height = 0 if window_width > window_height else window_height - window_width
    v_ranges = (window_height // 11 + starting_height, window_height // 8 + starting_height)
    colored_pixels = [[cog_hp_value(x) for x in matrix[y]] for y in range(v_ranges[0], v_ranges[1])]
    ranges = (window_width // 17, window_width // 13)

    for i in range(v_ranges[1] - v_ranges[0]):
        cog_hps = []
        current_z_v = current_green_hits = 0
        current_row = colored_pixels[i]
        for j in range(window_width):
            cp = current_row[j]
            if cp:
                current_z_v += 1
                if cp > 1:
                    current_green_hits += 1
            elif current_z_v:
                if ranges[0] < current_z_v < ranges[1] and current_green_hits > 5:
                    cog_hps.append((j - current_z_v, j))
                current_z_v = current_green_hits = 0
        if cog_hps:
            for j in range(i, v_ranges[1] - v_ranges[0]):
                if not colored_pixels[j][cog_hps[0][0] + slant_shift]:
                    return i + v_ranges[0] + window_bar_height, j + v_ranges[0] + window_bar_height, cog_hps
            return i + v_ranges[0] + window_bar_height, v_ranges[1] + window_bar_height, cog_hps
    return None


def crop_health_values(img):
    matrix = load_img(img)
    tup = find_separating_height2(matrix)
    if not tup:
        return None
    y_top, y_bottom, cog_hps = tup
    return [((u, v), img.crop((u + slant_shift, y_top + 1, v - slant_shift, y_bottom - 1))) for u, v in cog_hps]


def separate_into_columns(matrix, slash_expected_on_left):
    if len(matrix) >= 23 and len([row[-1] for row in matrix if row[-1]]) <= 3:
        matrix = [row[:-1] for row in matrix]
    matrix = [[False for i in matrix[0]]] + matrix + [[False for i in matrix[0]]]
    matrix = [[False] + u + [False] for u in matrix]
    h = len(matrix)
    w = len(matrix[0])
    transposed = [[row[i] for row in matrix] for i in range(w)]
    blank_columns = [x for x in range(len(transposed)) if len([u for u in transposed[x] if u]) <= 1]

    zones = []
    for i in range(1, len(blank_columns)):
        if blank_columns[i - 1] + 2 < blank_columns[i] or (
                blank_columns[i - 1] + 2 == blank_columns[i] and
                len([x for x in transposed[blank_columns[i] - 1] if x]) >= 5):
            zone_detected = transposed[blank_columns[i - 1]:blank_columns[i] + 1]
            current_min = 10000
            current_max = -1
            for j in zone_detected:
                for x in range(h):
                    if j[x]:
                        current_min = min(current_min, x - 1)
                        break
                for x in range(h - 1, 0, -1):
                    if j[x]:
                        current_max = max(current_max, x + 1)
                        break
            if (current_max - current_min + 2 > blank_columns[i] - blank_columns[i - 1]) or len(zone_detected) < 6:
                zones.append([[row[i] for row in zone_detected] for i in range(current_min, current_max + 1)])
            else:
                bci = blank_columns[i]
                bci1 = blank_columns[i - 1]
                lens = [(better_len([s for s, u in enumerate(v) if u], h / 2, 2.1), k) for k, v in
                        enumerate(zone_detected)]
                _, delta = min([(v, k) for v, k in lens[2:-2]])
                zones.append([[row[i] for row in transposed[bci1:bci1 + delta]] + [False] for i in
                              range(current_min, current_max + 1)])
                zones.append([[False] + [row[i] for row in transposed[bci1 + delta:bci + 1]] for i in
                              range(current_min, current_max + 1)])

    if slash_expected_on_left:
        full_count = len([x for y in zones[0] for x in y if x])
        if full_count <= 1.4 * len(zones[0]) and len(zones[0][0]) * 2 < len(zones[0]) < len(zones[0][0]) * 3.5:
            zones = zones[1:]
    return zones


def detect_number_single(matrix, debug=False):
    if len([x for y in matrix for x in y if x]) <= 4:
        return ''
    if len(matrix) > 12:
        return detect_number_topologically(matrix, debug)
    if len(matrix[0]) <= 4:
        return '1'
    return detect_number_by_similarity([x[1:-1] for x in matrix[1:-1]], debug)


def detect_number(matrix, sel, debug=False):
    possible_zones = separate_into_columns(matrix, sel)
    current_string = ''.join([detect_number_single(z, debug) for z in possible_zones])
    try:
        return int(current_string)
    except ValueError:
        return 0


def separate_image_into_health_values(img, debug=False):
    x = crop_health_values(img)
    if not x:
        return None
    crops = []
    for i, crop in x:
        w = i[1] - i[0] - slant_shift * 2
        crop_matrix = [[0 if is_bright_dark_gray(u) else 1 for u in v] for v in load_img(crop)]
        left_matrix = [x[:w // 2 - 1] for x in crop_matrix]
        right_matrix = [x[w // 2 + 3:] for x in crop_matrix]
        crops.append((detect_number(left_matrix, False, debug), detect_number(right_matrix, True, debug)))
    return crops


def sanctify_health_values(img, debug=False):
    hv = separate_image_into_health_values(img)
    if not hv:
        return False
    popular_values = [42, 56, 72, 90, 110, 132, 156, 182, 210, 240, 272, 306, 342, 380, 420,
                      63, 84, 108, 135, 165, 198, 234, 273, 315, 360, 408, 459, 513, 570, 630]
    ans = []
    for x in hv:
        if x[0] == x[1]:
            ans.append(x)
        elif x[1] in popular_values and x[0] > x[1]:
            ans.append((x[1], x[1]))
        elif x[0] in popular_values:
            ans.append((x[0], x[0]))
        elif x[1] > 630:
            ans.append((x[0], x[0]))
        elif x[0] > 630:
            ans.append((x[1], x[1]))
        elif x[0] > x[1]:
            ans.append((x[1], x[1]))
        else:
            ans.append(x)
    return ans
