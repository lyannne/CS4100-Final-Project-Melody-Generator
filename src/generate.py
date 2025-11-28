from music21 import stream, note, tempo, midi
import random
import argparse
import pickle
import time

REST = -1
KEYS = {
    'C_major': [0, 2, 4, 5, 7, 9, 11],   # C D E F G A B
    'G_major': [7, 9, 11, 0, 2, 4, 6],   # G A B C D E F#
    'D_major': [2, 4, 6, 7, 9, 11, 1],   # D E F# G A B C#
    'A_major': [9, 11, 1, 2, 4, 6, 8],   # A B C# D E F# G#
    'E_major': [4, 6, 8, 9, 11, 1, 3],   # E F# G# A B C# D#
    'F_major': [5, 7, 9, 10, 0, 2, 4],   # F G A Bb C D E
    'A_minor': [9, 11, 0, 2, 4, 5, 7],   # A B C D E F G
    'E_minor': [4, 6, 7, 9, 11, 0, 2],   # E F# G A B C D
    'D_minor': [2, 4, 5, 7, 9, 10, 0],   # D E F G A Bb C
}

def is_in_key(midi_note, key):
    """Check if a MIDI note number is in the given key."""
    if key not in KEYS:
        return True 
    
    pitch_class = midi_note % 12
    
    return pitch_class in KEYS[key]

def generate_first_order(length, BPM, pitch_model, duration_model, starting_pitch_dist, starting_duration_dist, save_path=None, key=None):
    """
    Input:
        `length`: float representing total length in seconds of the generated piece.
        `BPM`: float representing beats per minute of the MIDI.
        `pitch_model`: markov transition dictionary as a dict {note: {next_note: probability}}.
        `duration_model`: markov transition dictionary as a dict {duration: {next_duration: probability}}.
        `starting_pitch_dist`: Initial probability distribution as a dict {note: probability}.
        `starting_duration_dist`: initial probability distribution as a dict {duration: probability}.
        `save`: whether to save the resulting MIDI file (default False).

    Returns:
        music21.stream.Stream: the generated music21 stream object.
    """
    
    output_stream = stream.Stream()
    output_stream.append(tempo.MetronomeMark(number=BPM))

    seconds_per_beat = 60.0 / BPM
    current_time = 0.0

    candidates = starting_pitch_dist
    if key is not None:
        in_key_candidates = {note: prob for note, prob in candidates.items() 
                            if note == REST or is_in_key(note, key)}
        if in_key_candidates:
            total = sum(in_key_candidates.values())
            candidates = {note: prob/total for note, prob in in_key_candidates.items()}
    
    current_note = random.choices(
        population=list(candidates.keys()),
        weights=list(candidates.values())
    )[0]
        

    current_duration = random.choices(
        population=list(starting_duration_dist.keys()),
        weights=list(starting_duration_dist.values())
    )[0]

    while current_time < length:
        if current_note == REST:
            n = note.Rest()
        else:
            n = note.Note(current_note)
        
        n.quarterLength = current_duration
        output_stream.append(n)

        current_time += seconds_per_beat * n.quarterLength

        if current_note in pitch_model:
            transitions = pitch_model[current_note]

            if key is not None and current_note != REST:
                in_key_transitions = {note: prob for note, prob in transitions.items() 
                                     if note == REST or is_in_key(note, key)}
                if in_key_transitions:
                    total = sum(in_key_transitions.values())
                    transitions = {note: prob/total for note, prob in in_key_transitions.items()}
            
            current_note = random.choices(
                population=list(transitions.keys()),
                weights=list(transitions.values())
            )[0]
        else:
            candidates = starting_pitch_dist
            if key is not None:
                in_key_candidates = {note: prob for note, prob in candidates.items() 
                                   if note == REST or is_in_key(note, key)}
                if in_key_candidates:
                    total = sum(in_key_candidates.values())
                    candidates = {note: prob/total for note, prob in in_key_candidates.items()}
            current_note = random.choices(
                population=list(candidates.keys()),
                weights=list(candidates.values())
            )[0]
        
        if current_duration in duration_model:
            transitions = duration_model[current_duration]
            current_duration = random.choices(
                population=list(transitions.keys()),
                weights=list(transitions.values())
            )[0]
        else:
            current_duration = random.choices(
                population=list(starting_duration_dist.keys()),
                weights=list(starting_duration_dist.values())
            )[0]

    if save_path:
        midi_file = midi.translate.streamToMidiFile(output_stream)
        midi_file.open(save_path, "wb")
        midi_file.write()
        midi_file.close()
        print(f"Saved as {save_path}")

    return output_stream

def generate_second_order(length, BPM, pitch_model, duration_model, starting_pitch_dist, starting_duration_dist, save_path=None, key=None):
    """
    Input:
        `length`: float representing total length in seconds of the generated piece.
        `BPM`: float representing beats per minute of the MIDI.
        `pitch_model`: markov transition dictionary as a dict {(note1, note2): {next_note: probability}}.
        `duration_model`: markov transition dictionary as a dict {(duration1, duration2): {next_duration: probability}}.
        `starting_pitch_dist`: Initial probability distribution as a dict {(note1, note2): probability}.
        `starting_duration_dist`: initial probability distribution as a dict {(duration1, duration2): probability}.
        `save_path`: path to save MIDI file (optional).
        `key`: musical key to constrain generation (optional).

    Returns:
        music21.stream.Stream: the generated music21 stream object.
    """

    output_stream = stream.Stream()
    output_stream.append(tempo.MetronomeMark(number=BPM))

    seconds_per_beat = 60.0 / BPM
    current_time = 0.0

    current_note = random.choices(
        population=list(starting_pitch_dist.keys()),
        weights=list(starting_pitch_dist.values())
    )[0]

    current_duration = random.choices(
        population=list(starting_duration_dist.keys()),
        weights=list(starting_duration_dist.values())
    )[0]

    for i in range(2):
        pitch = current_note[i]
        duration = current_duration[i]
        
        if pitch == REST:
            n = note.Rest()
        else:
            n = note.Note(pitch)
        n.quarterLength = duration
        output_stream.append(n)
        current_time += seconds_per_beat * n.quarterLength

    while current_time < length:
        if current_note in pitch_model:
            transitions = pitch_model[current_note]
            
            if key is not None:
                in_key_transitions = {note: prob for note, prob in transitions.items() 
                                     if note == REST or is_in_key(note, key)}
                if in_key_transitions:
                    total = sum(in_key_transitions.values())
                    transitions = {note: prob/total for note, prob in in_key_transitions.items()}
            
            next_pitch = random.choices(
                population=list(transitions.keys()),
                weights=list(transitions.values())
            )[0]
        else:
            candidates = starting_pitch_dist
            
            if key is not None:
                in_key_candidates = {note_pair: prob for note_pair, prob in candidates.items() 
                                   if note_pair[1] == REST or is_in_key(note_pair[1], key)}
                if in_key_candidates:
                    total = sum(in_key_candidates.values())
                    candidates = {note_pair: prob/total for note_pair, prob in in_key_candidates.items()}
            
            new_note = random.choices(
                population=list(candidates.keys()),
                weights=list(candidates.values())
            )[0]
            next_pitch = new_note[1]
        
        if current_duration in duration_model:
            transitions = duration_model[current_duration]
            next_duration = random.choices(
                population=list(transitions.keys()),
                weights=list(transitions.values())
            )[0]
        else:
            new_duration = random.choices(
                population=list(starting_duration_dist.keys()),
                weights=list(starting_duration_dist.values())
            )[0]
            next_duration = new_duration[1]

        if next_pitch == REST:
            n = note.Rest()
        else:
            n = note.Note(next_pitch)
        n.quarterLength = next_duration
        output_stream.append(n)
        current_time += seconds_per_beat * n.quarterLength

        current_note = (current_note[1], next_pitch)
        current_duration = (current_duration[1], next_duration)

    if save_path:
        midi_file = midi.translate.streamToMidiFile(output_stream)
        midi_file.open(save_path, "wb")
        midi_file.write()
        midi_file.close()
        print(f"Saved as {save_path}")

    return output_stream

def main():
    parser = argparse.ArgumentParser(description="Generate midi files")

    parser.add_argument(
        "--input", "-i",
        help="Path to the model directory"
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to the sample output file"
    )
    parser.add_argument(
        "--order", "-or",
        choices=['first', 'second'],
        help="`first` or `second` depending out input model."
    )
    parser.add_argument(
        "--bpm", 
        type=int, 
        default=120,
        help="Set BPM, default 120"
    )
    parser.add_argument(
        "--length", 
        type=int, 
        default=30,
        help="Set length [in seconds] if provided. Default 30"
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

    # set up args
    input_model_dir = args.input
    output_file = args.output
    order = args.order
    bpm = args.bpm
    length = args.length
    key = args.key

    # get models
    pitch_model = input_model_dir + '/pitch.pkl'
    duration_model = input_model_dir + '/duration.pkl'
    try:
        with open(pitch_model, 'rb') as file:
            pitch_transitions, pitch_dist = pickle.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{pitch_model}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred during extraction: {e}")
        return

    try:
        with open(duration_model, 'rb') as file:
            duration_transitions, duration_dist = pickle.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{duration_model}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred during extraction: {e}")
        return
            
    print("="*50)
    print("Generating melodies...")

    start_time = time.time()
    if order == 'first':
        generate_first_order(length, bpm, pitch_transitions, duration_transitions, pitch_dist, duration_dist, output_file, key)
    if order == 'second':
        generate_second_order(length, bpm, pitch_transitions, duration_transitions, pitch_dist, duration_dist, output_file, key)
    end_time = time.time()

    print("="*50)
    print("\nFinished generating melody: ")
    print(f"Completed process in {end_time - start_time:.2f} seconds")
    print(f"Saved melody to {output_file}")

if __name__ == "__main__":
    main()