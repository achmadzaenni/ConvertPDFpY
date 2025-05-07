import pdfplumber
import pytesseract
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import declarative_base, sessionmaker
import re
import os
from PIL import Image

DATABASE_URL = "mysql+pymysql://root:@localhost/convertdata"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class ProductTable(Base):
    __tablename__ = 'invoice'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_no = Column(String(50))
    description = Column(String(255))
    quantity = Column(Integer)
    unit_price = Column(Float)
    line_total = Column(Float)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def parse_value(value, value_type, default=None):
    try:
        if value is None or value.strip() == "":
            return default
        if value_type == int:
            return int(value.replace(",", "").strip())
        elif value_type == float:
            return float(value.replace(",", "").strip())
        elif value_type == str:
            return value.strip()
    except (ValueError, AttributeError):
        return default

def parse_row(row_text):
    try:
        row_text = re.sub(r"[|[/~_}{)()(=]", " ", row_text)
        row_text = re.sub(r"\s+", " ", row_text).strip()
        parts = row_text.split()

        if len(parts) < 6:
            return None

        product_no = parts[0]

        # Baris produk di invoice terdiri dari:
        # Product No | Description (bisa multi kata) | Quantity | Unit Price | Line Total
        try:
            quantity = int(parts[-3])
            unit_price = float(parts[-2])
            line_total = float(parts[-1])
            description = " ".join(parts[1:-3])
        except ValueError:
            return None

        return (product_no, description, str(quantity), str(unit_price), str(line_total))
    except Exception as e:
        print(f"Kesalahan parsing baris: {row_text}. Error: {e}")
        return None
def extract_text_from_image(image_path):
    try:
        pil_image = Image.open(image_path)
        config = "--psm 6"
        return pytesseract.image_to_string(pil_image, config=config)
    except Exception as e:
        print(f"Kesalahan OCR pada gambar: {e}")
        return ""

def extract_text_with_ocr(page):
    try:
        page_image = page.to_image()
        pil_image = page_image.original
        config = "--psm 6"
        return pytesseract.image_to_string(pil_image, config=config)
    except Exception as e:
        print(f"Kesalahan OCR: {e}")
        return ""

def extract_table_from_pdf(pdf_path):

    if not os.path.exists(pdf_path):
        print(f"File tidak ditemukan: {pdf_path}")
        return

    if pdf_path.endswith('.pdf'):
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()

                if not text:
                    print(f"Halaman {page_number} menggunakan OCR karena tidak ada teks.")
                    text = extract_text_with_ocr(page)
                if not text:
                    print(f"Tidak ada teks di halaman {page_number}.")
                    continue

                rows = text.split("\n")
                process_row(rows)

    elif pdf_path.endswith(('.png','.jpg','.jpeg','.webp')):
        print(f"File berformat gambar : {pdf_path}")
        text = extract_text_from_image(pdf_path)

        if not text:
            print(f"TIdak ada teks yang diekstrak dari gambar {pdf_path}")
            return
        
        rows = text.split("\n")
        print(f" input {rows}")
        process_row(rows)

    else:
        print(f"format file tidak didukung: {pdf_path}")

def process_row(rows):
            
    for row in rows:
        parsed_row = parse_row(row)
        print(f"Parsed row: {parsed_row}")

        if not parsed_row:
            print(f"Baris tidak valid: {row}")
            continue
                    
        try:
            product_no, description, quantity, unit_price, line_total = parsed_row
         
            if not all([product_no, description, quantity, unit_price, line_total]):
                print(f"Data tidak lengkap: {row}")
                continue

            if not (product_no.isdigit() and len(product_no) == 5):
                print(f"Nomor produk tidak valid: {product_no}")
                continue

            product = ProductTable(
                        product_no=parse_value(product_no, str),
                        description=parse_value(description, str),
                        quantity=parse_value(quantity, int),
                        unit_price=parse_value(unit_price, float),
                        line_total=parse_value(line_total, float),
                    )
            session.add(product)
            session.commit()
        except Exception as e:
            print(f"Kesalahan saat menyimpan ke database: {e}")
            session.rollback()
            continue

extract_table_from_pdf("pdf/wholesale-produce-distributor-invoice.webp")