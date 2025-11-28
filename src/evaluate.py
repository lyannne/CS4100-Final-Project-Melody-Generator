import os
from music21 import converter
import statistics
import argparse
import matplotlib.pyplot as plt

def analyze_midi_file(filepath, collect_distributions=False):
    """Analyze a single MIDI file and return metrics."""
    score = converter.parse(filepath)
    
    pitches = []
    durations = []
    for note in score.flatten().notes:
        if note.isNote:
            pitches.append(note.pitch.midi)
            durations.append(note.quarterLength)
    
    if len(pitches) < 2:
        return None 
    
    metrics = {}
    
    intervals = [abs(pitches[i+1] - pitches[i]) for i in range(len(pitches) - 1)]
    signed_intervals = [pitches[i+1] - pitches[i] for i in range(len(pitches) - 1)]
    
    metrics['avg_interval'] = sum(intervals) / len(intervals)
    metrics['pitch_range'] = max(pitches) - min(pitches)
    
    repeats = sum(1 for i in range(len(pitches) - 1) if pitches[i] == pitches[i+1])
    metrics['repeat_rate'] = repeats / (len(pitches) - 1)
    
    bigrams = [(pitches[i], pitches[i+1]) for i in range(len(pitches) - 1)]
    unique_bigrams = len(set(bigrams))
    metrics['bigram_diversity'] = unique_bigrams / len(bigrams)
    
    metrics['max_interval'] = max(intervals)
    metrics['avg_duration'] = sum(durations) / len(durations)
    metrics['duration_variety'] = len(set(durations)) / len(durations)
    
    if collect_distributions:
        metrics['raw_pitches'] = pitches
        metrics['raw_durations'] = durations
        metrics['raw_intervals'] = signed_intervals
    
    return metrics

def analyze_directory(directory_path, make_plots=False, output_dir='.'):
    """Analyze all MIDI files in a directory."""
    all_metrics = {
        'avg_interval': [],
        'pitch_range': [],
        'repeat_rate': [],
        'bigram_diversity': [],
        'max_interval': [],
        'avg_duration': [],
        'duration_variety': []
    }
    
    all_pitches = []
    all_durations = []
    all_intervals = []
    
    for filename in os.listdir(directory_path):
        if filename.endswith('.mid') or filename.endswith('.midi'):
            filepath = os.path.join(directory_path, filename)
            
            try:
                metrics = analyze_midi_file(filepath, collect_distributions=make_plots)
                if metrics:
                    for key in all_metrics:
                        if key in metrics:
                            all_metrics[key].append(metrics[key])
                    
                    if make_plots:
                        all_pitches.extend(metrics['raw_pitches'])
                        all_durations.extend(metrics['raw_durations'])
                        all_intervals.extend(metrics['raw_intervals'])
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    print("\n=== RESULTS ===")
    print(f"Files analyzed: {len(all_metrics['avg_interval'])}")
    print(f"\nAverage interval size: {statistics.mean(all_metrics['avg_interval']):.2f} half-steps")
    print(f"Average pitch range: {statistics.mean(all_metrics['pitch_range']):.2f} half-steps")
    print(f"Average repeat rate: {statistics.mean(all_metrics['repeat_rate']):.3f}")
    print(f"Average bigram diversity: {statistics.mean(all_metrics['bigram_diversity']):.3f}")
    print(f"Average max interval jump: {statistics.mean(all_metrics['max_interval']):.2f} half-steps")
    print(f"Average duration: {statistics.mean(all_metrics['avg_duration']):.3f} quarter notes")
    print(f"Duration variety: {statistics.mean(all_metrics['duration_variety']):.3f}")
    
    if make_plots:
        all_pitches = [p for p in all_pitches if isinstance(p, (int, float))]
        all_durations = [d for d in all_durations if isinstance(d, (int, float)) and d > 0]
        all_intervals = [i for i in all_intervals if isinstance(i, (int, float))]

        # PITCH DISTRIBUTION
        plt.figure(figsize=(10, 4))
        plt.hist(all_pitches, bins=30, color='blue', edgecolor='black')
        plt.xlabel('MIDI Pitch')
        plt.ylabel('Frequency')
        plt.title('Pitch Distribution')
        plt.savefig(os.path.join(output_dir, 'pitch_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # DURATION DISTRIBUTION
        plt.figure(figsize=(10, 4))
        duration_bins = [i * 0.25 for i in range(21)]
        plt.hist(all_durations, bins=duration_bins, color='green', edgecolor='black')
        plt.xlabel('Duration (quarter notes)')
        plt.ylabel('Frequency')
        plt.title('Duration Distribution')
        plt.xlim(0, 5)
        plt.savefig(os.path.join(output_dir,'duration_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # INTERVAL DISTRIBUTION
        plt.figure(figsize=(10, 4))
        plt.hist(all_intervals, bins=range(-24, 25), color='red', edgecolor='black')
        plt.xlabel('Interval (half-steps)')
        plt.ylabel('Frequency')
        plt.title('Interval Distribution')
        plt.savefig(os.path.join(output_dir, 'interval_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print("\nSaved distribution plots: pitch_distribution.png, duration_distribution.png, interval_distribution.png")
    
    return all_metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate/analyze midi files."
    )

    parser.add_argument(
        "--dir", "-d",
        required=True,
        help="Directory of midi files to analyze"
    )

    parser.add_argument(
        "--make-plots", "-mp",
        action='store_true',
        help="Generate distribution plots"
    )

    args = parser.parse_args()

    model_name = os.path.basename(os.path.normpath(args.dir))
    
    eval_dir = os.path.join('evaluation', model_name)
    os.makedirs(eval_dir, exist_ok=True)

    metrics = analyze_directory(args.dir, make_plots=args.make_plots, output_dir=eval_dir)