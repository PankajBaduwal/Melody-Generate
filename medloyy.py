import numpy as np
from music21 import stream, note
import streamlit as st
from tensorflow.keras.models import load_model

# Load your trained model (replace with your actual path)
model_path = r'C:\Users\PANKAJ BADUWAL\Desktop\melody generate\model(1).h5'
try:
    model = load_model(model_path)
except FileNotFoundError:
    raise FileNotFoundError(f"Model file not found at {model_path}")

# Example reverse mapping and seed data
reverse_mapping = {0: 'C4', 1: 'D4', 2: 'E4', 3: 'F4', 4: 'G4', 5: 'A4', 6: 'B4'}
X_seed = np.random.rand(10, 10, 1)  # Dummy seed data, replace with actual seed data

def chords_n_notes(music):
    """Convert a list of notes into a music21 stream."""
    melody_stream = stream.Stream()
    for n in music:
        melody_stream.append(note.Note(n))
    return melody_stream

def melody_generator(note_count):
    """Generate a melody with a specified number of notes."""
    seed = X_seed[np.random.randint(0, len(X_seed) - 1)]  # Select a random seed
    notes_generated = []  # List to store generated notes

    for _ in range(note_count):
        seed = seed.reshape(1, 10, 1)  # Reshape the seed for prediction
        prediction = model.predict(seed, verbose=0)[0]  # Predict next note
        prediction = np.log(prediction + 1e-7) / 1.0  # Adjust diversity
        exp_preds = np.exp(prediction)
        prediction = exp_preds / np.sum(exp_preds)  # Softmax

        # Sample from the prediction distribution
        index = np.random.choice(len(prediction), p=prediction)

        # Check if the index is in reverse_mapping
        if index not in reverse_mapping:
            print(f"Warning: Index {index} not found in reverse_mapping!")
            continue

        # Add the corresponding note to the notes_generated list
        notes_generated.append(reverse_mapping[index])

        # Update the seed for the next prediction
        seed = np.insert(seed[0], len(seed[0]), index / float(len(reverse_mapping)))
        seed = seed[1:]

    # Ensure 'music' is assigned before passing to chords_n_notes
    music = notes_generated  # 'music' is now assigned with the generated notes
    return chords_n_notes(music)

# Streamlit UI
st.title("Melody Generator")

# User input for the number of notes
note_count = st.slider("Number of notes to generate:", min_value=1, max_value=100, value=10)

if st.button("Generate Melody"):
    melody = melody_generator(note_count)
    
    # Save the generated melody to a MIDI file
    midi_file_path = 'generated_melody.mid'
    melody.write('midi', fp=midi_file_path)
    
    # Provide a link to download and play the MIDI file
    st.success("Melody generated successfully!")
    st.audio(midi_file_path)  # Play the generated MIDI file
    with open(midi_file_path, 'rb') as f:
        st.download_button('Download Melody', f, file_name='generated_melody.mid')
