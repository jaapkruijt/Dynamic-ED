from data_preprocessing import prepare_data
from perfect_history_baseline.categorize_mentions import fst_snd_prons


def create_utterance_history(data, index):
    history_from_start = data[:index]
    current = history_from_start[index]
    scene_history = []
    for token in history_from_start[::-1]:
        if token[1] != current[1]:
            break
        else:
            scene_history.append(token)
    return scene_history


def create_candidate_list(memory):
    candidates = set()
    for entity, reference in memory:
        candidates.add(entity)
    return candidates


def rank_by_recency(scene_history, candidates, memory, current_reference, ignored_pronouns=fst_snd_prons, alpha=2,
                    mention_specific=False):
    memory_recent_first = reversed(memory)
    memory_recent_first = list(memory_recent_first)
    # next line will not work since there is also non-mention lines in the scene_history. How to find the length?
    # idea: use timestamps (make unique) in memory dict, iterate over timestamps (like in baseline)
    memory_scene = memory_recent_first[:len(scene_history)]
    recency_scores = {}
    for entity in candidates:
        recency_score = 0
        # distance = 1
        for index, (timepoint, reference) in enumerate(memory_scene):
            if reference in ignored_pronouns:
                # distance += 1
                pass
            elif mention_specific:
                # distance += 1
                if reference == current_reference:
                    if timepoint == entity:
                        distance = index + 1  # is distance only counted in mentions?
                        recency_score += (1 / distance) ** alpha
            elif not mention_specific:
                # distance += 1
                if timepoint == entity:
                    distance = index+1
                    recency_score += (1 / distance) ** alpha
        recency_scores[entity] = recency_score

    # TODO: normalize recency scores

    recency_ranking = {entity: score for entity, score in sorted(recency_scores.items(), key=lambda item: item[1])}

    return recency_ranking


# def recency_based_sort(candidates, recency_scores):
#     recency_ranking = {entity: score for entity, score in sorted(recency_scores.items(), key=lambda item: item[1])}
#     return recency_ranking



