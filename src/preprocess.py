import os
import pickle
from parse_midi import parse_midi, REST

def preprocess_midis(input_dir, output_file=None, chord_strategy='hightest'):
    """
    Input:
    `input_dir`: directory containing MIDI files
    `output_file`: optional path to save preprocessed data as a pickle file
    `chord_strategy`: strategy for handling chords; options are
      'highest' (use highest note), 'root' (use root note), 'skip' (ignore chords)

    Returns:
        - all_pitches: list of lists of MIDI pitch numbers (integers), with REST (-1) for rests
        - all_durations: list of lists of durations in quarter lengths (floats)
    """
    all_pitches = []
    all_durations = []

    midi_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.mid') or f.lower().endswith('.midi')]

    print(f"Found {len(midi_files)} MIDI files in {input_dir}.")

    successful = 0
    failed = 0

    for i, filename in enumerate(midi_files):
        filepath = os.path.join(input_dir, filename)
        pitches, durations = parse_midi(filepath, chord_strategy=chord_strategy)

        if len(pitches) > 0:
            all_pitches.append(pitches)
            all_durations.append(durations)
            successful += 1
        else:
            failed += 1
            print(f"Warning: Failed to parse MIDI file {filename}.")

        if (i + 1) % 10 == 0 or (i + 1) == len(midi_files):
            print(f"Processed {i + 1}/{len(midi_files)} files. Successful: {successful}, Failed: {failed}")

    print(f"Finished processing. Total successful: {successful}, Total failed: {failed}")

    if output_file:
        with open(output_file, 'wb') as f:
            pickle.dump({'pitches': all_pitches, 'durations': all_durations}, f)
        print(f"Preprocessed data saved to {output_file}.")
    
    return all_pitches, all_durations
