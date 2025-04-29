import pytesseract
import pandas as pd
from PIL import Image
import os

# Pastikan path Tesseract sesuai instalasi kamu
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_with_positions(image_path):
    image = Image.open(image_path)

    # Ambil data posisi per kata
    ocr_result = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
    ocr_result = ocr_result.dropna()

    # Hapus spasi aneh, normalisasi text
    ocr_result['text'] = ocr_result['text'].str.strip().str.lower()

    # Simpan list hasil
    rows = []

    current_row = {'product_no': '', 'description': '', 'quantity': '', 'unit_price': '', 'line_total': ''}

    for idx, row in ocr_result.iterrows():
        word = row['text']

        if word.startswith('product') or word.startswith('#') or word.startswith('no'):
            continue  # Ini header, skip

        if word.replace('.', '', 1).isdigit():  # kalau angka
            if current_row['quantity'] == '':
                current_row['quantity'] = word
            elif current_row['unit_price'] == '':
                current_row['unit_price'] = word
            elif current_row['line_total'] == '':
                current_row['line_total'] = word
        else:
            # selain angka, anggap bagian dari description atau product_no
            if current_row['product_no'] == '':
                current_row['product_no'] = word
            else:
                current_row['description'] += ' ' + word

        # Kalau semua kolom sudah terisi, simpan row
        if all(current_row.values()):
            rows.append(current_row)
            current_row = {'product_no': '', 'description': '', 'quantity': '', 'unit_price': '', 'line_total': ''}

    df = pd.DataFrame(rows)

    # Final cleaning
    df['description'] = df['description'].str.strip().str.capitalize()

    return df
