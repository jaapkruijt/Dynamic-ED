from recency_algorithm import create_utterance_history, create_candidate_list, \
    rank_by_recency, combine_rankings, normalise_scores
from data_preprocessing import prepare_data, format_gold, write_to_conll
from perfect_history_baseline.categorize_mentions import names, fst_snd_prons
# Read in the data


def predict_clusters(data, proper_nouns, ignored_labels=fst_snd_prons):
    # TODO make mention and label terminology clear
    # TODO MESSY

    new_cluster_id = 1
    memory = {}
    bridging_labels = {}
    unique_labels = {}
    output = {}

    for index, line in enumerate(data):
        # check if the line contains tokens
        if not line:
            continue
        elif line[0] == '#begin' or line[0] == '#end':
            continue
        else:
            current_timestamp = line[0]

            # find the mention label
            if line[-1] == '(-1)':
                label = line[3]
                label_timestamps = [current_timestamp]
                label_list = [label]
            elif line[-1] == '(-1':
                label_part = line[3]
                bridging_labels[current_timestamp] = label_part
                continue
            elif line[-1] == '-1)':
                label_part = line[3]
                bridging_labels[current_timestamp] = label_part
                label = ' '.join(bridging_labels.values())
                label_timestamps = []
                for ts in bridging_labels.keys():
                    label_timestamps.append(ts)
                label_list = []
                for lab in bridging_labels.values():
                    label_list.append(lab)
                bridging_labels.clear()
            elif line[-1] == '-':
                if bridging_labels:
                    mention_part = line[3]
                    bridging_labels[current_timestamp] = mention_part
                    continue
                else:
                    continue

            # skip if label is 1st or 2nd person pronoun
            if label in ignored_labels:
                continue

            # exact label matching if label is a proper noun
            elif line[4] == 'NNP' or line[4] == 'NNPS':  # pos annotation is not perfect but so is SpaCy
                if label in unique_labels.keys():
                    cluster_id = unique_labels[label]
                    for i, ts in enumerate(label_timestamps):
                        output[ts] = (cluster_id, label_list[i])
                else:
                    cluster_id = str(new_cluster_id)
                    for i, ts in enumerate(label_timestamps):
                        output[ts] = (cluster_id, label_list[i])
                    unique_labels[label] = cluster_id
                    new_cluster_id += 1
                memory[current_timestamp] = (cluster_id, label)

            # for all other labels we use the recency algorithm
            else:
                scene_history, timestamps = create_utterance_history(data, index)
                candidate_list = create_candidate_list(memory)
                label_agnostic_ranking = rank_by_recency(timestamps, candidate_list, memory, label)
                label_specific_ranking = rank_by_recency(timestamps, candidate_list, memory, label, label_specific=True)
                combined_ranking = combine_rankings(label_agnostic_ranking, label_specific_ranking)

                final_ranking = combined_ranking  # TODO make parameterizable
                if all(score == 0 for score in final_ranking.values()):
                    print(f"{current_timestamp} is all zero with {label}")
                    cluster_id = str(new_cluster_id)
                    for i, ts in enumerate(label_timestamps):
                        output[ts] = (cluster_id, label_list[i])
                    new_cluster_id += 1
                else:
                    normalise_scores(final_ranking)

                    # TODO define better threshold
                    highest_candidate = next(iter(final_ranking))
                    high_score = final_ranking[highest_candidate]
                    if high_score > 0.5:
                        cluster_id = highest_candidate
                        for i, ts in enumerate(label_timestamps):
                            output[ts] = (cluster_id, label_list[i])
                    else:
                        cluster_id = str(new_cluster_id)
                        for i, ts in enumerate(label_timestamps):
                            output[ts] = (cluster_id, label_list[i])
                        new_cluster_id += 1
                memory[current_timestamp] = (cluster_id, label)

    return output, memory, unique_labels


def format_output(data, system_output, ignored_labels=fst_snd_prons):
    for line in data:
        if not line:
            continue
        elif line[0] == '#begin' or line[0] == '#end':
            continue
        elif line[-1] == '-':
            continue
        elif line[3] in ignored_labels:
            # placeholder = '0'
            # new_mention = line[-1].replace('-1', placeholder)
            # line[-1] = new_mention
            line[-1] = '-'
        else:
            timestamp = line[0]
            system_id = system_output[timestamp][0]
            empty_mention = line[-1]
            new_mention = empty_mention.replace('-1', system_id)
            line[-1] = new_mention

    return data


if __name__ == "__main__":
    tests = [
        {'filename': 'friends.test.s01e04sc0.nokey.conll.txt', 'outname': 'test.1_04.sys.out'},
        {'filename': 'friends.test.s01e12sc01.nokey.conll.txt', 'outname': 'test.1_12.sys.out'},
        {'filename': 'friends.test.s01e23sc03.nokey.conll.txt', 'outname': 'test.1_23.sys.out'},
        {'filename': 'friends.test.s02e01sc0.nokey.conll.txt', 'outname': 'test.2_01.sys.out'},
        {'filename': 'friends.test.s02e10sc0.nokey.conll.txt', 'outname': 'test.2_10.sys.out'},
        {'filename': 'friends.test.s02e20sc0.nokey.conll.txt', 'outname': 'test.2_20.sys.out'}
    ]
    golds = [
        {'filename': 'friends.test.s01e04sc0.connl.txt', 'outname': 'test.1_04_0.gold'},
        {'filename': 'friends.test.s01e12sc01.conll.txt', 'outname': 'test.1_12_1.gold'},
        {'filename': 'friends.test.s01e23sc03.conll.txt', 'outname': 'test.1_23_3.gold'},
        {'filename': 'friends.test.s02e01sc0.conll.txt', 'outname': 'test.2_01_0.gold'},
        {'filename': 'friends.test.s02e10sc0.conll.txt', 'outname': 'test.2_10_0.gold'},
        {'filename': 'friends.test.s02e20sc0.conll.txt', 'outname': 'test.2_20_0.gold'}
    ]
    for test in tests[5:]:
        working_data = prepare_data(test['filename'])
        out, mem, labels = predict_clusters(working_data, names)
        output_data = format_output(working_data, out)
        write_to_conll(output_data, test['outname'])

    for gold in golds[5:]:
        data = prepare_data(gold['filename'])
        g_data = format_gold(data)
        write_to_conll(g_data, gold['outname'])



