import os
from flask import Flask, render_template
from flask_cors import CORS
from audiorecorder import AudioRecorder

app = Flask(__name__)
CORS(app)

recorder = None
output_file = os.path.join(app.root_path, 'recording.wav')


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/start-record', methods=['POST'])
def start_record():
    global recorder
    if recorder is not None and recorder.is_recording:
        return "Already recording!"

    # Start recording
    recorder = AudioRecorder(output_file)
    recorder.start_recording()
    return "Recording started"


@app.route('/stop-record', methods=['POST'])
def stop_record():
    global recorder
    if recorder is None or not recorder.is_recording:
        return "Not recording!"

    # Stop recording
    recorder.stop_recording()
    recorder = None
    return f"Recording saved to {output_file}"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
