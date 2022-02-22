
def read_input(filename):
    lines = []

    with open(filename, 'r') as conllfile:
        for line in conllfile:
            columns = line.split()
            lines.append(columns)

    return lines


def clean_lines(raw_lines):
    lines_clean = []
    for line in raw_lines:
        if not line:
            continue
        elif not line[0].startswith('/friends'):
            continue
        else:
            lines_clean.append(line)

    return lines_clean


def prepare_timestamps(cleanlines):
    running_order = 0

    for index in range(0, len(cleanlines)):
        season = cleanlines[index][0][11]
        episode = cleanlines[index][0][-2:]
        cleanlines[index][0] = season+"_"+episode
        if cleanlines[index-1][1] != cleanlines[index][1]:
            running_order = 0
        else:
            running_order += 1
        cleanlines[index][2] = running_order

    return cleanlines


def prepare_timestamps_alt(cleanlines):
    running_order = 0

    for index in range(0, len(cleanlines)):
        season = cleanlines[index][0][11]
        episode = cleanlines[index][0][-2:]
        scene = cleanlines[index][1]
        if cleanlines[index-1][1] != scene:
            running_order = 0
        else:
            running_order += 1
        cleanlines[index][0] = season+"_"+episode+"_"+scene+"_"+str(running_order)

    return cleanlines


def prepare_data(filename, alt=True):
    raw_data = read_input(filename)
    clean_data = clean_lines(raw_data)
    if alt:
        clean_data = prepare_timestamps_alt(clean_data)
    else:
        clean_data = prepare_timestamps(clean_data)

    return clean_data


if __name__ == "__main__":
    file = "recency_based_EL/friends_s01_e03_sc0_test.txt"

    working_data = prepare_data(file)

    for line in working_data:
        print(line)