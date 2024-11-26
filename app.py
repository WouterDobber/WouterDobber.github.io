import os
import wave
import threading
import pyaudio

from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Audio recording variables
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
frames = []
recording = False
audio = pyaudio.PyAudio()
stream = None
record_thread = None


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/start-record', methods=['POST'])
def start_record():
    global recording, stream, frames, record_thread

    if recording:
        return "Already recording!"

    # Initialize audio stream
    frames = []
    recording = True
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    # Start recording in a separate thread
    def record_audio():
        while recording:
            data = stream.read(CHUNK)
            frames.append(data)

    record_thread = threading.Thread(target=record_audio)
    record_thread.start()
    return "Recording started"


@app.route('/stop-record', methods=['POST'])
def stop_record():
    global recording, stream, record_thread

    if not recording:
        return "Not recording!"

    # Stop recording
    recording = False
    record_thread.join()  # Wait for thread to finish
    stream.stop_stream()
    stream.close()

    # Save audio to file
    output_file = os.path.join(app.root_path, 'recording.wav')
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return f"Recording saved to {output_file}"


if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        audio.terminate()
