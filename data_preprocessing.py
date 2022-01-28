
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


def prepare_data(filename, timestamps=True):
    raw_data = read_input(filename)
    clean_data = clean_lines(raw_data)
    if timestamps:
        clean_data = prepare_timestamps(clean_data)

    return clean_data


if __name__ == "__main__":
    file = "semeval-2018-task4/dat/friends.test.episode_delim.conll.txt"  # TODO change file path

    working_data = prepare_data(file)

    print(working_data)