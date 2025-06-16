import os
import json
import exiftool

# Load your JSON mapping
with open("meta.json", "r") as f:
    metadata_mapping = json.load(f)

EXTENSION_GROUPS = {
    ".jpg": "JPEG/HEIC/TIFF",
    ".jpeg": "JPEG/HEIC/TIFF",
    ".heic": "JPEG/HEIC/TIFF",
    ".tiff": "JPEG/HEIC/TIFF",
    ".tif": "JPEG/HEIC/TIFF",
    ".png": "PNG",
    ".pdf": "PDF",
    ".docx": "DOCX/XLSX/PPTX",
    ".xlsx": "DOCX/XLSX/PPTX",
    ".pptx": "DOCX/XLSX/PPTX",
    ".mp4": "MP4/MOV",
    ".mov": "MP4/MOV",
    ".mp3": "MP3",
}

def extract_full_metadata(path):
    with exiftool.ExifTool() as et:
        # -G to include group names, -j for JSON
        raw = et.execute(b"-G", b"-j", path.encode("utf-8"))
    # raw is bytes of a JSON list; take first element
    return json.loads(raw)[0]

def filter_metadata(path):
    ext = os.path.splitext(path)[1].lower()
    group = EXTENSION_GROUPS.get(ext)
    if not group:
        return {}

    allowed = set(metadata_mapping.get(group, []))
    full = extract_full_metadata(path)

    # If this is an image type, include **all** EXIF:* keys
    if group == "JPEG/HEIC/TIFF":
        exif_keys = {k for k in full.keys() if k.startswith("EXIF:")}
        allowed |= exif_keys

    # Finally, pick out only those keys that actually exist
    return {tag: full[tag] for tag in allowed if tag in full}

if __name__ == "__main__":
    file = "IMG_3118.HEIC"
    if os.path.exists(file):
        meta = filter_metadata(file)
        print(f"Filtered metadata for {file}:")
        print(json.dumps(meta, indent=2))
    else:
        print(f"File {file} does not exist.")
