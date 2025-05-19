from flask import Flask, request, redirect, url_for, render_template
import os
import subprocess
import csv
import logging

app = Flask(__name__, static_folder='templates')
UPLOAD_FOLDER = 'samples'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Mengecek ekstensi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return redirect(url_for('upload_file'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            logging.error('Tidak ada file yang diunggah!')
            return '❌ Tidak ada file yang diunggah!', 400
        file = request.files['pdf_file']
        if file.filename == '':
            logging.error('Tidak ada file yang dipilih!')
            return '❌ Tidak ada file yang dipilih!', 400
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            try:
                logging.info(f'Mengunggah file {filename}...')
                subprocess.run(["python", "main.py", filename], check=True)
                csv_filename = filename.replace('.pdf', '.csv')
                csv_path = os.path.join(app.config['OUTPUT_FOLDER'], csv_filename)
                logging.info(f'File CSV berhasil dibuat: {csv_path}')
                with open(csv_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    csv_data = list(reader)
                    logging.info(f'Data CSV: {csv_data}')
                return render_template('show_csv.html', csv_data=csv_data, csv_filename=csv_filename)
            except subprocess.CalledProcessError as e:
                logging.error(f'Terjadi kesalahan saat menjalankan main.py: {str(e)}')
                return f"❌ Terjadi kesalahan saat menjalankan main.py: {str(e)}", 500
    return render_template('upload.html')

@app.route('/send_to_mysql/<filename>', methods=['POST'])
def send_to_mysql(filename):
    from main import insert_csv_to_mysql
    csv_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    try:
        logging.info(f'Mengirim data {filename} ke MySQL...')
        insert_csv_to_mysql(csv_path)
        logging.info(f'Data {filename} berhasil dimasukkan ke MySQL!')
        return f'✅ Data dari {filename} berhasil dimasukkan ke MySQL!'
    except Exception as e:
        logging.error(f'Gagal mengirim data ke MySQL: {str(e)}')
        return f'❌ Gagal mengirim data ke MySQL: {str(e)}', 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(debug=True)
