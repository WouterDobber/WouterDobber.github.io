import os

from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    print("TEST" + app.root_path)
    return render_template("index.html")

@app.route('/record', methods=['POST'])
def record():
    print("Button was pressed!")
    return "Success"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)