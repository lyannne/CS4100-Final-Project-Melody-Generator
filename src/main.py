import pickle
from preprocess import preprocess_midis
from markov import train_first_order, train_second_order
from generate import generate_first_order, generate_second_order

def main():
    print("="*50)
    print("MIDI Markov Model Pipeline")
    print("="*50)
    
    print("\n[1/4] Preprocessing MIDI files...")
    pitches, durations = preprocess_midis(
        input_dir='data/raw/nes',
        output_file='data/processed/preprocessed_nes.pkl',
        chord_strategy='highest'
    )
    
    # Step 2: Train pitch models
    print("\n[2/4] Training pitch models...")
    pitch_model_1, pitch_start_1 = train_first_order(
        pitches, 
        save_to_file='models/pitch_first_order.pkl'
    )
    pitch_model_2, pitch_start_2 = train_second_order(
        pitches,
        save_to_file='models/pitch_second_order.pkl'
    )
    print(f"  First-order pitch states: {len(pitch_model_1)}")
    print(f"  Second-order pitch states: {len(pitch_model_2)}")
    
    # Step 3: Train duration models
    print("\n[3/4] Training duration models...")
    duration_model_1, duration_start_1 = train_first_order(
        durations,
        save_to_file='models/duration_first_order.pkl'
    )
    duration_model_2, duration_start_2 = train_second_order(
        durations,
        save_to_file='models/duration_second_order.pkl'
    )
    print(f"  First-order duration states: {len(duration_model_1)}")
    print(f"  Second-order duration states: {len(duration_model_2)}")
    
    # Step 4: Generate sample outputs
    print("\n[4/4] Generating sample MIDIs...")
    
    # First-order generation
    generate_first_order(
        length=30,  # 30 seconds
        BPM=120,
        pitch_model=pitch_model_1,
        starting_pitch_dist=pitch_start_1,
        duration_model=duration_model_1,
        starting_duration_dist=duration_start_1,
        save_path='outputs/first_order_sample.mid'
    )
    print("  Generated: outputs/first_order_sample.mid")
    
    # Second-order generation
    generate_second_order(
        length=30,
        BPM=120,
        pitch_model=pitch_model_2,
        starting_pitch_dist=pitch_start_2,
        duration_model=duration_model_2,
        starting_duration_dist=duration_start_2,
        save_path='outputs/second_order_sample.mid'
    )
    print("  Generated: outputs/second_order_sample.mid")
    
    print("\n" + "="*50)
    print("Pipeline complete!")
    print("="*50)

if __name__ == "__main__":
    main()