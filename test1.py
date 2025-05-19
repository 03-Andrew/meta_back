import exiftool
import json
import os
import shutil

def view_metadata(file_path):
    with exiftool.ExifTool() as et:
        result = et.execute(b"-json", file_path.encode('utf-8'))
        metadata = json.loads(result)[0]
        # Pretty print the JSON nicely
        print(json.dumps(metadata, indent=4))

def view_metadata_user_friendly(file_path):
    # Fields users might understand or care about
    friendly_tags = [
        "File:FileName",
        "File:FileSize",
        "File:FileType",
        "EXIF:Make",
        "EXIF:Model",
        "EXIF:DateTimeOriginal",
        "EXIF:CreateDate",
        "EXIF:GPSLatitude",
        "EXIF:GPSLongitude",
        "EXIF:GPSAltitude",
        "EXIF:LensModel",
        "EXIF:FocalLength",
        "EXIF:ExposureTime",
        "EXIF:FNumber",
        "EXIF:ISO",
        "QuickTime:Rotation",
        "QuickTime:ImagePixelDepth",
        "QuickTime:HandlerType"
    ]

    with exiftool.ExifTool() as et:
        result = et.execute(b"-json", file_path.encode('utf-8'))
        metadata = json.loads(result)[0]

        print(f"\n--- Simplified Metadata for {file_path} ---\n")
        for tag in friendly_tags:
            value = metadata.get(tag, None)
            if value is not None:
                print(f"{tag.split(':')[-1]}: {value}")

def duplicate_file(file_path, suffix="_cleaned"):
    """Duplicate a file and return the new file path."""
    file_root, file_ext = os.path.splitext(file_path)
    duplicated_file = f"{file_root}{suffix}{file_ext}"
    shutil.copy2(file_path, duplicated_file)
    print(f"✅ File duplicated as: {duplicated_file}")
    return duplicated_file

def remove_metadata(file_path):
    """Remove all metadata from a file (in-place) without leaving a _original backup."""
    with exiftool.ExifTool() as et:
        et.execute(b"-overwrite_original", b"-all=", file_path.encode('utf-8'))
        print("🚫 Metadata removed from file without backup.")


def duplicate_and_clean(file_path):
    """Duplicate the file, then clean metadata on the duplicate."""
    duplicated_file = duplicate_file(file_path)
    remove_metadata(duplicated_file)
    print(f"📂 Cleaned file saved as: {duplicated_file}")
    return duplicated_file

# Example usage
view_metadata("uploads/12aad37f-ec48-4e5d-8d0d-2d7a0ba77170.png")
