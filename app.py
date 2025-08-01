from flask import Flask, request, jsonify, render_template
from PIL import Image
import pytesseract
import os
import re

app = Flask(__name__)

# Uploads Folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if 'DYNO' in os.environ:
    pytesseract.pytesseract.tesseract_cmd = "/app/.apt/usr/bin/tesseract"
    os.environ["TESSDATA_PREFIX"] = "/app/.apt/usr/share/tesseract-ocr/4.00/"
else:
    # Local (Windows or others): Use bundled or system-installed path
    pytesseract.pytesseract.tesseract_cmd = os.path.join(os.getcwd(), "tesseract", "tesseract.exe")
    os.environ["TESSDATA_PREFIX"] = os.path.join(os.getcwd(), "tesseract", "tessdata")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'}), 400

        # ✅ Save image first
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        print(f"Tesseract path: {pytesseract.pytesseract.tesseract_cmd}")
        print(f"TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX')}")

        # ✅ Open and preprocess image
        img = Image.open(filepath).convert('L')
        img = img.point(lambda x: 0 if x < 140 else 255)

        # ✅ Run OCR
        raw_text = pytesseract.image_to_string(img, lang='eng')

        # ✅ Clean output with regex (optional)
        cleaned_lines = []
        for line in raw_text.splitlines():
            cleaned_line = re.sub(r'[^\w\s\[\](){}<>\\/.,!?\'"-]', '', line)
            cleaned_lines.append(cleaned_line.strip())
        cleaned_text = '\n'.join([line for line in cleaned_lines if line])

        os.remove(filepath)  # delete temp image
        return jsonify({'success': True, 'text': cleaned_text})

    except Exception as e:
        print("❌ OCR FAILED:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


