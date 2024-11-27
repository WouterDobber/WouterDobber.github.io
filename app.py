import speech_recognition as sr
import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from pydub import AudioSegment
import requests

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DEEPGRAM_API_KEY = "84fe12f84c6c00279f12bda538775e7e4900d7f8"  # Replace with your Deepgram API key

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

    # Send the audio to the Deepgram API for transcription with punctuation
    try:
        with open(audio_path, "rb") as audio_file:
            headers = {
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            }
            response = requests.post(
                "https://api.deepgram.com/v1/listen?punctuate=true",
                headers=headers,
                data=audio_file
            )
            
            if response.status_code != 200:
                print(f"Error from Deepgram API: {response.status_code} {response.text}")
                return jsonify({"message": "Error from Deepgram API."}), 500
            
            transcription_result = response.json()
            transcription_text = transcription_result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
            
            print(f"Transcription with punctuation: {transcription_text}")
            return jsonify({"message": "File saved and transcribed.", "transcription": transcription_text})
    
    except Exception as e:
        print(f"Error processing audio file with Deepgram API: {e}")
        return jsonify({"message": "Error processing audio file."}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
