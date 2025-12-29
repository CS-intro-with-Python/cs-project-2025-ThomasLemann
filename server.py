from flask import Flask, request, render_template, redirect, url_for
import os
import base64
from datetime import datetime

app = Flask(__name__)

DRAWINGS_FOLDER = 'static/drawings'
os.makedirs(DRAWINGS_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def hello():
    return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    return render_template('login.html', email=email, password=password)

@app.route('/note', methods=['GET', 'POST'])
@app.route('/note/<filename>', methods=['GET', 'POST'])
def note(filename=None):
    text_note = ''
    image_data = None

    if request.method == 'POST':
        data_url = request.form.get('imageData')
        text_note = request.form.get('textNote', '')
        original_filename = request.form.get('originalFilename')

        if data_url:
            header, encoded = data_url.split(",", 1)
            data = base64.b64decode(encoded)
            if original_filename:
                filepath = os.path.join(DRAWINGS_FOLDER, original_filename)
            else:
                filepath = os.path.join(DRAWINGS_FOLDER, datetime.now().strftime("%Y%m%d%H%M%S") + ".png")

            with open(filepath, "wb") as f:
                f.write(data)

            text_path = filepath + ".txt"
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text_note)

        return redirect(url_for('note'))

    if filename:
        filepath = os.path.join(DRAWINGS_FOLDER, filename)
        text_path = filepath + ".txt"
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                image_data = f"data:image/png;base64,{encoded}"
        if os.path.exists(text_path):
            with open(text_path, "r", encoding="utf-8") as f:
                text_note = f.read()

    return render_template('note.html',
                           images=None,
                           image_data=image_data,
                           original_filename=filename,
                           text_note=text_note)

@app.route('/all_notes', methods=['GET'])
def all_notes():
    images = sorted(os.listdir(DRAWINGS_FOLDER))
    notes = []
    for img in images:
        if img.endswith(".png"):
            img_path = f"/static/drawings/{img}"
            text_file = os.path.join(DRAWINGS_FOLDER, img + ".txt")
            text_content = ""
            if os.path.exists(text_file):
                with open(text_file, "r", encoding="utf-8") as f:
                    text_content = f.read()
            notes.append({'img': img_path, 'text': text_content, 'filename': img})
    return render_template('all_notes.html', notes=notes)

@app.route('/delete_note', methods=['POST'])
def delete_note():
    filename = request.form.get('filename')
    if filename:
        filepath = os.path.join(DRAWINGS_FOLDER, filename)
        textpath = filepath + ".txt"
        if os.path.exists(filepath):
            os.remove(filepath)
        if os.path.exists(textpath):
            os.remove(textpath)
    return redirect(url_for('note'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)