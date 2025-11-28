import argparse
import os
import subprocess

def join_genres(genres: list):
    """
    Join genres in a consistent order with underscores.
    Always sorts the list so the name is deterministic.
    """
    return "_".join(sorted(genres))

def get_preprocessed_path(genres: list, chord_strategy: str, base_dir="data/processed"):
    """
    Returns the path to the preprocessed .pkl file.
    """
    genre_str = join_genres(genres)
    filename = f"processed_{genre_str}_{chord_strategy}.pkl"
    full_path = os.path.join(base_dir, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    return full_path

def get_model_dir(genres: list, chord_strategy: str, order: str, base_dir="models"):
    """
    Returns a directory path for a Markov model.
    """
    genre_str = join_genres(genres)
    dirname = f"{genre_str}_{chord_strategy}_{order}"
    full_path = os.path.join(base_dir, dirname)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def get_sample_dir(model_dir: str, base_dir="outputs"):
    """
    Returns path for saving a generated MIDI sample.
    """
    model_name = os.path.basename(model_dir)
    full_path = os.path.join(base_dir, model_name)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def file_nonempty(path):
    return os.path.exists(path) and os.path.getsize(path) > 0

def main():
    # Initialize Parser
    parser = argparse.ArgumentParser(
        description="Full pipeline to generate melodies"
    )
    parser.add_argument(
        "--genres", "-g",
        nargs="+",
        required=False,
        choices=["classical", "jazz", "nes", "pop", "all", "all-genres", "angry", "warm", "sad", "exciting", "all-moods"],
        default=['all'],
        help='One or more genres/moods to include from data/raw, default `all-genres`'
    )
    parser.add_argument(
        "--order", "-or",
        required=True,
        help="Order for desired markov model, one of `first` or `second`",
        choices=["first", "second"]
    )
    parser.add_argument(
        "--chord-strategy", "-c",
        choices=["highest", "root", "skip"],
        default="highest",
        help="How to reduce chords to a single pitch, one of `highest`, `root`, `skip`"
    )
    parser.add_argument(
        "--num-samples", "-n",
        default=1,
        help="How many samples to generate",
        type=int
    )
    parser.add_argument(
        "--bpm",
        default=120,
        type=int,
        help="Set BPM for generated melodies. Default 120."
    )
    parser.add_argument(
        "--length",
        default=30,
        type=int,
        help="Set length of generated melodies. Default 30sec."
    )
    parser.add_argument(
        "--key", "-k",
        type=str,
        default=None,
        choices=['C_major', 'G_major', 'D_major', 'A_major', 'E_major', 'F_major', 
                'A_minor', 'E_minor', 'D_minor', 'Bb_major'],
        help="Musical key to constrain generation (e.g., C_major, A_minor)"
    )
    args = parser.parse_args()

    # Get args
    genres = args.genres
    order = args.order
    chord_strategy = args.chord_strategy
    num_samples = args.num_samples
    bpm = args.bpm
    length = args.length
    key = args.key
    if 'all' in genres:
        genres = ['classical', 'jazz', 'nes', 'pop', 'angry', 'sad', 'exciting', 'warm']
    elif 'all-genres' in genres:
        genres = ['classical', 'jazz', 'nes', 'pop']
    elif 'all-moods' in genres:
        genres = ['angry', 'sad', 'exciting', 'warm']

    print("="*50)
    print("MIDI Markov Model Pipeline")
    print("="*50)

    # Setup file locations
    preprocessed_file = get_preprocessed_path(genres, chord_strategy)
    model_dir = get_model_dir(genres, chord_strategy, order)
    sample_dir = get_sample_dir(model_dir)

    required_files = ["pitch.pkl", "duration.pkl"]

    model_exists = all(file_nonempty(os.path.join(model_dir, f)) for f in required_files)
    preprocess_exists = os.path.exists(preprocessed_file)

    if (not model_exists and not preprocess_exists):
        subprocess.run([
            "python3", "src/preprocess.py",
            "-o", preprocessed_file,
            "-c", chord_strategy,
            "-g", *genres
        ])
    if (not model_exists):
        subprocess.run([
            "python3", "src/markov.py",
            "-i", preprocessed_file,
            "-o", model_dir,
            "-or", order
        ])
    
    for i in range(1, num_samples + 1):
        if key is None:
            fname = os.path.join(sample_dir, f"{i}.mid")
            subprocess.run([
                "python3", "src/generate.py",
                "-i", model_dir,
                "-o", fname,
                "-or", order,
                "--bpm", str(bpm),
                "--length", str(length),
            ])
        else:
            key_dir = os.path.join(sample_dir, key)
            os.makedirs(key_dir, exist_ok=True)
            fname = os.path.join(key_dir, f"{i}.mid")
            subprocess.run([
                "python3", "src/generate.py",
                "-i", model_dir,
                "-o", fname,
                "-or", order,
                "--bpm", str(bpm),
                "--length", str(length),
                "-k", key,
            ])

    print("\n" + "="*50)
    print("Pipeline complete!")
    print("="*50)

if __name__ == "__main__":
    main()