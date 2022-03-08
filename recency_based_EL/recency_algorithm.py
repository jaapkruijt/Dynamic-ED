from data_preprocessing import prepare_data
from perfect_history_baseline.categorize_mentions import fst_snd_prons
import math
import operator


def create_utterance_history(data, index):
    history_from_start = data[:index]
    current = data[index]
    scene_history = []
    scene_timestamps = []
    for token in history_from_start[::-1]:
        if token[1] != current[1]:
            break
        else:
            scene_history.append(token)
            scene_timestamps.append(token[0])
    return scene_history, scene_timestamps


def create_candidate_list(memory):
    candidates = set()
    for timestamp, pair in memory.items():
        mention = pair[0]
        candidates.add(mention)
    candidates = list(candidates)
    return candidates


def rank_by_recency(scene_timestamps, candidates, memory, current_label, ignored_pronouns=fst_snd_prons, alpha=4,
                    label_specific=False):
    """
    :param scene_timestamps: List. All timestamps for the current scene from current timestamp to beginning
    :param candidates: List. All entity cluster identifiers known at to this point
    :param memory: Dict. timestamp:(mention, label)
    :param current_label: String. Label used in the current mention
    :param ignored_pronouns: List. Contains the labels which will be ignored by the ranker
    :param alpha: Int. Parameterizable value to simulate rate of forgetting
    :param label_specific: Bool. Whether the ranker will compute recency based on the label or not
    :return: Mention candidate list ranked by recency
    """

    memory_scene = []
    for timestamp in scene_timestamps:
        if timestamp in memory.keys():
            memory_scene.append(memory[timestamp])

    recency_scores = {}
    for entity in candidates:
        recency_score = 0
        # distance = 1
        for index, (mention, label) in enumerate(memory_scene):
            if label in ignored_pronouns:
                # distance += 1
                pass
            elif label_specific:
                # distance += 1
                if label == current_label:
                    if mention == entity:
                        distance = index + 1  # is distance only counted in mentions?
                        recency_score += (1 / distance) ** alpha
            elif not label_specific:
                # distance += 1
                if mention == entity:
                    distance = index+1
                    recency_score += (1 / distance) ** alpha
        recency_scores[entity] = recency_score

    recency_ranking = {entity: score for entity, score in sorted(recency_scores.items(), key=lambda item: item[1],
                                                                 reverse=True)}

    return recency_ranking


def combine_rankings(ranking_1, ranking_2):
    candidates = ranking_1.keys()
    combined_scores = {}
    for candidate in candidates:
        score = ranking_1[candidate]+ranking_2[candidate]
        combined_scores[candidate] = score

    combined_ranking = {entity: score for entity, score in sorted(combined_scores.items(), key=lambda item: item[1],
                                                                  reverse=True)}

    return combined_ranking


def normalise_scores(ranking):
    # from https://stackoverflow.com/questions/16417916/normalizing-dictionary-values
    factor = 1.0/math.fsum(ranking.values())
    for k in ranking:
        ranking[k] = ranking[k]*factor
    key_for_max = max(ranking.items(), key=operator.itemgetter(1))[0]
    diff = 1.0 - math.fsum(ranking.values())
    ranking[key_for_max] += diff


if __name__ == "__main__":
    # test some functions
    score_test = {'1': 0.56, '2': 1.45, '3': 0.2, '4': 1.6, '5': 0, '6': 1}
    score_ranked = {entity: score for entity, score in sorted(score_test.items(), key=lambda item: item[1],
                                                              reverse=True)}
    normalise_scores(score_ranked)
    print(score_ranked)
    print(math.fsum(score_ranked.values()))
    print(2/len(score_test))
    highest_candidate = next(iter(score_ranked))
    high_score = score_ranked[highest_candidate]
    print(highest_candidate, high_score)

    memory_test = {'01023': ('1', 'Mark'), '020312': ('1', 'he'), '0304021': ('2', 'Juliet')}
    test_candidates = create_candidate_list(memory_test)
    print(test_candidates)




