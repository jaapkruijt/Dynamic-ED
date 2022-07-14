from mention_patterns import INNER_NAMES, FAMOUS, FRIENDS_NAMES, categorize_acquaintances, map_entities, find_patterns, \
    format_gold
from data_preprocessing import read_input, prepare_data

import json, re


def get_clusters(filename, predicted_clusters=False):
    # based on boberle-corefconversion
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
            scene_counter += 1
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
                scene = line[0] + '_' + str(scene_counter)
                clusters[scene][chain_index].append(ent)
                scene_already_mentioned.append(ent)

    return clusters


def compare_clusters(gold, sys):
    errors = {}
    for scene, clusters in gold.items():
        scene_errors = {}
        for cluster in clusters:
            if len(cluster) <= 2:
                ref = 'noref'
            else:
                ref = 'coref'
            entity = cluster[-1]
            found = False
            for mention in cluster:
                for system_cluster in sys[scene]:
                    if mention in system_cluster:
                        true_pos = [sys_men for sys_men in system_cluster if sys_men in cluster]
                        false_pos = [sys_men for sys_men in system_cluster if sys_men not in cluster]
                        false_neg = [mention for mention in cluster[:-1] if mention not in system_cluster]
                        scene_errors[entity] = {'ref': ref, 'true positive': true_pos, 'false positive': false_pos,
                                                'false negative': false_neg, 'support': len(cluster[:-1])}
                        found = True
            if not found:
                scene_errors[entity] = {'ref': ref, 'true positive': [], 'false positive': [],
                                        'false negative': cluster[:-1], 'support': len(cluster[:-1])}

        errors[scene] = scene_errors

    return errors


def categorize_errors(error_dict, inner_ents):
    errors_categorised = {'inner': {'noref': {'tp': 0, 'fp': 0, 'fn': 0, 'support': 0},
                                    'coref': {'tp': 0, 'fp': 0, 'fn': 0, 'support': 0}},
                          'outer': {'noref': {'tp': 0, 'fp': 0, 'fn': 0, 'support': 0},
                                    'coref': {'tp': 0, 'fp': 0, 'fn': 0, 'support': 0}}}
    # inner_tp, outer_tp, inner_fp, inner_fn, outer_fp, outer_fn = 0, 0, 0, 0, 0, 0
    for errors in error_dict.values():
        for entity, mistakes in errors.items():
            if entity in inner_ents:
                cat = 'inner'
            else:
                cat = 'outer'
            errors_categorised[cat][mistakes['ref']]['tp'] += len(mistakes['true positive'])
            print(f"{cat} {entity} has {len(mistakes['true positive'])} true positives ({mistakes['ref']})")
            errors_categorised[cat][mistakes['ref']]['fp'] += len(mistakes['false positive'])
            print(f"{cat} {entity} has {len(mistakes['false positive'])} false positives ({mistakes['ref']})")
            errors_categorised[cat][mistakes['ref']]['fn'] += len(mistakes['false negative'])
            print(f"{cat} {entity} has {len(mistakes['false negative'])} false negatives ({mistakes['ref']})")
            errors_categorised[cat][mistakes['ref']]['support'] += mistakes['support']

    return errors_categorised


def calculate_precision_recall_f1(errors):
    score_categorised = {}

    for circle, refs in errors.items():
        score_categorised[circle] = {}
        for ref, scores in refs.items():
            try:
                precision = scores['tp'] / (scores['fp'] + scores['tp'])
            except ZeroDivisionError:
                precision = 0
            try:
                recall = scores['tp'] / (scores['fn'] + scores['tp'])
            except ZeroDivisionError:
                recall = 0
            try:
                f1 = 2 * precision * recall / (precision + recall)
            except ZeroDivisionError:
                f1 = 0
            score_categorised[circle][ref] = {'precision': precision * 100, 'recall': recall * 100, 'f1': f1 * 100,
                                              'support': scores['support']}

    return score_categorised


if __name__ == "__main__":
    gold_clusters = get_clusters('224_all_gold.english.128.jsonlines')
    gold_clusters = add_entity_id(gold_clusters, 'all/test/224_all_gold.english.conll.txt')

    # support = 0
    # for sc, clusters in gold_clusters.items():
    #     for clus in clusters:
    #         support += len(clus[:-1])
    #
    # print(support)

    sys_clusters = get_clusters('224_small.jsonlines', predicted_clusters=True)

    # for gold_cluster in gold_clusters:
    #     print(gold_cluster, gold_clusters[gold_cluster])
    #     print(gold_cluster, sys_clusters[gold_cluster])

    err = compare_clusters(gold_clusters, sys_clusters)

    # print("ERRORS")
    # for scene, scene_err in err.items():
    #     print(scene, scene_err)

    gold_data = prepare_data('friends.all.scene_delim.conll.txt')
    gold_formatted = format_gold(gold_data)
    entmap = map_entities('friends_entity_map.txt')

    mention_patterns = find_patterns(gold_data, entmap)

    six_friends, famous_people, inner_circle, outer_circle = categorize_acquaintances(entmap, mention_patterns)
    inner = six_friends + famous_people + inner_circle

    categorisation = categorize_errors(err, inner)

    print(f"Inner circle, noref: true positives: {categorisation['inner']['noref']['tp']}, "
          f"false positives: {categorisation['inner']['noref']['fp']}, "
          f"false negatives: {categorisation['inner']['noref']['fn']}\n"
          f"Inner circle, coref: true positives: {categorisation['inner']['coref']['tp']}, "
          f"false positives: {categorisation['inner']['coref']['fp']}, "
          f"false negatives: {categorisation['inner']['coref']['fn']}\n"
          f"Outer circle, noref: true positives: {categorisation['outer']['noref']['tp']}, "
          f"false positives: {categorisation['outer']['noref']['fp']}, "
          f"false negatives: {categorisation['outer']['noref']['fn']}\n"
          f"Outer circle, coref: true positives: {categorisation['outer']['coref']['tp']}, "
          f"false positives: {categorisation['outer']['coref']['fp']}, "
          f"false negatives: {categorisation['outer']['coref']['fn']}")
    print()

    score = calculate_precision_recall_f1(categorisation)
    print(f"Inner circle, noref: precision: {score['inner']['noref']['precision']}, "
          f"recall: {score['inner']['noref']['recall']}, "
          f"f1: {score['inner']['noref']['f1']}, "
          f"support: {score['inner']['noref']['support']}\n"
          f"Inner circle, coref: precision: {score['inner']['coref']['precision']}, "
          f"recall: {score['inner']['coref']['recall']}, "
          f"f1: {score['inner']['coref']['f1']},"
          f"support: {score['inner']['coref']['support']}\n"
          f"Outer circle, noref: precision: {score['outer']['noref']['precision']}, "
          f"recall: {score['outer']['noref']['recall']}, "
          f"f1: {score['outer']['noref']['f1']},"
          f"support: {score['outer']['noref']['support']}\n"
          f"Outer circle, coref: precision: {score['outer']['coref']['precision']}, "
          f"recall: {score['outer']['coref']['recall']}, "
          f"f1: {score['outer']['coref']['f1']},"
          f"support: {score['outer']['coref']['support']}")
