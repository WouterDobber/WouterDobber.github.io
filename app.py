import speech_recognition as sr
import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from pydub import AudioSegment
from transformers import pipeline

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Hugging Face punctuation restoration model
punctuation_model = pipeline("text2text-generation", model="oliverguhr/fullstop-punctuation-multilang-large")


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    if 'audio' not in request.files:
        return "No audio file uploaded!", 400
    
    audio = request.files['audio']
    original_audio_path = os.path.join(UPLOAD_FOLDER, "recording_original")
    audio.save(original_audio_path)

    # Convert the uploaded audio file to WAV format
    try:
        audio_segment = AudioSegment.from_file(original_audio_path)
        audio_path = os.path.join(UPLOAD_FOLDER, "recording.wav")
        audio_segment.export(audio_path, format="wav")
    except Exception as e:
        print(f"Error converting audio file: {e}")
        return jsonify({"message": "Error converting audio file."}), 400

    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    # Load the audio file
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            
            # Transcribe the audio to text
            text = recognizer.recognize_google(audio_data, language="en-US", show_all=False)
            print(f"Transcription: {text}")
            
            # Add punctuation to the transcription
            def add_punctuation(transcription):
                result = punctuation_model(transcription, max_length=512)
                return result[0]["generated_text"]

            punctuated_text = add_punctuation(text)
            return jsonify({"message": "File saved and transcribed.", "transcription": punctuated_text})
    except sr.UnknownValueError:
        print("Could not understand the audio.")
        return jsonify({"message": "Could not understand the audio."}), 400
    except sr.RequestError:
        print("Could not request results from the recognition service.")
        return jsonify({"message": "Recognition service error."}), 500
    except Exception as e:
        print(f"Error processing audio file: {e}")
        return jsonify({"message": "Error processing audio file."}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use PORT from env or default to 5000
    app.run(debug=True, host='0.0.0.0', port=port)
