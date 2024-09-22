from flask import Flask, request, redirect, jsonify, flash
import os
import whisper

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = "secret_key"  # Needed for flashing messages

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Load Whisper model
model = whisper.load_model("base")  # You can use "tiny", "small", "medium", "large" based on your needs

# Route to render the file upload form
@app.route('/')
def index():
    return '''
        <h1>Upload Audio File for Transcription</h1>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="file" name="audio_file">
            <input type="submit" value="Upload">
        </form>
    '''

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    audio_file = request.files['audio_file']
    
    if audio_file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if audio_file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
        audio_file.save(file_path)
        flash('File successfully uploaded')
        return jsonify({
            "message": "File uploaded successfully",
            "file_path": file_path
        })

# Route to handle transcription with Whisper
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    data = request.get_json()  # Expect the file path to be sent via JSON
    file_path = data.get("file_path")
    
    if not file_path:
        return jsonify({"error": "File path is required for transcription"}), 400
    
    # Use Whisper model to transcribe the audio
    try:
        result = model.transcribe(file_path)
        transcription = result['text']
        return jsonify({
            "message": "Transcription complete",
            "transcription": transcription
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
