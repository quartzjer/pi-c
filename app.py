from flask import Flask, send_file, request, jsonify, send_from_directory, abort
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'cache')
ALLOWED_EXTENSIONS = {'png'}
MAX_SIZE = (1024, 768)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def handle_upload():
    if 'image' not in request.files or not request.files['image'].filename:
        return jsonify({'error': 'No valid image provided'}), 400

    file = request.files['image']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PNG files allowed'}), 400

    try:
        # Dimensions check
        img = Image.open(file)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
        
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(path, 'PNG', optimize=True)
        
        return jsonify({'url': f"/cache/{filename}"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cache/<filename>')
def serve_image(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        abort(404)

@app.route('/')
def serve_index():
    return send_file('./index.html')

if __name__ == '__main__':
    app.run(debug=True)