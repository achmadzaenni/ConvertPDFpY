import mysql.connector

def save_to_sql(df, table_name='invoice', db_config=None):
    if db_config is None:
        raise ValueError("db_config must be provided")

    conn = mysql.connector.connect(
        host=db_config['localhost'],
        user=db_config['root'],
        password=db_config[''],
        database=db_config['convertdata']
    )
    cursor = conn.cursor()

    # Membuat tabel jika belum ada
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        level INT,
        page_num INT,
        block_num INT,
        par_num INT,
        line_num INT,
        word_num INT,
        left_pos INT,
        top_pos INT,
        width INT,
        height INT,
        conf FLOAT,
        text_content TEXT
    )
    """
    cursor.execute(create_table_query)

    # Insert data
    for _, row in df.iterrows():
        insert_query = f"""
        INSERT INTO {table_name} (level, page_num, block_num, par_num, line_num, word_num, left_pos, top_pos, width, height, conf, text_content)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            int(row['level']),
            int(row['page_num']),
            int(row['block_num']),
            int(row['par_num']),
            int(row['line_num']),
            int(row['word_num']),
            int(row['left']),
            int(row['top']),
            int(row['width']),
            int(row['height']),
            float(row['conf']),
            str(row['text'])
        )
        cursor.execute(insert_query, values)

    conn.commit()
    cursor.close()
    conn.close()
