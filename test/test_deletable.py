import tempfile
import shutil
import json
import os
import exiftool  # pip install exiftool

def get_exiftool_metadata(file_path):
    with exiftool.ExifTool() as et:
        result = et.execute(b"-json", file_path.encode("utf-8"))
        return json.loads(result)[0]

def get_deletable_metadata_exiftool(file_bytes, suffix=".jpg"):
    # Step 1: Save original file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        tmp_path = tmp.name

    try:
        # Step 2: Get original metadata
        original_metadata = get_exiftool_metadata(tmp_path)

        # Step 3: Overwrite temp file with deleted metadata version
        with exiftool.ExifTool() as et:
            et.execute(b"-all=", b"-overwrite_original", tmp_path.encode("utf-8"))

        # Step 4: Get cleaned metadata
        cleaned_metadata = get_exiftool_metadata(tmp_path)

        # Step 5: Compare and extract deletable fields
        deletable = {k: v for k, v in original_metadata.items() if k not in cleaned_metadata}

    finally:
        os.remove(tmp_path)

    return deletable


# Assume you have some uploaded file as bytes
with open("test/Test1.JPG", "rb") as f:
    file_bytes = f.read()

deletable_tags = get_deletable_metadata_exiftool(file_bytes, suffix=".JPG")

for tag, value in deletable_tags.items():
    print(f"{tag}: {value}")
