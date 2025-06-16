import exiftool
import json


def remove_metadata_fields(file_path: str, fields_to_remove: list[str]):
    with exiftool.ExifTool() as et:
        args = [b"-overwrite_original", b"-ignoreMinorErrors"]
        for field in fields_to_remove:
            args.append(f"-{field}=".encode("utf-8"))
        args.append(file_path.encode("utf-8"))
        et.execute(*args)

import exiftool
import json

def verify_fields_removed(file_path: str, fields_to_check: list[str]) -> dict:
    """
    Returns a dictionary indicating whether each field is still present.
    """
    with exiftool.ExifTool() as et:
        result = et.execute(b"-json", file_path.encode("utf-8"))
        metadata = json.loads(result)[0]

    return {field: field in metadata for field in fields_to_check}


file_path = "Kayak.jpg"

fields = [
        "JFIF:JFIFVersion",
        "JFIF:ResolutionUnit",
        "JFIF:XResolution",
        "JFIF:YResolution"
    ]
remove_metadata_fields(file_path, fields)

# After deletion
status = verify_fields_removed(file_path, fields)
for field, present in status.items():
    print(f"{field}: {'❌ Still present' if present else '✅ Removed'}")


