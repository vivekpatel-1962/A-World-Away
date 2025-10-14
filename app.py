from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, 
            static_folder='frontend/static',
            template_folder='frontend/templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('frontend/static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
