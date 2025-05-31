from openpyxl import load_workbook
from openpyxl.packaging.core import DocumentProperties

def clean_excel_metadata(filepath, output_path=None):
    try:
        wb = load_workbook(filepath)

        # Overwrite the entire metadata object with a clean one
        wb.properties = DocumentProperties()

        output_path = output_path or filepath
        wb.save(output_path)
        print(f"[✓] Cleaned metadata: {filepath}")
    except Exception as e:
        print(f"[!] Failed to clean metadata from {filepath}: {e}")

clean_excel_metadata("test/Test1.xlsx", "test/Test1_cleaned.xlsx")
