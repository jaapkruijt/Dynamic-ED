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


def recency_algorithm(scene_history, candidates, memory, ignored_pronouns, alpha=2):
    memory_recent_first = reversed(memory)
    memory_recent_first = list(memory_recent_first)
    memory_scene = memory_recent_first[:len(scene_history)]
    recency_scores = {}
    for entity in candidates:
        recency_score = 0
        for index, timepoint in enumerate(memory_scene):
            if timepoint == entity:
                distance = index+1
                recency_score += (1 / distance) ** alpha
        recency_scores[entity] = recency_score

    return recency_scores


def recency_based_sort(candidates, recency_scores):
    pass



