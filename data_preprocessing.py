from perfect_history_baseline.categorize_mentions import names, fst_snd_prons, prons, endearing, context_dep, errors


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


# TODO IMPORTANT remember to also make a function that works with the old baseline or change the baseline!
# See notebook for old function which changes index[2] to the running order
def prepare_timestamps(cleanlines):
    running_order = 0

    for index in range(0, len(cleanlines)):
        season = cleanlines[index][0][11]
        episode = cleanlines[index][0][-2:]
        scene = cleanlines[index][1]
        cleanlines[index][0] = season + "_" + episode + "_" + scene

    return cleanlines


def prepare_timestamps_alt(cleanlines):
    running_order = 0

    for index in range(0, len(cleanlines)):
        if not cleanlines[index]:
            continue
        elif cleanlines[index][0] == '#end':
            continue
        elif cleanlines[index][0] == '#begin':
            running_order = 0
            continue
        else:
            season = cleanlines[index][0][11]
            episode = cleanlines[index][0][-2:]
            scene = cleanlines[index][1]
            running_order += 1
            cleanlines[index][0] = season+"_"+episode+"_"+scene+"_"+str(running_order)

    return cleanlines


def change_scene_numbers(data):
    scene_number = '0'

    for line in data:
        if not line:
            continue
        elif line[0] == '#end':
            continue
        elif line[0] == '#begin':
            scene_number = line[-1][-2:]
            continue
        else:
            line[1] = scene_number

    return data


def format_gold(gold_data, ignored_labels=fst_snd_prons):
    for line in gold_data:
        if not line:
            continue
        elif line[0] == '#begin' or line[0] == '#end':
            continue
        elif line[3] in ignored_labels:
            line[-1] = '-'
        else:
            continue

    return gold_data


def write_to_conll(data, test_name):
    with open(f'{test_name}.conll.txt', 'x') as conll:
        for line in data:
            conll.write(' '.join(line)+"\n")


def create_dataset(file, test_name, ignored_labels=fst_snd_prons):
    dataset = read_input(file)
    dataset = change_scene_numbers(dataset)
    dataset = format_gold(dataset, ignored_labels)
    write_to_conll(dataset, test_name)


def prepare_data(filename, raw_lines=True):
    raw_data = read_input(filename)
    if raw_lines:
        data = prepare_timestamps_alt(raw_data)
    else:
        clean_data = clean_lines(raw_data)
        data = prepare_timestamps(clean_data)

    return data


def find_test_scenes(data):
    unique_scenes = {}
    for line in data:
        if line[-1] == '-':
            continue
        else:
            scene_info = line[0]
            unique_scenes[scene_info] = 0
    for line in data:
        if line[-1] == '-':
            continue
        else:
            scene_info = line[0]
            label = line[3]
            if label not in fst_snd_prons:
                unique_scenes[scene_info] += 1
    useful_scenes = {scene: 0 for scene, value in unique_scenes.items() if value != 0}
    useless_scenes = [scene for scene, value in unique_scenes.items() if value == 0]
    for line in data:
        scene_info = line[0]
        if unique_scenes[scene_info] == 0:
            continue
        else:
            label = line[3]
            if label in prons or label in context_dep:
                useful_scenes[scene_info] += 1

    return useful_scenes, unique_scenes, useless_scenes


if __name__ == "__main__":
    gold_data = prepare_data('recency_based_EL/all/finetune/all.dev_214.english.conll.txt')
    gold_formatted = format_gold(gold_data)

    print(len(gold_formatted))

    # file_in_name, file_out_name = ("recency_based_EL/friends.all.scene_delim.conll.txt", 'friends.ordered.scene_delim')
    #
    # # create_dataset(file_in_name, file_out_name)
    # data = read_input(file_in_name)
    # for line in data:
    #     print(line)

    # for token in working_data:
    #     print(token)

    # working_data = prepare_data(file)
    #
    # for token in working_data:
    #     print(token)

    # useful, unique, useless = find_test_scenes(working_data)
    # print(useful)
    # print(unique)
    # print(useless)

    # Potentiele test scenes: 1_04_0, 1_12_1, 1_23_3, 2_01_0, 2_10_0, 2_20_0
    # totale aantal relevante mentions (dus geen 1st of 2nd person pronoun) = 13+30+15+28+16+19 = 111 (grofweg)
