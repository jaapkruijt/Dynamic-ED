from recency_algorithm import create_utterance_history, create_candidate_list, \
    rank_by_recency, combine_rankings, normalise_scores
from data_preprocessing import prepare_data
from perfect_history_baseline.categorize_mentions import names, fst_snd_prons
# Read in the data


def predict_clusters(data, proper_nouns, ignored_labels=fst_snd_prons):
    # TODO make mention and label terminology clear

    new_cluster_id = 1
    memory = {}
    bridging_labels = []
    unique_labels = {}
    clusters = {}

    for index, line in enumerate(data):
        current_timestamp = line[0]

        if line[-1] == '(-1)':
            label = line[3]
        elif line[-1] == '(-1':
            label_part = line[3]
            bridging_labels.append(label_part)
            continue
        elif line[-1] == '-1)':
            label = ' '.join(bridging_labels)
            bridging_labels.clear()
        elif line[-1] == '-':
            if bridging_labels:
                mention_part = line[3]
                bridging_labels.append(mention_part)
                continue
            else:
                continue

        if label in ignored_labels:
            continue

        elif line[4] == 'NNP' or line[4] == 'NNPS':  # pos annotation is not perfect but so is SpaCy
            if label in unique_labels.keys():
                cluster_id = unique_labels[label]
                clusters[cluster_id].append(current_timestamp)
            else:
                cluster_id = str(new_cluster_id)
                clusters[cluster_id] = [current_timestamp]
                unique_labels[label] = cluster_id
                new_cluster_id += 1
            line[-1] = f'({cluster_id})'  # TODO is this how I should do it?
            memory[current_timestamp] = (cluster_id, label)

        else:
            scene_history, timestamps = create_utterance_history(data, index)
            candidate_list = create_candidate_list(memory)
            label_agnostic_ranking = rank_by_recency(timestamps, candidate_list, memory, label)
            label_specific_ranking = rank_by_recency(timestamps, candidate_list, memory, label, label_specific=True)
            combined_ranking = combine_rankings(label_agnostic_ranking, label_specific_ranking)

            final_ranking = combined_ranking  # make parameterizable
            normalise_scores(final_ranking)

            # TODO define better threshold
            highest_candidate = next(iter(final_ranking))
            high_score = final_ranking[highest_candidate]
            if high_score > 0.5:
                cluster_id = highest_candidate
                clusters[cluster_id].append(current_timestamp)
            else:
                cluster_id = str(new_cluster_id)
                clusters[cluster_id] = [current_timestamp]
                new_cluster_id += 1
            line[-1] = f'({cluster_id})'
            memory[current_timestamp] = (cluster_id, label)

    return clusters, memory, unique_labels


if __name__ == "__main__":
    file = "friends_s01_e03_sc0_test.txt"

    working_data = prepare_data(file)

    clusters, memory, labels = predict_clusters(working_data, names)
    print(clusters)
    print(memory)
    # print(labels)



