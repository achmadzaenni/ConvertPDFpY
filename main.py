def clean_text_data(raw_data):
    """
    Mengolah raw_data hasil OCR dan mengonversinya ke struktur data yang sesuai untuk disimpan ke dalam database.
    """
    data = []
    
    
    lines = raw_data.splitlines()
    
    for line in lines:
        if line.strip():  # Menghindari baris kosong
            columns = line.split()
            
            # Pastikan setiap baris memiliki cukup data
            if len(columns) >= 5:
                data.append({
                    'ProductNumber': columns[0],  # Nomor Produk
                    'Description': " ".join(columns[1:-3]),  # Deskripsi produk (mungkin lebih dari satu kata)
                    'Quantity': columns[-3],  # Kuantitas
                    'UnitPrice': columns[-2],  # Harga satuan
                    'LineTotal': columns[-1]  # Total per baris
                })
    return data
