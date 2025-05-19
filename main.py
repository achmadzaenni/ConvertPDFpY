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
TABLE_NAME = 'invoice'

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
    header = None
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        columns = [col.strip() for col in line.split(' ') if col.strip()]
        if not header:
            header = columns
        else:
            rows.append(columns)
    return header, rows

# ===== Step 3: Simpan CSV =====
def save_rows_to_csv(header, rows, csv_file):
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
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
    
    # Create table
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        create_table_query = f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} ("
        for col in header:
            create_table_query += f"{col} TEXT, "
        create_table_query = create_table_query[:-2] + ")"
        cur.execute(create_table_query)
        
        # Insert data
        insert_query = f"INSERT INTO {TABLE_NAME} ({', '.join(header)}) VALUES ({', '.join(['%s'] * len(header))})"
        for row in reader:
            cur.execute(insert_query, row)
    
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
    header, rows = parse_text_to_rows(text)
    output_csv = os.path.join(OUTPUT_FOLDER, filename.replace('.pdf', '.csv'))
    save_rows_to_csv(header, rows, output_csv)
    print(f"✅ Berhasil disimpan ke: {output_csv}")
    insert_csv_to_mysql(output_csv)

# ===== Saat dipanggil langsung =====
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ Harap sertakan nama file PDF sebagai argumen.")
    else:
        main(sys.argv[1])
