from typing import Iterable, Tuple, List, Dict
import numpy as np


def firstOrderMM(data: Iterable[Iterable[float]]) -> Tuple[Dict[float, Dict[float, float]], Dict[float, float]]:
	"""
	Input:
	`data`: list of melodies, with each melody represented as a sequence of numbers
	
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

	return transition_dict, start_dist_dict
