import pytesseract
from pytesseract import Output

def extract_text_from_image(image):
    """
    Menggunakan pytesseract untuk ekstrak teks dan posisi dari gambar.
    """
    data = pytesseract.image_to_data(image, output_type=Output.DICT)
    return data
