from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set the Google Cloud credentials environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-key.json"


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

    # Transcribe using Google Cloud Speech-to-Text with punctuation enabled
    try:
        client = speech.SpeechClient()
        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()
        
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_automatic_punctuation=True
        )

        response = client.recognize(config=config, audio=audio)
        transcription = " ".join(result.alternatives[0].transcript for result in response.results)
        print(f"Transcription: {transcription}")
        return jsonify({"message": "File saved and transcribed.", "transcription": transcription})
    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({"message": "Error during transcription."}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
