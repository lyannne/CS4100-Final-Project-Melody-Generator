# AI Melody Generator - Project Task Breakdown

## Project Goal
Generate melodies using Markov models trained on MIDI data, with genre or mood-based control.

## Project Structure
```
/data
  /raw                           # Midi training files
    /classical                 
    /jazz
    /nes
    /pop
  /processed                     # Parsed data to reuse
/docs                            # Documentation, data sources, research/notes
/models                          # Trained transition matrices
  /jazz_highest_second          # Models organized by directory
    /pitch.pkl
    /duration.pkl
/outputs                         # Generated samples/MIDI sequences
  /jazz_highest_second          # Outputs organized by directory
    /1.mid
/src                             # Source code
  generate.py                   # Generates melodies using provided markov models
  markov.py                     # Constructs markov models of different orders
  parse_midi.py                 # Processes a single midi file into our representation
  pipeline.py                   # Contains full pipeline to train a model and generate a melody
  preprocess.py                 # Script to process all midi files by genre
  #evaluate.py                  # For metrics/figures/etc.
requirements.txt                 # Python dependencies
README.md
```

## Set-up

### Dependencies
```bash
pip install -r requirements.txt
```

### Data
MIDI files are not included directly due to size. Instead, follow these steps:
1. Download each zip from [this Google Drive folder](https://drive.google.com/drive/folders/1j48kT7JdG92KWkNUhN6xpGdX9PffIkfU?usp=sharing).
2. Extract them into `data/raw/`. They should remain in their folders, e.g.: `data/raw/classical/**.mid` 

Note: There is now data from [XMusic](https://xmusic-project.github.io) which will be processed differently.

### Optional: MuseScore (for visualization)
Download from https://musescore.org/ to view generated melodies as sheet music.  
Not required for core functionality.

### Using the program
The easiest way to do this is with `pipeline.py`. This keeps all generated files well-organized, with consistent names to allow efficient data and model reuse.  
Make sure you're in the root directory. Then, you will call `python3 src/pipeline.py` in your command line, and the following flags are available:  
`--genres` or `-g` : Takes one or more of `classical`, `jazz`, `nes`, `pop`, or `all`. e.g. `-g nes pop`. Not required; defaults to `all`. Beware `all` will take some time to process.  
`--order` or `-or` : Takes one of `first` or `second`, to determine the order of the markov model. Required.  
`--chord-strategy` or `-c` : Takes one of `highest`, `root`, or `skip`, to determine how to process chords in midi files. Not required; defaults to `highest`.  
`--num-samples` or `-n` : Takes how many samples to generate. Not required; defaults to 1.  
`--bpm` : Takes desired BPM for generated melodies. Not required; defaults to 120.  
`--length` : Takes desired length for generated melodies. Not required; defaults to 30.  
An example command looks like:
```bash
python3 src/pipeline.py -g jazz -or second -n 5
```

Note: The script will not re-generate preprocessed data or models if they already exist. Processed data is unique by its genres and chord strategy, and a model its genres, chord strategy, and order. If you want to generate a second version of these for some reason, rename the old one or move it to a different directory.  

Note 2: You can also run `preprocess.py`, `markov.py`, and `generate.py` independently with CL args. But why would you do this?  

## Approach
- Train Markov models (1st and 2nd order) on pitch sequences
- Train separate Markov model on rhythm/duration sequences
- Combine pitch + rhythm to generate complete melodies
- Add genre-specific models OR mood-based constraints for variation

## Major Components
**1. Data & Preprocessing**
- Collect MIDI files
- Parse into pitch and duration sequences
- Clean and organize data

**2. Core Markov Models**
- 1st-order model (baseline)
- 2nd-order model (better context)
- Separate rhythm model

**3. Generation**
- Sample from trained models
- Combine pitch + rhythm
- Output as MIDI files

**4. Enhancement (choose at least one)**
- Genre-specific: Train models on different musical styles
- Mood-based: Add constraints to guide generation toward emotional tone
- Harmony generation: Modify training and generation to create a harmony from an existing melody sequence

**5. Evaluation & Documentation**
- Generate sample outputs
- Compare different approaches (metrics + listening)
- Write up results, prepare demo, and create graphs/figures

## Timeline
- [Nov 2 - Nov 8]: environment setup, data, 1st order model
- [Nov 9 - Nov 15]: 2nd order, rhythm generation
  - Meet with TA by **Nov 14**
- [Nov 16 - Nov 22]: Enhancement features, generate samples
- [Nov 23 - Nov 29]: Prepare slides, demos, figures
  - Slides due **Nov 28**
- [Nov 30 - Dec 10]: Final report, clean up repo
  - Presentations week of **Dec 1**
  - Final deliverables due **Dec 10**