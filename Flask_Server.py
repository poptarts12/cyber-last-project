import os
from flask import Flask, send_file

app = Flask(__name__)
os.chdir(os.path.dirname(__file__))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_video(path):
    # Serve the video file
    video_path = os.path.join('server data', 'rickroll.mp4')
    return send_file(video_path, mimetype='video/mp4')

def run_web_server():
    # Use the path to the certificate and key files directly
    cert_path = r'certificates\cert.pem'
    key_path = r'certificates\key.pem'
    app.run(host='0.0.0.0', port=443, ssl_context=(cert_path, key_path))

if __name__ == '__main__':
    run_web_server()
