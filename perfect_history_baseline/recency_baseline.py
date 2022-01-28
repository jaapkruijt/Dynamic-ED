from categorize_mentions import fst_snd_prons
from create_mention_lists import create_all_mention_data


def recency_baseline(combined_references_and_mentions, ordered_mention_data):
    recency_salience = {}
    alpha = 2

    for ent, ref in combined_references_and_mentions:
        recency_salience[ent] = {'1_01_0_21': 0}

    for ment_dict in ordered_mention_data:
        timestamp = ment_dict['timestamp']
        entity = ment_dict['entity']

        current_position = ordered_mention_data.index(ment_dict)
        history = []
        for hist_dict in ordered_mention_data[:current_position]:
            if hist_dict['timestamp'][:6] == timestamp[:6]:
                history.append(hist_dict)

        for ent in recency_salience:
            total_recency = 0
            for story in history:
                story_ent = story['entity']
                story_ref = story['reference']
                story_position = ordered_mention_data.index(story)
                dist = current_position - story_position

                if ent == story_ent:
                    if story_ref in fst_snd_prons:
                        rec = 0
                    else:
                        rec = (1 / dist) ** alpha
                else:
                    rec = 0
                total_recency += rec
            recency_salience[ent][timestamp] = total_recency

    return recency_salience


'''
def New recency algorithm 
input: candidate list (all mentioned entities); utterance history (e.g. scene) with information
about reference, speaker, timestamp, sentence; brain with memory of mentioned entities
function: when called, take candidate list and for each candidate compute recency (sum of inverted distances to 
previous mentions, based on utterance history and mention memory
function: sort candidate list based on recency scores
output: recency sorting, updated mention memory

'''
