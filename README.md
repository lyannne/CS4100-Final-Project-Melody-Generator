# AI Melody Generator - Project Task Breakdown

## Project Goal
Generate melodies using Markov models trained on MIDI data, with genre or mood-based control.

## Project Structure
```
/data
  /raw                           # Midi training files
    /angry                      # Organized by genre/mood
    /classical
  /processed                     # Parsed data to reuse
/docs                             # Documentation, data sources, research/notes
/evaluation                       # Generated figures
/models                           # Trained transition matrices
  /jazz_highest_second           # Models organized by directory
    /pitch.pkl
    /duration.pkl
/outputs                          # Generated samples/MIDI sequences
  /jazz_highest_second           # Outputs organized by directory
    /1.mid
/src                              # Source code
  evaluate.ipynb                 # Figures/metrics for report
  evaluate.py                    # Figures/metrics for presentation
  generate.py                    # Generates melodies using provided markov models
  markov.py                      # Constructs markov models of different orders
  mood_data_pipeline.py          # Organizes mood dataset by mood labels in folders
  parse_midi.py                  # Processes a single midi file into our representation
  pipeline.py                    # Contains full pipeline to train a model and generate a melody
  preprocess.py                  # Script to process all midi files by genre
requirements.txt                  # Python dependencies
README.md
```

## Set-up

### Dependencies
```bash
pip install -r requirements.txt
```

### Data
MIDI files are not included directly due to size. Instead, follow these steps:
1. Download each genre zip from [this Google Drive folder](https://drive.google.com/drive/folders/1j48kT7JdG92KWkNUhN6xpGdX9PffIkfU?usp=sharing).
2. Extract them into `data/raw/`. They should remain in their folders, e.g.: `data/raw/classical/**.mid` 

There is also data from [XMusic](https://xmusic-project.github.io) in the Google Drive folder. If you wish to create mood models:
1. Download the zip and extract into any folder (preferably somewhere easily accessible from this project).
2. Run `python src/mood_data_pipeline.py --organize --source {source_dir_path}`. You can also adjust the destination directory with the `--dest` tag for where the sorted files will go, but by default they will go into mood folders in `data/raw/`.

### Optional: MuseScore (for visualization)
Download from https://musescore.org/ to view generated melodies as sheet music.  
Not required for core functionality. We do not include code to do this. Just fun to consider!

### Using the program
The easiest way to do this is with `pipeline.py`. This keeps all generated files well-organized, with consistent names to allow efficient data and model reuse.  
Make sure you're in the root directory. Then, you will call `python src/pipeline.py` in your command line, and the following flags are available:  
`--genres` or `-g` : Takes one or more of `classical`, `jazz`, `nes`, `pop`, or `all`. e.g. `-g nes pop`. Not required; defaults to `all`. Beware `all` will take some time to process.  
`--order` or `-or` : Takes one of `first` or `second`, to determine the order of the markov model. Required.  
`--chord-strategy` or `-c` : Takes one of `highest`, `root`, or `skip`, to determine how to process chords in midi files. Not required; defaults to `highest`.  
`--num-samples` or `-n` : Takes how many samples to generate. Not required; defaults to 1.  
`--bpm` : Takes desired BPM for generated melodies. Not required; defaults to 120.  
`--length` : Takes desired length for generated melodies. Not required; defaults to 30. 
`--key` or `-k` : Takes desired key for generated melodies. Not required; default none.
`--rhythm` or `-r` : Takes desired rhythm profile. Not required; default none. 
An example command looks like:
```bash
python src/pipeline.py -g jazz -or second -n 5 -c root -k C_major
```

We include multiple pre-built models in the repository. You can find them in models/. Each model directory is of the form {genre(s)}\_{chord-strategy}\_{model-order}, where there can be any number of genres, separated by `_`. Thus, if you want to generate from the `classical_root_second` model, the genre, order, and chord-strategy tags must match exactly. The rest of the tags do not change the model, so you may experiment to your liking!

To actually run the generated samples, you need some form of MIDI player. Windows has this natively; MacOS does not. There are plenty of free options available for download, such as NS MIDI Player, but choose your favorite! 

Note: The script will not re-generate preprocessed data or models if they already exist. Processed data is unique by its genres and chord strategy, and a model its genres, chord strategy, and order. If you want to generate a second version of these for some reason, rename the old one or move it to a different directory.  

Note 2: You can also run `preprocess.py`, `markov.py`, and `generate.py` independently with CL args. However it requires significantly more effort in determining the appropriate input/output file locations, and we do not recommend it.

## Approach
- Construct Markov models (1st and 2nd order) from pitch sequences
- Construct separate Markov model on rhythm/duration sequences
- Combine pitch + rhythm to generate complete melodies
- Add genre- and mood-specific models for variation

## Major Components
**1. Data & Preprocessing**
- Collect MIDI files
- Parse into pitch and duration sequences
- Clean and organize data into genre/mood directories.
- `parse_midi.py`, `preprocess.py`, `mood_data_pipeline.py`

**2. Core Markov Models**
- 1st-order model (baseline)
- 2nd-order model (better context)
- Separate pitch and rhythm models.
- `markov.py`

**3. Generation**
- Sample from trained models
- Combine pitch + rhythm
- Output as MIDI files
- `generate.py`, `pipeline.py`

**4. Evaluation & Documentation**
- Generate sample outputs
- Compare different approaches (metrics + listening)
- `evaluate.py`, `evaluate.ipynb`