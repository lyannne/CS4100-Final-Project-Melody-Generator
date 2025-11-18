from music21 import converter, note

REST = -1

def parse_midi(filename, chord_strategy='highest'):
    """
    Input:
    `filename`: path to a MIDI file
    `chord_strategy`: strategy for handling chords; options are
      'highest' (use highest note), 'root' (use root note), 'skip' (ignore chords)
  
    Returns:
      - pitches: list of MIDI pitch numbers (integers), with REST (-1) for rests
      - durations: list of durations in quarter lengths (floats)
    """
    try:
        score = converter.parse(filename)
        
        if len(score.parts) > 0:
            notes = score.parts[0].flatten().notes
            if len(notes) == 0:
                notes = score.flatten().notes
        else:
            notes = score.flatten().notes
        
        pitches = []
        durations = []
        current_time = 0
        
        for n in notes:
            if n.offset > current_time:
                rest_duration = n.offset - current_time
                pitches.append(REST)
                durations.append(rest_duration)

            if n.isNote:
                pitches.append(n.pitch.midi)
                durations.append(n.duration.quarterLength)
            elif n.isChord:
                if chord_strategy == 'highest':
                    pitches.append(n.pitches[-1].midi)
                elif chord_strategy == 'root':
                    pitches.append(n.root().midi)
                elif chord_strategy == 'skip': 
                    continue
                durations.append(n.duration.quarterLength)
            current_time = n.offset + n.duration.quarterLength

        return pitches, durations
    
    except Exception as e:
        return [], []