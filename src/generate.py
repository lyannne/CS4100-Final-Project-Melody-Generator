from music21 import stream, note, tempo, midi
import random
import argparse
import pickle
import time

REST = -1

def generate_first_order(length, BPM, pitch_model, duration_model, starting_pitch_dist, starting_duration_dist, save_path=None):
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

    current_note = random.choices(
        population=list(starting_pitch_dist.keys()),
        weights=list(starting_pitch_dist.values())
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
            current_note = random.choices(
                population=list(transitions.keys()),
                weights=list(transitions.values())
            )[0]
        else:
            current_note = random.choices(
                population=list(starting_pitch_dist.keys()),
                weights=list(starting_pitch_dist.values())
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

def generate_second_order(length, BPM, pitch_model, duration_model, starting_pitch_dist, starting_duration_dist, save_path=None):
    """
    Input:
        `length`: float representing total length in seconds of the generated piece.
        `BPM`: float representing beats per minute of the MIDI.
        `pitch_model`: markov transition dictionary as a dict {(note1, note2): {next_note: probability}}.
        `duration_model`: markov transition dictionary as a dict {(duration1, duration2): {next_duration: probability}}.
        `starting_pitch_dist`: Initial probability distribution as a dict {(note1, note2): probability}.
        `starting_duration_dist`: initial probability distribution as a dict {(duration1, duration2): probability}.
        `save`: whether to save the resulting MIDI file (default False).

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
            next_pitch = random.choices(
                population=list(transitions.keys()),
                weights=list(transitions.values())
            )[0]
        else:
            new_note = random.choices(
                population=list(starting_pitch_dist.keys()),
                weights=list(starting_pitch_dist.values())
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

    args = parser.parse_args()

    # set up args
    input_model_dir = args.input
    output_file = args.output
    order = args.order
    bpm = args.bpm
    length = args.length

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
        generate_first_order(length, bpm, pitch_transitions, duration_transitions, pitch_dist, duration_dist, output_file)
    if order == 'second':
        generate_second_order(length, bpm, pitch_transitions, duration_transitions, pitch_dist, duration_dist, output_file)
    end_time = time.time()

    print("="*50)
    print("\nFinished generating melody: ")
    print(f"Completed process in {end_time - start_time:.2f} seconds")
    print(f"Saved melody to {output_file}")

if __name__ == "__main__":
    main()