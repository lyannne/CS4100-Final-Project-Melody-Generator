# AI Melody Generator - Project Task Breakdown

## Project Goal
Generate melodies using Markov models trained on MIDI data, with genre or mood-based control.

## Project Structure
```
/data
  /raw                           # Midi training files
    /genre1                     # Optional: organized by genre
    /genre2
    ...
  /processed                     # Parsed data to reuse
    pitch_sequences.pkl
    duration_sequences.pkl
    genre1_pitches.pkl
    genre1_durations.pkl
    ...
/docs                            # Documentation, data sources, research/notes
/models                          # Trained transition matrices
/outputs                         # Generated samples/MIDI sequences
/src                             # Source code
  parse_midi.py                 # Processes a single midi file into our representation
  #preprocess.py                # Script to process all midi files
  #markov.py                    # Builds transition matrices
  #generate.py                  # Generate melodies using trained models
  #evaluate.py                  # For metrics
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

### Optional: MuseScore (for visualization)
Download from https://musescore.org/ to view generated melodies as sheet music. 
Not required for core functionality.

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