import speech_recognition as sr
import os
import wave
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from pydub import AudioSegment
import requests


HF_API_URL = "https://api-inference.huggingface.co/models/oliverguhr/fullstop-punctuation-multilang-large"
HF_HEADERS = {"Authorization": "Bearer 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"}
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
            
            # Transcribe the audio to text with punctuation enabled
            text = recognizer.recognize_google(audio_data, language="en-US", show_all=False)
            print(f"Transcription: {text}")

            try:
                response = requests.post(
                    HF_API_URL,
                    headers=HF_HEADERS,
                    json={"inputs": text}
                )
                if response.status_code == 200:
                    punctuated_text = response.json().get("generated_text", text)
                    print(f"Punctuated Transcription: {punctuated_text}")
                else:
                    print(f"Error from Hugging Face API: {response.status_code}, {response.text}")
                    punctuated_text = text  # Fallback to unpunctuated text

            except Exception as api_error:
                print(f"Error calling Hugging Face API: {api_error}")
                punctuated_text = text  # Fallback to unpunctuated text

            
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
    app.run(debug=True, host='0.0.0.0', port=5000)
