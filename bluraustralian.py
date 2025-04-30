import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
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

def preprocess_image(image_path):
    try:
        image = Image.open(image_path).convert("L")
        image = image.filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        return image
    except Exception as e:
        print(f"Error membuka atau memproses gambar: {e}")
        return None

def extract_table_from_image(image_path):
    image = preprocess_image(image_path)
    if image is None:
        return

    text = pytesseract.image_to_string(image)

    lines = text.split('\n')
    for line in lines:
       
        columns = [col.strip() for col in line.split() if col.strip()]
        
        if len(columns) >= 6:
            try:
                taxable = columns[0]
                description = ' '.join(columns[1:-4])
                quantity = int(clean_number(columns[-4]))
                unit_price = float(clean_number(columns[-3]))
                discount = float(clean_number(columns[-2]))
                line_total = float(clean_number(columns[-1]))

                product = ProductTable(
                    taxable=taxable,
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount=discount,
                    line_total=line_total
                )
                session.add(product)
                session.commit()
                print(f"✔ Disimpan: {taxable}, {description}, {quantity}, {unit_price}, {discount}, {line_total}")
            except Exception as e:
                print(f"❌ Gagal memproses baris: {columns} - {e}")
        else:
            print(f"❗ Baris diabaikan (tidak cukup kolom): {line}")

    print("✅ Proses selesai.")

extract_table_from_image("pdf/blurry_australiantaxinvoicetemplate.webp")
