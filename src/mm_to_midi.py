from music21 import stream, note, tempo, midi
import random

def mm_to_midi(length, BPM, markov_model, starting_dist, save=False):
    """
    Generate a MIDI sequence from a Markov model.

    Parameters:
        length (float): Total length in seconds of the generated piece.
        BPM (float): Beats per minute of the MIDI.
        markov_model (dict): Markov transition dictionary {note: {next_note: probability}}.
        starting_dist (dict): Initial probability distribution {note: probability}.
        save (bool): Whether to save the resulting MIDI file (default False).

    Returns:
        music21.stream.Stream: The generated music21 stream object.
    """
    output_stream = stream.Stream()
    output_stream.append(tempo.MetronomeMark(number=BPM))

    seconds_per_beat = 60.0 / BPM
    current_time = 0.0

    current_note = random.choices(
        population=list(starting_dist.keys()),
        weights=list(starting_dist.values())
    )[0]

    while current_time < length:
        n = note.Note(current_note)
        n.quarterLength = 1
        output_stream.append(n)

        current_time += seconds_per_beat * n.quarterLength

        if current_note in markov_model:
            transitions = markov_model[current_note]
            current_note = random.choices(
                population=list(transitions.keys()),
                weights=list(transitions.values())
            )[0]
        else:
            current_note = random.choices(
                population=list(starting_dist.keys()),
                weights=list(starting_dist.values())
            )[0]

    if save:
        midi_file = midi.translate.streamToMidiFile(output_stream)
        midi_file.open("markov_output.mid", "wb")
        midi_file.write()
        midi_file.close()
        print("Saved as markov_output.mid")

    return output_stream
