from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = 'invoice'

    id = Column(Integer, primary_key=True)
    product_no = Column(String, nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)

def preprocess_image(img_path):
    img = Image.open(img_path)
    img = img.convert('L') 
    img = img.filter(ImageFilter.SHARPEN) 
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2) 
    return img

def parse_row(row_text):
    parts = row_text.strip().split()
    if len(parts) < 5 or not parts[0].isdigit():
        return None
    try:
        product_no = parts[0]

     
        line_total = parts[-1]

      
        unit_price = parts[-2]
        quantity = parts[-3]

        description = " ".join(parts[1:-3])

        return (product_no, description, quantity, unit_price, line_total)
    except Exception as e:
        print(f"Failed to parse row: {row_text}. Error: {e}")
        return None

def process_invoice(img_path, db_url):
    img = preprocess_image(img_path)

    text = pytesseract.image_to_string(img)

    print("--- OCR Output ---")
    print(text)

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    rows = text.split('\n')
    for row in rows:
        parsed_data = parse_row(row)
        if parsed_data:
            product_no, description, quantity, unit_price, line_total = parsed_data
            try:
                product = Product(
                    product_no=product_no,
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total
                )
                session.add(product) 

            except Exception as e:
                print(f"Error: {e}")
                session.rollback()  

    try:
        session.commit()  
        print("Invoice processed and data saved successfully.")
    except Exception as e:
        print(f"Error committing data: {e}")
        session.rollback()

img_path = "pdf/wholesale-produce-distributor-invoice.webp"
db_url = "mysql+pymysql://root:@localhost:3306/convertdata" 

process_invoice(img_path, db_url)
