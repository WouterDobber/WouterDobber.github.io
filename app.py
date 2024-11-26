import speech_recognition as sr
import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    if 'audio' not in request.files:
        return "No audio file uploaded!", 400
    
    audio = request.files['audio']
    audio_path = os.path.join(UPLOAD_FOLDER, "recording.wav")
    audio.save(audio_path)

    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    # Load the audio file
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        
        try:
            # Transcribe the audio to text
            text = recognizer.recognize_google(audio_data)
            print(f"Transcription: {text}")
            return jsonify({"message": "File saved and transcribed.", "transcription": text})
        except sr.UnknownValueError:
            print("Could not understand the audio.")
            return jsonify({"message": "Could not understand the audio."}), 400
        except sr.RequestError:
            print("Could not request results from the recognition service.")
            return jsonify({"message": "Recognition service error."}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
