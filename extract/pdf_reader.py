import pdfplumber

def extract_invoice_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]  # Assuming the first page contains the data
        table = page.extract_table()

        # Process the table and extract the necessary data
        extracted_data = []
        for row in table[1:]:  # Skipping the header row
            print(row)  # Print the raw row for debugging

            # Extract data from the row and handle conversion errors
            try:
                product_id, description, quantity, unit_price, line_total, *_ = row
                # Attempt to convert the values and handle any unexpected formats
                extracted_data.append({
                    "product_id": product_id,
                    "description": description,
                    "quantity": int(quantity) if quantity.isdigit() else None,  # Handle non-numeric values
                    "unit_price": float(unit_price) if unit_price.replace('.', '', 1).isdigit() else None,
                    "line_total": float(line_total) if line_total.replace('.', '', 1).isdigit() else None,
                    "date": "2023-01-01"  # Modify this based on the actual date from the invoice
                })
            except ValueError as e:
                print(f"Error processing row {row}: {e}")

        return extracted_data
