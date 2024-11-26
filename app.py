import os
import wave
import threading
import numpy as np
import sounddevice as sd

from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Audio recording variables
RATE = 44100  # Sample rate
CHANNELS = 1  # Mono
CHUNK = 1024
RECORD_SECONDS = 10
recording = False
frames = []
record_thread = None

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/start-record', methods=['POST'])
def start_record():
    global recording, frames, record_thread

    if recording:
        return "Already recording!"

    # Clear previous frames
    frames = []
    recording = True

    # Start recording in a separate thread
    def record_audio():
        global frames, recording
        while recording:
            data = sd.rec(CHUNK, samplerate=RATE, channels=CHANNELS, dtype='int16')
            sd.wait()  # Wait for the buffer to fill
            frames.append(data)

    record_thread = threading.Thread(target=record_audio)
    record_thread.start()
    return "Recording started"


@app.route('/stop-record', methods=['POST'])
def stop_record():
    global recording, record_thread

    if not recording:
        return "Not recording!"

    # Stop recording
    recording = False
    record_thread.join()

    # Save frames to a WAV file
    output_file = os.path.join(app.root_path, 'recording.wav')
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 2 bytes for 'int16'
        wf.setframerate(RATE)
        wf.writeframes(b''.join(np.array(frames).flatten()))
    
    return f"Recording saved to {output_file}"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
