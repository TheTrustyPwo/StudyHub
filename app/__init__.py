import os
from flask import Flask
from flask_cors import CORS

# Initialize application
app = Flask(__name__, static_folder=None)

# Enabling cors
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
