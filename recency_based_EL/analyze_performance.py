from mention_patterns import INNER_NAMES, FAMOUS, FRIENDS_NAMES, categorize_acquaintances, map_entities, find_patterns,\
    format_gold
from data_preprocessing import read_input, prepare_data

import json, re


def get_clusters(filename, predicted_clusters=False):
    scene_clusters = {}

    with open(filename) as jsonfile:
        for line in jsonfile:
            data = json.loads(line)

            doc_key = data["doc_key"]
            clusters = data["clusters" if not predicted_clusters else "predicted_clusters"]

            if predicted_clusters:
                lookup = [gold for gold_chain in data['clusters'] for gold in gold_chain]
                new_chains = []
                for chain in clusters:
                    new_chain = []
                    for mention in chain:
                        if mention in lookup:
                            new_chain.append(mention)
                    if new_chain:
                        new_chains.append(new_chain)
                scene_clusters[doc_key] = new_chains

            else:
                scene_clusters[doc_key] = clusters

    return scene_clusters


def add_entity_id(clusters, conll_file):
    gold_data = read_input(conll_file)
    scene_counter = 0
    scene_already_mentioned = []

    for line in gold_data:
        if not line:
            continue
        elif line[0] == '#begin':
            continue
        elif line[0] == '#end':
            scene_counter+=1
            scene_already_mentioned.clear()
            continue
        elif line[-1] == '-':
            continue
        else:
            mention = line[-1]
            ent = re.sub(r'[^0-9]', '', mention)
            if ent in scene_already_mentioned:
                continue
            else:
                chain_index = len(scene_already_mentioned)
                scene = line[0]+'_'+str(scene_counter)
                clusters[scene][chain_index].append(ent)
                scene_already_mentioned.append(ent)

    return clusters


def compare_clusters(gold, sys):
    errors = {}
    for scene, clusters in gold.items():
        scene_errors = {}
        for cluster in clusters:
            entity = cluster[-1]
            found = False
            for mention in cluster:
                for system_cluster in sys[scene]:
                    if mention in system_cluster:
                        false_pos = [sys_men for sys_men in system_cluster if sys_men not in cluster]
                        false_neg = [mention for mention in cluster[:-1] if mention not in system_cluster]
                        scene_errors[entity] = {'false positive': false_pos, 'false negative': false_neg}
                        found = True
            if not found:
                scene_errors[entity] = {'false positive': [], 'false negative': cluster[:-1]}

        errors[scene] = scene_errors

    return errors


def categorize_errors(error_dict, inner_ents):
    inner_fp, inner_fn, outer_fp, outer_fn = 0,0,0,0
    for errors in error_dict.values():
        for entity, mistakes in errors.items():
            if entity in inner_ents:
                inner_fp += len(mistakes['false positive'])
                print(f"Inner {entity} has {len(mistakes['false positive'])} false positives")
                inner_fn += len(mistakes['false negative'])
                print(f"Inner {entity} has {len(mistakes['false negative'])} false negatives")
            else:
                outer_fp += len(mistakes['false positive'])
                print(f"Outer {entity} has {len(mistakes['false positive'])} false positives")
                outer_fn += len(mistakes['false negative'])
                print(f"Outer {entity} has {len(mistakes['false negative'])} false negatives")

    return inner_fp, inner_fn, outer_fp, outer_fn


if __name__ == "__main__":
    gold_clusters = get_clusters('224_all_gold.english.128.jsonlines')
    gold_clusters = add_entity_id(gold_clusters, 'all/test/224_all_gold.english.conll.txt')

    sys_clusters = get_clusters('test.224_finetune.jsonlines', predicted_clusters=True)

    # for gold_cluster in gold_clusters:
    #     print(gold_cluster, gold_clusters[gold_cluster])
    #     print(gold_cluster, sys_clusters[gold_cluster])

    err = compare_clusters(gold_clusters, sys_clusters)

    print("ERRORS")
    for scene, scene_err in err.items():
        print(scene, scene_err)

    gold_data = prepare_data('friends.all.scene_delim.conll.txt')
    gold_formatted = format_gold(gold_data)
    entmap = map_entities('friends_entity_map.txt')

    mention_patterns = find_patterns(gold_data, entmap)

    six_friends, famous_people, inner_circle, outer_circle = categorize_acquaintances(entmap, mention_patterns)
    inner = six_friends+famous_people+inner_circle

    in_fp, in_fn, out_fp, out_fn = categorize_errors(err, inner)

    print(f"Inner circle false positives: {in_fp}, inner circle false negatives: {in_fn}\n"
          f"Outer circle false positives: {out_fp}, outer circle false negatives: {out_fn}")





