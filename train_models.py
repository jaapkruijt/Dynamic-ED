"""
Steps during training:

prepare the dataset (code from data_preprocessing); think about how exactly you will use the dataset

Iterate over the scenes/tokens in the dataset:

    If a token contains a mention (as annotated):

        Collect the utterance history for the scene up to that point (index) #mostly done, perhaps rethink

        Collect the history of all the mentions within the scene #perhaps restructure; add sentence

        Create the candidate list from the mention history #done

        Get the current mention token #simple step

        Get the current sentence #relatively simple step

        Feed the utterance history, mention history, candidate list and current mention to the recency rankers
        --> Get recency rankings (2 versions: reference-specific and reference-agnostic) #mostly done, normalize

        Feed the utterance history, mention history, candidate list and current sentence to the context
                    embeddings ranker #find out-of-the-box
        --> Get context ranking

        Combine context and recency rankings in one ranking based on variable weights #to do

        Filter for gender-mismatch with previous mentions in third-person pronouns #to do

        If the highest ranked candidate > threshold:

            Select that candidate, add to output

        Else:

            Select 'new'/'unknown', get the corresponding identifier from the gold data, add to output

        Compare with gold output, compute loss --> HOW?? #to do

        Based on loss, update either forgetting parameter (recency) or combination weights

Experiment with: forgetting parameter, window size, weights, rankers in isolation, threshold

Evaluate: system output(s), threshold, performance over time (as history size increases), how many times the system
            chose 'new'/'unknown'

"""

