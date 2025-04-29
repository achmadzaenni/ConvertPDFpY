import re
import pdfplumber
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Konfigurasi database
DATABASE_URL = "mysql+pymysql://root:@localhost/convertdata"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Model database
class ProductTable(Base):
    __tablename__ = 'australiann'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_no = Column(String(50))
    description = Column(String(255))
    quantity = Column(Integer)
    unit_price = Column(Float)
    discount = Column(Float)
    line_total = Column(Float)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Parsing nilai
def parse_value(value, value_type, default=None):
    try:
        if value is None or value == "":
            return default
        if value_type == int:
            return int(float(value.replace(",", "").strip()))
        elif value_type == float:
            return float(value.replace(",", "").strip())
        elif value_type == str:
            return value.strip()
    except (ValueError, AttributeError):
        return default

def parse_row(row_text):
    parts = row_text.strip().split()
    
    if len(parts) < 6:
        return None

    # Misah dari belakang
    product_no = parts[0]
    quantity = parts[-4]
    unit_price = parts[-3]
    discount = parts[-2].replace("%", "")  # hapus tanda % kalau ada
    line_total = parts[-1]

    description = " ".join(parts[1:-4])

    # Tambahkan "p" jika belum ada
    if not product_no.startswith('p'):
        product_no = f"p{product_no}"

    return (product_no, description, quantity, unit_price, discount, line_total)


# Fungsi ekstrak tabel dari PDF
def extract_table_from_pdf(pdf_path):
    if not pdf_path.endswith('.pdf'):
        print(f"File bukan PDF: {pdf_path}")
        return

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                print(f"Tidak ada teks di halaman: {page_number}")
                continue

            rows = text.split("\n")
            for row in rows:
                parsed_row = parse_row(row)
                if not parsed_row:
                    continue

                product_no, description, quantity, unit_price, discount, line_total = parsed_row

                product = ProductTable(
                    product_no=parse_value(product_no, str),
                    description=parse_value(description, str),
                    quantity=parse_value(quantity, int),
                    unit_price=parse_value(unit_price, float),
                    discount=parse_value(discount, float),
                    line_total=parse_value(line_total, float),
                )

                session.add(product)
                session.commit()
                print(f"Disimpan: {product_no}, {description}, {quantity}, {unit_price}, {discount}, {line_total}")

    print("✅ Data selesai ditambahkan ke database.")

# Jalankan
extract_table_from_pdf("pdf/nonblurry_australiantaxinvoicetemplate.pdf")
