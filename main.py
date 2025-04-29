import pytesseract
from pdf2image import convert_from_path
import pdfplumber
from PIL import Image
import mysql.connector
import os
import io
import csv
 
# ===== CONFIG =====
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows users only
PDF_FOLDER = 'samples'
OUTPUT_FOLDER = 'outputs'
 
# MySQL Configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''  # Ganti dengan password MySQL Anda
DB_NAME = 'convertdata'
 
# ===== STEP 1: Convert PDF to Text =====
def pdf_to_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            if page.width and page.height:
                text = page.extract_text()
                if not text:
                    print(f"Tidak ada teks, menggunakan OCR untuk halaman: {page_number}")
                    with io.BytesIO(page.to_image(resolution=300).original_image) as image_bytes:
                        image = Image.open(image_bytes)
                        text = pytesseract.image_to_string(image)
 
                    row = text.split("\n")
                    parsed_row = parse_table(row)
                    for parsed_row in parsed_row:
                        text = pytesseract.image_to_string(page, lang='eng')  # atau 'ind' untuk bahasa Indonesia
                        full_text += text + "\n"
                    return full_text
 
# ===== STEP 2: Clean and Parse Data =====
def parse_text_to_rows(text):
    # Ini contoh sederhana: parsing text menjadi list per baris
    rows = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            # Anggap setiap baris data dipisah spasi
            rows.append(line.split())
    return rows
 
# ===== STEP 3: Save to CSV =====
def save_rows_to_csv(rows, csv_file):
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
 
# ===== STEP 4: Insert CSV Data into MySQL =====
def insert_csv_to_mysql(csv_file):
    # Koneksi ke MySQL
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cur = conn.cursor()
 
    # Buat database dan tabel jika belum ada
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cur.execute(f"USE {DB_NAME}")
    cur.execute('''
    CREATE TABLE IF NOT EXISTS extracted_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product TEXT,
        description TEXT,
        quantity TEXT,
        unit_price TEXT,
        line_total TEXT
    )
    ''')
 
    # Baca data dari CSV dan masukkan ke tabel
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            # Sesuaikan jumlah kolom sesuai struktur database
            cur.execute('''
                INSERT INTO extracted_data (product, description, quantity, unit_price, line_total)
                VALUES (%s, %s, %s, %s, %s)
            ''', (row + [''] * 5)[:5])  # Pastikan pas 5 kolom
 
    conn.commit()
    cur.close()
    conn.close()
 
# ===== Main Execution =====
def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
 
    for pdf_file in os.listdir(PDF_FOLDER):
        if pdf_file.endswith('.pdf'):
            print(f"Processing {pdf_file}...")
            text = pdf_to_text(os.path.join(PDF_FOLDER, pdf_file))
            rows = parse_text_to_rows(text)
 
            # Simpan ke CSV
            output_csv = os.path.join(OUTPUT_FOLDER, pdf_file.replace('.pdf', '.csv'))
            save_rows_to_csv(rows, output_csv)
 
            # Insert ke MySQL
            insert_csv_to_mysql(output_csv)
 
    print("✅ Semua PDF selesai diproses!")
 
if __name__ == "__main__":
    main()