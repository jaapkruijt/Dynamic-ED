from data_preprocessing import prepare_data

import re


def get_mention_indices(data):
    bridge_start_index = []
    bridge_end_index = []
    single = []

    for index, line in enumerate(data):
        if line[-1] == '-':
            continue
        elif not line[-1].endswith(')'):
            bridge_start_index.append(index)
        elif not line[-1].startswith('('):
            bridge_end_index.append(index)
        else:
            single.append(index)

    ordered_mentions_indices = sorted(bridge_start_index + single)

    return bridge_start_index, bridge_end_index, ordered_mentions_indices


def get_ordered_entities_from_data(mention_indices):
    entities_from_text = []
    for index in mention_indices:
        ent = working_data[index][-1]
        ent = re.sub(r'[^0-9]', '', ent)
        entities_from_text.append(ent)

    return entities_from_text

def check_data_against_gold(ordered_mentions, gold_mention_file):
    with open(gold_mention_file) as outfile:
        correct_entities = outfile.read().splitlines()

    return ordered_mentions == correct_entities


def get_ordered_references(data, mention_indices, bridging_start_indices, bridging_end_indices):
    references = []

    for index in mention_indices:
        if index in bridging_start_indices:
            position = bridging_start_indices.index(index)
            end = bridging_end_indices[position]
            current_ref = []
            for pos in range(index, end + 1):
                ref_part = data[pos][3]
                current_ref.append(ref_part)
            ref = ' '.join(current_ref)
        else:
            ref = data[index][3]
        references.append(ref)

    return references


def create_name_lookup_dictionary(entity_map_file):
    entity_dictionary = {}
    with open(entity_map_file) as entity_map:
        for line in entity_map:
            nameslist = line.split()
            name = '_'.join(nameslist[1:])
            entity = nameslist[0]
            entity_dictionary[entity] = name
    return entity_dictionary


def create_ordered_mention_data(data, mention_indices, combined_references_and_mentions, entity_map):
    ordered_mention_data = []
    timestamps = []

    for mention_id in mention_indices:
        se_ep = data[mention_id][0]
        scene = data[mention_id][1]
        ts = data[mention_id][2]
        timestamp = f'{se_ep}_{scene}_{ts}'
        timestamps.append(timestamp)
        position = mention_indices.index(mention_id)
        entity = combined_references_and_mentions[position][0]
        reference = combined_references_and_mentions[position][1]
        name = entity_map[entity]
        mention_dict = {'timestamp': timestamp, 'entity': entity, 'reference': reference, 'name': name}
        ordered_mention_data.append(mention_dict)

    return ordered_mention_data, timestamps


def create_all_mention_data(data, gold_mention_file, entity_map_file):
    bridge_start, bridge_end, mention_indices = get_mention_indices(data)

    ordered_mentions = get_ordered_entities_from_data(mention_indices)

    if not check_data_against_gold(ordered_mentions, gold_mention_file):
        return "Incorrect extraction of mentions from data"

    ordered_references = get_ordered_references(data, mention_indices, bridge_start, bridge_end)

    combined_references_and_mentions = list(zip(ordered_mentions, ordered_references))

    entity_dictionary = create_name_lookup_dictionary(entity_map_file)

    ordered_mention_data, timestamps = create_ordered_mention_data(data, mention_indices,
                                                                   combined_references_and_mentions, entity_dictionary)

    return ordered_mentions, ordered_references, combined_references_and_mentions, ordered_mention_data, timestamps


if __name__ == "__main__":
    # TODO change file paths
    file = "semeval-2018-task4/dat/friends.test.episode_delim.conll.txt"
    gold = 'semeval-2018-task4/dat/ref.out.txt'
    entity_map = 'semeval-2018-task4/dat/friends_entity_map.txt'

    working_data = prepare_data(file)

    ments_ordered, references, ent_with_ref, all_mentions, all_timestamps = create_all_mention_data(working_data,
                                                                                                    gold, entity_map)

