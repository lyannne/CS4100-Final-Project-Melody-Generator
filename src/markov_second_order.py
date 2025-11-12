import pickle
from collections import defaultdict

def train_second_order(sequence, save_to_file=None):
    if len(sequence) < 3:
        raise ValueError("Sequence must have at least 3 elements")
    
    transitions = defaultdict(lambda: defaultdict(int))
    
    for i in range(len(sequence) - 2):
        state = (sequence[i], sequence[i + 1])
        next_val = sequence[i + 2]
        transitions[state][next_val] += 1
    
    model = {}
    for state, next_vals in transitions.items():
        total = sum(next_vals.values())
        model[state] = {val: count / total for val, count in next_vals.items()}
    
    if save_to_file:
        with open(save_to_file, 'wb') as f:
            pickle.dump(model, f)
    
    return model

