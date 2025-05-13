import pytesseract
from pdf2image import convert_from_path
import pdfplumber
import os
import csv
import mysql.connector
import sys

# ===== CONFIG =====
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Ubah jika perlu
PDF_FOLDER = 'samples'
OUTPUT_FOLDER = 'outputs'

# MySQL Configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'convertdata'

# ===== Step 1: Convert PDF ke text =====
def pdf_to_text(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                print(f"📄 Halaman {page_number} kosong, menggunakan OCR...")
                img = page.to_image(resolution=300).original
                text = pytesseract.image_to_string(img)
            full_text += text + "\n"
    return full_text

# ===== Step 2: Parsing text ke rows =====
def parse_text_to_rows(text):
    rows = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        columns = [col.strip() for col in line.split('  ') if col.strip()]
        if len(columns) >= 5:
            rows.append(columns[:5])
    return rows

# ===== Step 3: Simpan CSV =====
def save_rows_to_csv(rows, csv_file):
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Product', 'Description', 'Quantity', 'Unit Price', 'Line Total'])
        writer.writerows(rows)

# ===== Step 4: Masukkan CSV ke MySQL =====
def insert_csv_to_mysql(csv_file):
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS invoice (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product TEXT,
            description TEXT,
            quantity TEXT,
            unit_price TEXT,
            line_total TEXT
        )
    ''')

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) < 5:
                row += [''] * (5 - len(row))
            cur.execute('''
                INSERT INTO invoice (product, description, quantity, unit_price, line_total)
                VALUES (%s, %s, %s, %s, %s)
            ''', row[:5])

    conn.commit()
    cur.close()
    conn.close()

# ===== Main Entry Point =====
def main(filename):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    if not filename.lower().endswith('.pdf'):
        print("❌ File bukan PDF")
        return

    pdf_path = os.path.join(PDF_FOLDER, filename)
    if not os.path.exists(pdf_path):
        print(f"❌ File {pdf_path} tidak ditemukan.")
        return

    print(f"🔍 Memproses {filename}...")
    text = pdf_to_text(pdf_path)
    rows = parse_text_to_rows(text)

    output_csv = os.path.join(OUTPUT_FOLDER, filename.replace('.pdf', '.csv'))
    save_rows_to_csv(rows, output_csv)
    print(f"✅ Berhasil disimpan ke: {output_csv}")

# ===== Saat dipanggil langsung =====
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ Harap sertakan nama file PDF sebagai argumen.")
    else:
        main(sys.argv[1])
