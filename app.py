from flask import Flask, send_file, request, jsonify, send_from_directory, abort
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import anthropic
from dotenv import load_dotenv
import base64
import json

load_dotenv()
client = anthropic.Anthropic()

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
        img = Image.open(file)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        #img = ImageOps.fit(img, MAX_SIZE, Image.Resampling.LANCZOS)
        img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)

        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(path, 'PNG', optimize=True)

        return jsonify({'url': f"/cache/{filename}"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_image():
    data = request.get_json()
    if not data or 'filename' not in data or 'message' not in data:
        return jsonify({'error': 'Missing filename or message in request'}), 400

    filename = data['filename']
    message = data['message']

    # Verify image exists and is valid
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Image not found'}), 404

    try:
        with Image.open(file_path) as img:
            width, height = img.size
            with open(file_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        response = client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=[{
                "type": "computer_20241022",
                "name": "computer",
                "display_width_px": width,
                "display_height_px": height
            }],
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"You only have the computer tool available, and the only supported action is mouse_move, please interpret the user's message as a request to move the mouse to the position they are indicating. Provide any other helpful answer in your text response as well.\n\nHere's the user's request: {message}"
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64_image
                        }
                    }
                ]
            }],
            betas=["computer-use-2024-10-22"]
        )
        print(response.to_json())
        return jsonify(json.loads(response.to_json())), 200

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/cache/<filename>')
def serve_image(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        abort(404)

@app.route('/')
def serve_index():
    return send_file('./index.html')

@app.route('/favicon.ico')
def serve_favicon():
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=8008)