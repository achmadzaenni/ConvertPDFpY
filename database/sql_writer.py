from sqlalchemy import create_engine, MetaData, Table
import pandas as pd

def insert_data_to_db(cleaned_data):
    """
    Menyimpan data yang sudah dibersihkan ke database, menambah kolom secara dinamis jika perlu.
    """
    # Pastikan cleaned_data berupa DataFrame
    if not isinstance(cleaned_data, pd.DataFrame):
        df = pd.DataFrame(cleaned_data)
    else:
        df = cleaned_data

    try:
        # Membuat koneksi ke database menggunakan SQLAlchemy
        engine = create_engine("mysql+pymysql://root:@localhost/convertdata")
        metadata = MetaData(bind=engine)
        metadata.reflect()

        # Cek apakah tabel extract_data sudah ada
        if 'extract_data' not in metadata.tables:
            print("[INFO] Tabel 'extract_data' belum ada, membuat tabel baru.")
            df.to_sql("extract_data", con=engine, if_exists="replace", index=False)
        else:
         
            table = metadata.tables['extract_data']
            existing_columns = [col.name for col in table.columns]

            # Menambahkan kolom baru jika belum ada
            new_columns = set(df.columns) - set(existing_columns)
            if new_columns:
                for col in new_columns:
                    print(f"[INFO] Menambahkan kolom baru: {col}")
                    with engine.connect() as conn:
                        conn.execute(f"ALTER TABLE extract_data ADD COLUMN {col} VARCHAR(255)")

            # Menyimpan data ke tabel
            df.to_sql("extract_data", con=engine, if_exists="append", index=False)

        print("[INFO] Data berhasil disimpan ke database.")
    except Exception as e:
        print(f"[ERROR] Gagal menyimpan data ke database: {str(e)}")
