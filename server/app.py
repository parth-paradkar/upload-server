from flask import Flask, request
from werkzeug.utils import secure_filename
import os
from .upload import UploadAdmin

app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'uploads'
app.debug = True

BASE_PATH = './tmp/'
admin = None

@app.route('/upload', methods=['POST'])
def upload():
    print(request.headers)
    global admin
    uploaded_file = request.files['file']
    if uploaded_file.filename:
        admin = UploadAdmin(
            BASE_PATH, 
            uploaded_file.stream, 
            uploaded_file.filename
        )
        admin.start()
        return "OK", 200
        

@app.route('/upload/pause', methods=['GET'])
def pause_upload():
    if(admin):
        admin.pause()
        return "OK", 200
    return "NO_FILE", 400

@app.route('/upload/resume', methods=['GET'])
def resume_upload():
    if(admin):
        admin.resume()
        return "OK", 200
    return "NO_FILE", 400

@app.route('/upload/terminate', methods=['GET'])
def terminate_upload():
    if(admin):
        admin.terminate()
        return "OK", 200
    return "NO_FILE", 400

@app.route('/upload/stop', methods=['GET'])
def stop_upload():
    if(admin):
        admin.stop()
        return "OK", 200
    return "NO_FILE", 400

@app.route('/upload/status', methods=['GET'])
def status():
    if(admin):
        return admin.status()
    else:
        return "No upload in progress"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)