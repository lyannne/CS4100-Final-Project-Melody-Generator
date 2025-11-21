import pickle
from collections import defaultdict
from typing import Iterable, Tuple, List, Dict
import numpy as np
import sys
import time
import argparse
import os

def construct_first_order(data: Iterable[Iterable[float]], save_to_file=None) -> Tuple[Dict[float, Dict[float, float]], Dict[float, float]]:
    """
    Input:
    `data`: list of numbers, representing a sequence of notes or durations
    
    Returns:
      - transition_matrix: dict where each key is a state and its value
        is another dict mapping next_state -> probability. For example:
        {1: {1: 0.3, 2: 0.6, 3: 0.1}, 2: {1: 0.2, 2: 0.1, 3: 0.7}}
        Probabilities for each state sum to 1.0.
      - start_distribution: A dict mapping state -> probability of starting with
        that state. For example: {1: 0.5, 2: 0.3, 3: 0.2}. Sums to 1.0.
    """

    # Materialize the outer iterable to allow multiple passes
    sequences = [list(seq) for seq in data]

    # Collects every note from every melody into one flat list
    all_values = [v for seq in sequences for v in seq]

    # Empty input case
    if len(all_values) == 0:
        return {}, {}

    # Unique states (sorted) determine rows/cols order
    unique_states = np.unique(np.asarray(all_values))
    states = list(unique_states.tolist())
    
    # Creates a mapping from each note to an index (e.g., {60: 0, 62: 1, 64: 2, 67: 3})
    state_to_index = {s: i for i, s in enumerate(states)}

    n = len(states)
    counts = np.zeros((n, n), dtype=int)
    start_counts = np.zeros(n, dtype=int)

    # Tally transitions inside each sequence and count starting notes
    for seq in sequences:
        if len(seq) == 0:
            continue
        # Count the first note in this sequence
        first_note = seq[0]
        start_counts[state_to_index[first_note]] += 1
      
        # Count transitions
        if len(seq) < 2:
            continue
        for a, b in zip(seq[:-1], seq[1:]):
            i = state_to_index[a]
            j = state_to_index[b]
            counts[i, j] += 1

    # Convert counts to probabilities (row-normalize)
    probs = counts.astype(float)
    row_sums = probs.sum(axis=1)
    nonzero = row_sums > 0
    if np.any(nonzero):
        probs[nonzero] = probs[nonzero] / row_sums[nonzero][:, None]

    # Convert start counts to start distribution
    start_dist = start_counts.astype(float)
    total_starts = start_dist.sum()
    if total_starts > 0:
        start_dist = start_dist / total_starts

    # Convert numpy arrays to dicts
    transition_dict = {}
    for i, state in enumerate(states):
        if row_sums[i] > 0:  # Only include states with outgoing transitions
            transition_dict[state] = {}
            for j, next_state in enumerate(states):
                prob = probs[i, j]
                if prob > 0:  # Only include non-zero probabilities
                    transition_dict[state][next_state] = prob

    start_dist_dict = {}
    for i, state in enumerate(states):
        prob = start_dist[i]
        if prob > 0:  # Only include non-zero probabilities
            start_dist_dict[state] = prob

    if save_to_file:
        with open(save_to_file, 'wb') as f:
            pickle.dump((transition_dict, start_dist_dict), f)

    return transition_dict, start_dist_dict


def construct_second_order(data: Iterable[Iterable[float]], save_to_file=None) -> Tuple[Dict[Tuple[float, float], Dict[float, float]], Dict[Tuple[float, float], float]]:
    """
    Input:
    `data`: list of numbers, representing a sequence of notes or durations
    
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

def main():
    parser = argparse.ArgumentParser(
        description="Construct markov model from data"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help='The path to the processed data file'
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help='The path to the output model directory'
    )
    parser.add_argument(
        "--order", "-or",
        required=True,
        help='Order for desired markov model, one of `first` or `second`',
        choices=["first", "second"]
    )
    args = parser.parse_args()

    input_data = args.input
    pitch_output_file = os.path.join(args.output, 'pitch.pkl')
    duration_output_file = os.path.join(args.output, 'duration.pkl')
    order = args.order

    try:
        with open(input_data, 'rb') as file:
            pitches, durations = pickle.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{input_data}' was not found.")
    except Exception as e:
        print(f"An error occurred during extraction: {e}")
           
    print("="*50)
    print("Constructing Markov Models...")

    start_time = time.time()
    if (order == 'first'):
        construct_first_order(pitches, pitch_output_file)
        construct_first_order(durations, duration_output_file)
    else:
        construct_second_order(pitches, pitch_output_file)
        construct_second_order(durations, duration_output_file)

    print("="*50)
    end_time = time.time()

    print("\nFinished constructing models: ")
    print(f"Completed process in {end_time - start_time:.2f} seconds")
    print(f"Saved {order} order markov model for {input_data} to {pitch_output_file} and {duration_output_file}")

if __name__ == "__main__":
    main()