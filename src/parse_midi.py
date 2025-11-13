import os.path

from music21 import converter, note, configure

# Need to adjust this functionality for certain MIDI files, to used a specific layer
# (e.g. melody) instead of flattening.
def parse_midi(filename):
  score = converter.parse(filename)
  notes = score.flatten().notes

  pitches = []
  durations = []

  notesWords = []

  for n in notes:
    if n.isNote:
      pitches.append(n.pitch.midi)
      durations.append(n.duration.quarterLength)

      notesWords.append(f"{n.name}{n.octave}")
    elif n.isChord:
      pitches.append(n.pitches[-1].midi)
      durations.append(n.duration.quarterLength)
  
  # return pitches, durations

  # configure.run()
  score.show("xml")

  return notesWords




if __name__ == '__main__':
    print(os.path.dirname(os.path.realpath(__name__)))
    print(parse_midi(".\\ArtPepper_Anthropology_FINAL.mid"))