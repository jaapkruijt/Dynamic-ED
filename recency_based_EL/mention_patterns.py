from data_preprocessing import prepare_data, read_input, format_gold, write_to_conll

import spacy

import re

NAMES_PRONS = ['NNP', 'PRP', 'PRP$']

# based on family relation, and Wikidata query and selection using minimally 2 in-show triples, people that appear in
# the first two seasons
INNER_NAMES = ['Charles Bing',
               'Judy Geller', 'Jack Geller', 'Susan Bunch', 'Carol Willick', 'Ben',
               'Ursula', 'Richard Burke', 'Richard', 'Frank Buffay', 'Janice', 'Gunther', 'Gloria Tribbiani',
               'Joey Tribbiani Sr.', 'Leonard Green', 'Lily Buffay', 'Mr. Greene', 'Mrs. Green',
               'Mrs. Greene', 'Mrs. Tribbiani',
               'Mrs. Bing', 'Mrs. Geller', 'Mr. Tribbiani', "Phoebe's grandmother",
               "Rachel's sister", "Ross' grandmother", 'Sandra Green']

FRIENDS_NAMES = ['Ross Geller', 'Joey Tribbiani', 'Chandler Bing', 'Monica Geller', 'Phoebe Buffay', 'Rachel Green']

FAMOUS = ['Al Pacino', 'Albert Einstein', 'Bishop Tutu', 'Demi Moore', 'Drew Barrymore',
          'Hannibal Lecter', 'James Bond', 'Jay Leno', 'Jill Goodacre', 'Jim Crochee', 'Joseph Stalin', 'Judy Jetson',
          'Liam Neeson', 'Mother Theresa', 'Spike Lee', 'Uma Thurman', 'Van Damme', 'Warren Beatty']

INDEFINITES = ['a', 'A', 'an', 'An', 'some']

episodes = {
    '/friends-s01e01': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e02': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e03': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e04': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e05': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e06': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e07': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e08': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e09': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e10': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e11': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e12': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e13': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e14': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e15': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e16': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e17': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e18': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e19': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e20': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e21': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e22': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e23': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s01e24': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e01': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e02': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e03': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e04': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e05': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e06': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e07': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e08': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e09': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e10': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e11': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e12': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e13': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e14': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e15': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e16': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e17': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e18': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e19': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e20': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e21': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e22': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e23': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
    '/friends-s02e24': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}}}


def map_entities(entity_map_file):
    entity_map = {}

    with open(entity_map_file) as ent_map:
        for line in ent_map:
            info = line.split()
            identifier = info[0]
            name = ' '.join(info[1:])
            entity_map[identifier] = name

    return entity_map


def find_patterns(formatted_data, entity_map):
    patterns = {}
    bridging_labels = []
    nlp = spacy.load('en_core_web_sm')

    for name in entity_map.values():
        patterns[name] = []

    for index, line in enumerate(formatted_data):
        # check if the line contains tokens
        if not line:
            continue
        elif line[0] == '#begin' or line[0] == '#end':
            continue
        else:
            current_timestamp = line[0]

            # find the mention label
            if line[-1].startswith('(') and line[-1].endswith(')'):
                label = line[3]
                mention = line[-1]
                ent = re.sub(r'[^0-9]', '', mention)
                name = entity_map[ent]
                previous = []
                speaker = line[-3]
                if line[4] not in NAMES_PRONS:
                    # for prev in formatted_data[index-1:index-3:-1]:
                    #     try:
                    #         previous.append(prev[3])
                    #     except IndexError:
                    #         continue
                    try:
                        previous.append(formatted_data[index - 1][3])
                    except IndexError:
                        continue
                else:
                    previous = []
                previous = reversed(previous)
                previous = ' '.join(previous)
                patterns[name].append([current_timestamp, label, ent, speaker, previous])
            elif line[-1].startswith('('):
                label_part = line[3]
                bridging_labels.append(label_part)
                continue
            elif line[-1].endswith(')'):
                label_part = line[3]
                bridging_labels.append(label_part)
                label = ' '.join(bridging_labels)
                mention = line[-1]
                ent = re.sub(r'[^0-9]', '', mention)
                name = entity_map[ent]
                speaker = line[-3]
                patterns[name].append([current_timestamp, label, ent, speaker])
                bridging_labels.clear()
            elif line[-1] == '-':
                if bridging_labels:
                    mention_part = line[3]
                    bridging_labels.append(mention_part)
                    continue
                else:
                    continue

    for pattern in patterns.values():
        for mention in pattern:
            doc = nlp(mention[1])
            token = doc[-1]
            pos = token.tag_
            # if pos == 'NN':
            #     if mention[4] in INDEFINITES:
            #         pos = pos + '_in'
            #     else:
            #         pos = pos + '_def'
            mention.append(pos)

    for pattern in patterns.values():
        for index, mention in enumerate(pattern):
            if index == 0 or pattern[index - 1][0][:6] != mention[0][:6]:
                prev_pos = 'NULL'
                mention.append(prev_pos)
            else:
                prev_pos = pattern[index - 1][-2]
                mention.append(prev_pos)

    return patterns


def categorize_acquaintances(entity_map, pattern_map):
    friends = []
    famous = []
    inner = []
    outer = []

    for identifier, name in entity_map.items():
        if name in FRIENDS_NAMES:
            friends.append(identifier)
        elif name in FAMOUS:
            famous.append(identifier)
        elif name in INNER_NAMES:
            if len(pattern_map[name]) > 2:
                inner.append(identifier)
            else:
                outer.append(identifier)
        elif name in FAMOUS:
            inner.append(identifier)
        else:
            outer.append(identifier)

    return friends, famous, inner, outer


def ratio_inner_outer_per_episode(inner, friends, famous, dataset, entity_map):
    eps = episodes
    inner_friends = inner + friends + famous

    for line in dataset:
        if not line:
            continue
        elif line[0] == '#begin' or line[0] == '#end':
            continue
        elif line[-1].endswith(')'):
            mention = line[-1]
            ent = re.sub(r'[^0-9]', '', mention)
            name = entity_map[ent]
            episode = line[0]
            if ent in inner_friends:
                eps[episode]['inner']['amount'] += 1
                eps[episode]['inner']['participants'].add(name)
            else:
                eps[episode]['outer']['amount'] += 1
                eps[episode]['outer']['participants'].add(name)
        else:
            continue

    for ep_dict in eps.values():
        inner_num = ep_dict['inner']['amount']
        outer_num = ep_dict['outer']['amount']
        try:
            ratio = inner_num / outer_num
        except ZeroDivisionError:
            ratio = 0
        ep_dict['inner']['ratio'] = ratio

    return eps


def change_inner_data(filename, friends, inner):
    inner = friends + inner
    data = read_input(filename)
    for line in data:
        if not line:
            continue
        elif line[0] == '#begin' or line[0] == '#end':
            continue
        elif line[-1] == '-':
            continue
        else:
            mention = line[-1]
            ent = re.sub(r'[^0-9]', '', mention)
            if ent in inner:
                continue
            else:
                line[-1] = '-'

    return data


def change_famous_data(filename, famous):
    data = read_input(filename)
    for line in data:
        if not line:
            continue
        elif line[0] == '#begin' or line[0] == '#end':
            continue
        elif line[-1] == '-':
            continue
        else:
            mention = line[-1]
            ent = re.sub(r'[^0-9]', '', mention)
            if ent in famous:
                continue
            else:
                line[-1] = '-'

    return data


def change_outer_data(filename, outer):
    data = read_input(filename)
    for line in data:
        if not line:
            continue
        elif line[0] == '#begin' or line[0] == '#end':
            continue
        elif line[-1] == '-':
            continue
        else:
            mention = line[-1]
            ent = re.sub(r'[^0-9]', '', mention)
            if ent in outer:
                continue
            else:
                line[-1] = '-'

    return data


def make_nokey_files(filename_in, filename_out):
    data = read_input(filename_in)
    for line in data:
        if not line:
            continue
        elif line[0] == '#begin' or line[0] == '#end':
            continue
        elif line[-1] == '-':
            continue
        else:
            gold = line[-1]
            ent = re.sub(r'[^0-9]', '', gold)
            nokey = gold.replace(ent, '-1')
            line[-1] = nokey
    write_to_conll(data, filename_out)


def show_mention_patterns(gold, entities):
    mention_patterns = find_patterns(gold, entities)

    for entity in mention_patterns.keys():
        if mention_patterns[entity]:
            print(entity)
            print(mention_patterns[entity])


def write_all_data(gold, entities):
    mention_patterns = find_patterns(gold, entities)

    six_friends, famous_people, inner_circle, outer_circle = categorize_acquaintances(entmap, mention_patterns)

    file = '/Users/jaapkruijt/PycharmProjects/pythonProject/friends.ordered.scene_delim.conll.txt'
    inner_data = change_inner_data(file, six_friends, inner_circle)
    famous_data = change_famous_data(file, famous_people)
    outer_data = change_outer_data(file, outer_circle)

    write_to_conll(inner_data, 'inner.all')
    write_to_conll(famous_data, 'famous.all')
    write_to_conll(outer_data, 'outer.all')


def show_episode_ratios(gold, entities):
    mention_patterns = find_patterns(gold, entities)

    six_friends, famous_people, inner_circle, outer_circle = categorize_acquaintances(entmap, mention_patterns)

    raw_data = read_input('/Users/jaapkruijt/PycharmProjects/pythonProject/friends.ordered.scene_delim.conll.txt')
    episode_info = ratio_inner_outer_per_episode(inner_circle, six_friends, famous_people, raw_data, entmap)
    for episode, ep_info in episode_info.items():
        print(f'episode {episode}:')
        print(ep_info)


def process_gold_to_nokey():
    nokeys = [
        {'filename': 'all/test/all.test_109.gold.conll.txt', 'outname': 'all.test_109.nokey'},
        {'filename': 'all/test/all.test_119.gold.conll.txt', 'outname': 'all.test_119.nokey'},
        {'filename': 'all/test/all.test_214.gold.conll.txt', 'outname': 'all.test_214.nokey'},
        {'filename': 'all/test/all.test_224.gold.conll.txt', 'outname': 'all.test.224.nokey'},
        {'filename': 'famous/test/famous.test_109.gold.conll.txt', 'outname': 'famous.test_109.nokey'},
        {'filename': 'famous/test/famous.test_119.gold.conll.txt', 'outname': 'famous.test_119.nokey'},
        {'filename': 'famous/test/famous.test_214.gold.conll.txt', 'outname': 'famous.test_214.nokey'},
        {'filename': 'famous/test/famous.test_224.gold.conll.txt', 'outname': 'famous.test_224.nokey'},
        {'filename': 'inner_circle/test/inner.test_109.gold.conll.txt', 'outname': 'inner.test_109.nokey'},
        {'filename': 'inner_circle/test/inner.test_119.gold.conll.txt', 'outname': 'inner.test_119.nokey'},
        {'filename': 'inner_circle/test/inner.test_214.gold.conll.txt', 'outname': 'inner.test_214.nokey'},
        {'filename': 'inner_circle/test/inner.test_224.gold.conll.txt', 'outname': 'inner.test_224.nokey'},
        {'filename': 'outer_circle/test/outer.test_109.gold.conll.txt', 'outname': 'outer.test_109.nokey'},
        {'filename': 'outer_circle/test/outer.test_119.gold.conll.txt', 'outname': 'outer.test_119.nokey'},
        {'filename': 'outer_circle/test/outer.test_214.gold.conll.txt', 'outname': 'outer.test_214.nokey'},
        {'filename': 'outer_circle/test/outer.test_224.gold.conll.txt', 'outname': 'outer.test.224.nokey'}
    ]
    for nkey in nokeys:
        make_nokey_files(nkey['filename'], nkey['outname'])


def show_circles(gold, entities):
    mention_patterns = find_patterns(gold, entities)

    six_friends, famous_people, inner_circle, outer_circle = categorize_acquaintances(entmap, mention_patterns)

    print(f'friends: {six_friends}')
    print(f"inner: {inner_circle}")
    print(f'famous: {famous_people}')
    print(f'outer: {outer_circle}')
    print(len(inner_circle) + len(six_friends) + len(famous_people))
    print(len(outer_circle))

    return len(inner_circle + six_friends + famous_people), len(outer_circle)


def count_mention_pos(ment_patterns):
    pos_counts = {}
    for name, pattern in ment_patterns.items():
        pattern_pos = {}
        for mention in pattern:
            pos = mention[-2]
            if pos in pattern_pos:
                pattern_pos[pos] += 1
            else:
                pattern_pos[pos] = 1
        pos_counts[name] = pattern_pos

    return pos_counts


def avg_pos_per_circle(pos_counts):
    inner_pos = {'NNP': 0, 'NN': 0, 'PRP': 0, 'OTHER': 0}
    outer_pos = {'NNP': 0, 'NN': 0, 'PRP': 0, 'OTHER': 0}

    inner = INNER_NAMES + FRIENDS_NAMES + FAMOUS

    for entity in pos_counts:
        if entity in inner:
            for pos, count in pos_counts[entity].items():
                if 'NNP' in pos:
                    inner_pos['NNP'] += count
                elif 'NN' in pos:
                    inner_pos['NN'] += count
                elif 'PRP' in pos:
                    inner_pos['PRP'] += count
                else:
                    inner_pos['OTHER'] += count
        else:
            for pos, count in pos_counts[entity].items():
                if 'NNP' in pos:
                    outer_pos['NNP'] += count
                elif 'NN' in pos:
                    outer_pos['NN'] += count
                elif 'PRP' in pos:
                    outer_pos['PRP'] += count
                else:
                    outer_pos['OTHER'] += count

    # for pos, value in inner_pos.items():
    #     inner_pos[pos] = value/inner_amounts
    # for pos, value in outer_pos.items():
    #     outer_pos[pos] = value/outer_amounts

    return inner_pos, outer_pos


def calculate_reference_succession_patterns(mention_patterns):
    # format: circle_mention1_mention2
    inner_null_nn = 0
    inner_null_nnp = 0
    inner_null_prp = 0
    inner_nn_nn = 0
    inner_nn_nnp = 0
    inner_nn_prp = 0
    inner_nnp_nn = 0
    inner_nnp_nnp = 0
    inner_nnp_prp = 0
    inner_prp_nn = 0
    inner_prp_nnp = 0
    inner_prp_prp = 0
    outer_null_nn = 0
    outer_null_nnp = 0
    outer_null_prp = 0
    outer_nn_nn = 0
    outer_nn_nnp = 0
    outer_nn_prp = 0
    outer_nnp_nn = 0
    outer_nnp_nnp = 0
    outer_nnp_prp = 0
    outer_prp_nn = 0
    outer_prp_nnp = 0
    outer_prp_prp = 0

    inner_names = INNER_NAMES + FRIENDS_NAMES + FAMOUS

    for name, mention_pattern in mention_patterns.items():
        if name in inner_names:
            for index, mention in enumerate(mention_pattern):
                if 'NULL' in mention[-1]:
                    if 'NNP' in mention[-2]:
                        inner_null_nnp += 1
                    elif 'NN' in mention[-2]:
                        inner_null_nn += 1
                    elif 'PRP' in mention[-2]:
                        inner_null_prp += 1
                elif 'NNP' in mention[-1]:
                    if 'NNP' in mention[-2]:
                        inner_nnp_nnp += 1
                    elif 'NN' in mention[-2]:
                        inner_nnp_nn += 1
                    elif 'PRP' in mention[-2]:
                        inner_nnp_prp += 1
                elif 'NN' in mention[-1]:
                    if 'NNP' in mention[-2]:
                        inner_nn_nnp += 1
                    elif 'NN' in mention[-2]:
                        inner_nn_nn += 1
                    elif 'PRP' in mention[-2]:
                        inner_nn_prp += 1
                elif 'PRP' in mention[-1]:
                    if 'NNP' in mention[-2]:
                        inner_prp_nnp += 1
                    elif 'NN' in mention[-2]:
                        inner_prp_nn += 1
                    elif 'PRP' in mention[-2]:
                        inner_prp_prp += 1

        else:
            for index, mention in enumerate(mention_pattern):
                if 'NULL' in mention[-1]:
                    if 'NNP' in mention[-2]:
                        outer_null_nnp += 1
                    elif 'NN' in mention[-2]:
                        outer_null_nn += 1
                    elif 'PRP' in mention[-2]:
                        outer_null_prp += 1
                elif 'NNP' in mention[-1]:
                    if 'NNP' in mention[-2]:
                        outer_nnp_nnp += 1
                    elif 'NN' in mention[-2]:
                        outer_nnp_nn += 1
                    elif 'PRP' in mention[-2]:
                        outer_nnp_prp += 1
                elif 'NN' in mention[-1]:
                    if 'NNP' in mention[-2]:
                        outer_nn_nnp += 1
                    elif 'NN' in mention[-2]:
                        outer_nn_nn += 1
                    elif 'PRP' in mention[-2]:
                        outer_nn_prp += 1
                elif 'PRP' in mention[-1]:
                    if 'NNP' in mention[-2]:
                        outer_prp_nnp += 1
                    elif 'NN' in mention[-2]:
                        outer_prp_nn += 1
                    elif 'PRP' in mention[-2]:
                        outer_prp_prp += 1

    inner_null_total = inner_null_nnp + inner_null_nn + inner_null_prp
    inner_prp_total = inner_prp_nnp + inner_prp_nn + inner_prp_prp
    inner_nnp_total = inner_nnp_nnp + inner_nnp_nn + inner_nnp_prp
    inner_nn_total = inner_nn_nnp + inner_nn_nn + inner_nn_prp
    outer_null_total = outer_null_nnp + outer_null_nn + outer_null_prp
    outer_prp_total = outer_prp_nnp + outer_prp_nn + outer_prp_prp
    outer_nnp_total = outer_nnp_nnp + outer_nnp_nn + outer_nnp_prp
    outer_nn_total = outer_nn_nnp + outer_nn_nn + outer_nn_prp

    succession_dict = {'Inner': {'NULL': {'NNP': inner_null_nnp / inner_null_total * 100,
                                          'NN': inner_null_nn / inner_null_total * 100,
                                          'PRP': inner_null_prp / inner_null_total * 100},
                                 'NNP': {'NNP': inner_nnp_nnp / inner_nnp_total * 100,
                                         'NN': inner_nnp_nn / inner_nnp_total * 100,
                                         'PRP': inner_nnp_prp / inner_nnp_total * 100},
                                 'NN': {'NNP': inner_nn_nnp / inner_nn_total * 100,
                                        'NN': inner_nn_nn / inner_nn_total * 100,
                                        'PRP': inner_nn_prp / inner_nn_total * 100},
                                 'PRP': {'NNP': inner_prp_nnp / inner_prp_total * 100,
                                         'NN': inner_prp_nn / inner_prp_total * 100,
                                         'PRP': inner_prp_prp / inner_prp_total * 100}},
                       'Outer': {'NULL': {'NNP': outer_null_nnp / outer_null_total * 100,
                                          'NN': outer_null_nn / outer_null_total * 100,
                                          'PRP': outer_null_prp / outer_null_total * 100},
                                 'NNP': {'NNP': outer_nnp_nnp / outer_nnp_total * 100,
                                         'NN': outer_nnp_nn / outer_nnp_total * 100,
                                         'PRP': outer_nnp_prp / outer_nnp_total * 100},
                                 'NN': {'NNP': outer_nn_nnp / outer_nn_total * 100,
                                        'NN': outer_nn_nn / outer_nn_total * 100,
                                        'PRP': outer_nn_prp / outer_nn_total * 100},
                                 'PRP': {'NNP': outer_prp_nnp / outer_prp_total * 100,
                                         'NN': outer_prp_nn / outer_prp_total * 100,
                                         'PRP': outer_prp_prp / outer_prp_total * 100}}}

    return succession_dict


if __name__ == "__main__":
    gold_data = prepare_data('friends.all.scene_delim.conll.txt')
    gold_formatted = format_gold(gold_data)
    entmap = map_entities('friends_entity_map.txt')

    # show_mention_patterns(gold_formatted, entmap)

    # len_inner, len_outer = show_circles(gold_formatted, entmap)
    #
    # for entity in patt.keys():
    #     if patt[entity]:
    #         print(entity)
    #         print(patt[entity])

    patt = find_patterns(gold_formatted, entmap)
    # #
    counts = count_mention_pos(patt)
    # for ent in counts:
    #     print(ent)
    #     print(counts[ent])
    #
    in_pos, out_pos = avg_pos_per_circle(counts)
    print()
    print(in_pos)
    print(out_pos)
    print()
    #
    successions = calculate_reference_succession_patterns(patt)
    for circle, calculations in successions.items():
        print(circle)
        for succeeding, preceding in calculations.items():
            print(succeeding)
            print(preceding)

    # show_episode_ratios(gold_formatted, entmap)

    # print(len(INNER_NAMES)+len(FAMOUS)+len(FRIENDS_NAMES))

    # /friends-s01e19 and /friends-s02e24 could be good candidates (based on 1/1 ratio)
    # also /friends-s01e09 and /friends-s02e14 with a 4/1 ratio
