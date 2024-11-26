import os
from flask import Flask, request, render_template
from flask_cors import CORS
import speech_recognition as sr

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
    
    audio_file = request.files['audio']
    file_path = os.path.join(UPLOAD_FOLDER, "recording.wav")
    audio_file.save(file_path)

    # Process the audio file
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print(text)
            return text
    except sr.UnknownValueError:
        return "Speech could not be understood!"
    except sr.RequestError as e:
        return f"Could not request results; {e}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
