from data_preprocessing import prepare_data
from test_recency import format_gold

import re

NAMES_PRONS = ['NNP', 'PRP', 'PRP$']

# based on family relation, and Wikidata query and selection using minimally 2 in-show triples, people that appear in
# the first two seasons
INNER_NAMES = ['Charles Bing', 'Amy Green', 'Jill Green', 'Nora Tyler Bing', 'Elizabeth Stevens', 'Estelle Leonard',
               'Judy Geller', 'Jack Geller', 'Susan Bunch' 'Paul Stevens', 'Carol Willick', 'Ben Geller',
               'Ursula Buffay', 'Richard Burke', 'Frank Buffay', 'Janice', 'Gunther', 'Gloria Tribbiani',
               'Joey Tribbiani Sr.', "Joey's cousin", 'Leonard Green', 'Lily Buffay', 'Mr. Greene', 'Mrs. Green',
               'Mrs. Bing', 'Mrs. Buffay', 'Mrs. Geller', 'Mr. Tribbiani', "Phoebe's grandmother",
               "Phoebe's stepfather", "Rachel's sister", "Ross' grandmother", 'Sandra Green', ]

FRIENDS_NAMES = ['Ross Geller', 'Joey Tribbiani', 'Chandler Bing', 'Monica Geller', 'Phoebe Buffay', 'Rachel Green']

FAMOUS = ['David Hasselhoff', 'Al Pacino', 'Albert Einstein', 'Bishop Tutu', 'Demi Moore', 'Drew Barrymore',
          'Hannibal Lecter', 'James Bond', 'Jay Leno', 'Jill Goodacre', 'Jim Crochee', 'Joseph Stalin', 'Judy Jetson',
          'Liam Neeson', 'Mother Theresa', 'Spike Lee', 'Uma Thurman', 'Van Damme', 'Warren Beatty']


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
    inner = []
    outer = []

    for identifier, name in entity_map.items():
        if name in FRIENDS_NAMES:
            friends.append(identifier)
        elif name in INNER_NAMES:
            if len(pattern_map[name]) > 2:
                inner.append(identifier)
            else:
                outer.append(identifier)
        elif name in FAMOUS:
            inner.append(identifier)
        else:
            outer.append(identifier)

    return friends, inner, outer


if __name__ == "__main__":
    gold_data = prepare_data('friends.train.scene_delim.conll.txt')
    gold_formatted = format_gold(gold_data)
    entmap = map_entities('friends_entity_map.txt')
    mention_patterns = find_patterns(gold_formatted, entmap)
    # for entity in mention_patterns.keys():
    #     if mention_patterns[entity]:
    #         print(entity)
    #         print(mention_patterns[entity])
    six_friends, inner_circle, outer_circle = categorize_acquaintances(entmap, mention_patterns)
    print(inner_circle)
    print(outer_circle)
    print(six_friends)
