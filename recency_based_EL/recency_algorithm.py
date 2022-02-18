from data_preprocessing import prepare_data
from perfect_history_baseline.categorize_mentions import fst_snd_prons


def create_utterance_history(data, index):
    history_from_start = data[:index]
    current = history_from_start[index]
    scene_history = []
    scene_timestamps = []
    for token in history_from_start[::-1]:
        if token[1] != current[1]:
            break
        else:
            scene_history.append(token)
            scene_timestamps.append(token[0])
    scene_history_rev = reversed(scene_history)
    scene_history_rev = list(scene_history_rev)
    scene_timestamps_rev = reversed(scene_timestamps)
    scene_timestamps_rev = list(scene_timestamps_rev)
    return scene_history_rev, scene_timestamps_rev


def create_candidate_list(memory):
    candidates = set()
    for entity, reference in memory:
        candidates.add(entity)
    return candidates


def rank_by_recency(scene_timestamps, candidates, memory, current_label, ignored_pronouns=fst_snd_prons, alpha=2,
                    mention_specific=False):
    """
    :param scene_timestamps: List. All timestamps for the current scene from current timestamp to beginning
    :param candidates: List. All entity cluster identifiers known at to this point
    :param memory: Dict. timestamp:(mention, label)
    :param current_label: String. Label used in the current mention
    :param ignored_pronouns: List. Contains the labels which will be ignored by the ranker
    :param alpha: Int. Parameterizable value to simulate rate of forgetting
    :param mention_specific: Bool. Whether the ranker will compute recency based on the label or not
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
        for index, (timepoint, reference) in enumerate(memory_scene):
            if reference in ignored_pronouns:
                # distance += 1
                pass
            elif mention_specific:
                # distance += 1
                if reference == current_label:
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



