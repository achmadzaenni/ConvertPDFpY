from flask import Flask, request, redirect, url_for, render_template
import os
import subprocess

app = Flask(__name__, static_folder='templates')


# Folder untuk menyimpan file yang diunggah
UPLOAD_FOLDER = 'samples'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Hanya menerima file dengan ekstensi PDF
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Memastikan ekstensi file yang diunggah valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return redirect(url_for('upload_file'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return 'Tidak ada file yang diunggah!', 400

        file = request.files['pdf_file']
        if file.filename == '':
            return 'Tidak ada file yang dipilih!', 400

        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            try:
                subprocess.run(["python", "main.py"], check=True)
                return f"File berhasil diunggah dan diproses: {file.filename}"
            except subprocess.CalledProcessError as e:
                return f"Terjadi kesalahan saat menjalankan main.py: {str(e)}", 500

    return render_template('upload.html')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
