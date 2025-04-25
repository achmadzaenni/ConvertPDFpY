import pandas as pd

def clean_text_data(ocr_data):
    """
    Membersihkan hasil OCR dan mengelompokkan teks ke dalam baris-baris tabel.
    """
    words = []
    for i in range(len(ocr_data['text'])):
        if int(ocr_data['conf'][i]) > 30 and ocr_data['text'][i].strip():
            words.append({
                'text': ocr_data['text'][i],
                'left': ocr_data['left'][i],
                'top': ocr_data['top'][i]
            })

    # Grouping berdasarkan baris (top/posisi Y)
    df = pd.DataFrame(words)
    df['line_group'] = pd.cut(df['top'], bins=20, labels=False)  # pengelompokan kasar per baris

    grouped = df.groupby('line_group').apply(lambda g: ' '.join(g.sort_values('left')['text']))
    return grouped.tolist()
