import os
import pickle
from parse_midi import parse_midi, REST
import time
import argparse

def preprocess_midis(input_dirs, output_file=None, chord_strategy='highest'):
    """
    Input:
    `input_dirs`: list of directories containing MIDI files
    `output_file`: optional path to save preprocessed data as a pickle file
    `chord_strategy`: strategy for handling chords; options are
      'highest' (use highest note), 'root' (use root note), 'skip' (ignore chords)

    Returns:
        - all_pitches: list of lists of MIDI pitch numbers (integers), with REST (-1) for rests
        - all_durations: list of lists of durations in quarter lengths (floats)
    """
    all_pitches = []
    all_durations = []

    for input_dir in input_dirs:
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
            pickle.dump((all_pitches, all_durations), f)
        print(f"Preprocessed data saved to {output_file}.")
        
    return all_pitches, all_durations

def main():
    parser = argparse.ArgumentParser(
        description="Preprocess MIDI files into pitch/duration sequences."
    )

    parser.add_argument(
        "--genres", "-g",
        nargs="+",
        required=True,
        help="One or more genres to include from data/raw containing MIDI files."
    )

    parser.add_argument(
        "--output-name", "-o",
        required=True,
        help="Name to save preprocessed output (e.g. data/processed/[OUTPUT_NAME].pkl)."
    )

    parser.add_argument(
        "--chord-strategy", "-c",
        choices=["highest", "root", "skip"],
        default="highest",
        help="How to reduce chords to a single pitch."
    )

    args = parser.parse_args()
    
    input_dirs = [f"data/raw/{genre}" for genre in args.genres]

    print("="*50)
    print("Preprocessing MIDI files...")
    print("Input directories:", args.genres)

    start_time = time.time()

    preprocess_midis(
        input_dirs = input_dirs,
        output_file = args.output_name,
        chord_strategy = args.chord_strategy
    )

    end_time = time.time()
    print("="*50)

    print("\nFinished processing:")
    print(f"Completed in {end_time - start_time:.2f} seconds")
    print(f"Saved processed data to data/processed/{args.output_name}.pkl")

if __name__ == "__main__":
    main()