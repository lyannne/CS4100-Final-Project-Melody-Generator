from music21 import converter, note

# Need to adjust this functionality for certain MIDI files, to used a specific layer
# (e.g. melody) instead of flattening.
def parse_midi(filename):
  score = converter.parse(filename)
  notes = score.flatten().notes

  pitches = []
  durations = []

  for n in notes:
    if n.isNote:
      pitches.append(n.pitch.midi)
      durations.append(n.duration.quarterLength)
    elif n.isChord:
      pitches.append(n.pitches[-1].midi)
      durations.append(n.duration.quarterLength)
  
  return pitches, durations
