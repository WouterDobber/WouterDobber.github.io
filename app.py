from flask import Flask, request, jsonify
import os
import speech_recognition as sr
import soundfile as sf
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = '/opt/render/project/src/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return "No audio file uploaded!", 400

    audio_file = request.files['audio']
    file_path = os.path.join(UPLOAD_FOLDER, "recording.wav")
    
    # Save the uploaded file
    audio_file.save(file_path)

    # Process the audio file
    recognizer = sr.Recognizer()
    try:
        # Try to convert the file to a supported format
        data, samplerate = sf.read(file_path)
        
        # Convert to mono if stereo
        if len(data.shape) > 1:
            data = data.mean(axis=1)
        
        # Normalize audio
        data = data / np.max(np.abs(data))
        
        # Save as WAV 
        sf.write(file_path, data, samplerate)

        # Now try speech recognition
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print(text)
            return text
    except Exception as e:
        print(f"Error processing audio: {e}")
        return f"Could not process audio file: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
