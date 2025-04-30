import pdfplumber
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "mysql+pymysql://root:@localhost/convertdata"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class ProductTable(Base):
    __tablename__ = 'australiann'
    id = Column(Integer, primary_key=True, autoincrement=True)
    taxable = Column(String(50))
    description = Column(String(255))
    quantity = Column(Integer)
    unit_price = Column(Float)
    discount = Column(Float)
    line_total = Column(Float)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def clean_number(text):
    return text.replace(' ', '').replace(',', '').replace('%', '').strip()

def extract_table_from_pdf(pdf_path):
    if not pdf_path.endswith('.pdf'):
        print(f"File bukan PDF : {pdf_path}")
        return

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()

            if not table:
                print(f"Tidak ada teks di halaman: {page.page_number}, tidak ada tabel yang ditemukan.")
                continue

            if table:

                for row in table[1:]:
                    if all(row):
                        try:
                            taxable = row[0]
                            description = row[1]
                            quantity = int(clean_number(row[2]))
                            unit_price = float(clean_number(row[3]))
                            discount = float(clean_number(row[4]))
                            line_total = float(clean_number(row[5]))

                            product = ProductTable(
                                taxable=row[0],
                                description=row[1],
                                quantity=quantity,
                                unit_price=unit_price,
                                discount=discount,   
                                line_total=line_total  
                            )
                            session.add(product)
                            session.commit()

                            print(f"Baris berhasil disimpan: {taxable}, {description}, {quantity}, {unit_price}, {line_total}")
                        except Exception as e:
                            print(f"Error processing row {row}: {e}")

    print("Proses Selesai.")

extract_table_from_pdf("pdf/nonblurry_australiantaxinvoicetemplate.pdf")