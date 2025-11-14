import pickle
from collections import defaultdict
from typing import Iterable, Tuple, Dict

def secondOrderMM(data: Iterable[Iterable[float]], save_to_file=None) -> Tuple[Dict[Tuple[float, float], Dict[float, float]], Dict[Tuple[float, float], float]]:
    """
    Input:
    `data`: list of melodies, with each melody represented as a sequence of numbers
    
    Returns:
        - transition_matrix: dict where each key is a pair of states (note1, note2) 
          and its value is another dict mapping next_state -> probability
        - start_distribution: dict mapping (note1, note2) -> probability of starting 
          with that pair. Probabilities sum to 1.0.
    """
    
    sequences = [list(seq) for seq in data]
    
    if len(sequences) == 0:
        return {}, {}
    
    transitions = defaultdict(lambda: defaultdict(int))
    start_counts = defaultdict(int)
    
    for seq in sequences:
        if len(seq) < 2:
            continue
            
        start_pair = (seq[0], seq[1])
        start_counts[start_pair] += 1
        
        if len(seq) < 3:
            continue
            
        for i in range(len(seq) - 2):
            state = (seq[i], seq[i + 1])
            next_val = seq[i + 2]
            transitions[state][next_val] += 1
    
    transition_dict = {}
    for state, next_vals in transitions.items():
        total = sum(next_vals.values())
        if total > 0:
            transition_dict[state] = {val: count / total for val, count in next_vals.items()}
    
    total_starts = sum(start_counts.values())
    start_dist_dict = {}
    if total_starts > 0:
        start_dist_dict = {pair: count / total_starts for pair, count in start_counts.items()}
    
    if save_to_file:
        with open(save_to_file, 'wb') as f:
            pickle.dump((transition_dict, start_dist_dict), f)
    
    return transition_dict, start_dist_dict


