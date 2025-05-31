import zipfile
import shutil
import os
from io import BytesIO

def clean_docx_metadata(path):
    # In-memory output docx
    buffer = BytesIO()

    with zipfile.ZipFile(path, 'r') as zin:
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                # Skip metadata files
                if item.filename in [
                    'docProps/core.xml',
                    'docProps/app.xml',
                    'custom.xml'
                ]:
                    continue

                # Copy everything else
                data = zin.read(item.filename)
                zout.writestr(item, data)

    # Write cleaned file
    with open(path, 'wb') as f:
        f.write(buffer.getvalue())


# Usage
clean_docx_metadata("test/test1.docx", "test/test1_cleaned.docx")
