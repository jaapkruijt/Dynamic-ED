from data_preprocessing import prepare_data, read_input, format_gold, write_to_conll

import re

NAMES_PRONS = ['NNP', 'PRP', 'PRP$']

# based on family relation, and Wikidata query and selection using minimally 2 in-show triples, people that appear in
# the first two seasons
INNER_NAMES = ['Charles Bing', 'Amy Green', 'Jill Green', 'Nora Tyler Bing', 'Elizabeth Stevens', 'Estelle Leonard',
               'Judy Geller', 'Jack Geller', 'Susan Bunch', 'Paul Stevens', 'Carol Willick', 'Ben',
               'Ursula Buffay', 'Richard Burke', 'Richard', 'Frank Buffay', 'Janice', 'Gunther', 'Gloria Tribbiani',
               'Joey Tribbiani Sr.', "Joey's cousin", 'Leonard Green', 'Lily Buffay', 'Mr. Greene', 'Mrs. Green',
               'Mrs. Greene', 'Mrs. Tribbiani',
               'Mrs. Bing', 'Mrs. Buffay', 'Mrs. Geller', 'Mr. Tribbiani', "Phoebe's grandmother",
               "Phoebe's stepfather", "Rachel's sister", "Ross' grandmother", 'Sandra Green']

FRIENDS_NAMES = ['Ross Geller', 'Joey Tribbiani', 'Chandler Bing', 'Monica Geller', 'Phoebe Buffay', 'Rachel Green']

FAMOUS = ['Al Pacino', 'Albert Einstein', 'Bishop Tutu', 'Demi Moore', 'Drew Barrymore',
          'Hannibal Lecter', 'James Bond', 'Jay Leno', 'Jill Goodacre', 'Jim Crochee', 'Joseph Stalin', 'Judy Jetson',
          'Liam Neeson', 'Mother Theresa', 'Spike Lee', 'Uma Thurman', 'Van Damme', 'Warren Beatty']

episodes = {'/friends-s01e01': {'inner': {'amount': 0, 'participants': set()}, 'outer': {'amount': 0, 'participants': set()}},
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
                    for prev in formatted_data[index-1:index-3:-1]:
                        try:
                            previous.append(prev[3])
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
    inner_friends = inner+friends+famous

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
            ratio = inner_num/outer_num
        except ZeroDivisionError:
            ratio = 0
        ep_dict['inner']['ratio'] = ratio

    return eps


def change_inner_data(filename, friends, inner):
    inner = friends+inner
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


if __name__ == "__main__":
    gold_data = prepare_data('friends.train.scene_delim.conll.txt')
    gold_formatted = format_gold(gold_data)
    entmap = map_entities('friends_entity_map.txt')
    mention_patterns = find_patterns(gold_formatted, entmap)
    # for entity in mention_patterns.keys():
    #     if mention_patterns[entity]:
    #         print(entity)
    #         print(mention_patterns[entity])
    six_friends, famous_people, inner_circle, outer_circle = categorize_acquaintances(entmap, mention_patterns)

    file = '/Users/jaapkruijt/PycharmProjects/pythonProject/friends.ordered.scene_delim.conll.txt'
    inner_data = change_inner_data(file, six_friends, inner_circle)
    famous_data = change_famous_data(file, famous_people)
    outer_data = change_outer_data(file, outer_circle)

    write_to_conll(inner_data, 'inner.all')
    write_to_conll(famous_data, 'famous.all')
    write_to_conll(outer_data, 'outer.all')

    # raw_data = read_input('/Users/jaapkruijt/PycharmProjects/pythonProject/friends.ordered.scene_delim.conll.txt')
    # episode_info = ratio_inner_outer_per_episode(inner_circle, six_friends, famous_people, raw_data, entmap)
    # for episode, ep_info in episode_info.items():
    #     print(f'episode {episode}:')
    #     print(ep_info)

    # /friends-s01e19 and /friends-s02e24 could be good candidates (based on 1/1 ratio)
    # also /friends-s01e09 and /friends-s02e14 with a 4/1 ratio
