import exiftool
from typing import List
def remove_metadata_tags_exiftool(file_path: str, tags: List[str]):
    # tags like ["EXIF:Orientation", "EXIF:XResolution"]
    args = [
            b"-overwrite_original",
            b"-m",
            *[f"-{tag}=".encode("utf-8") for tag in tags],
            file_path.encode("utf-8"),
        ]    
    print(args, flush=True)
    with exiftool.ExifTool() as et:
        et.execute(*args)

file="cleaned_IMG.HEIC"
tags = [
  "EXIF:Orientation",
  "EXIF:XResolution",
  "EXIF:YResolution",
  "EXIF:ResolutionUnit",
  "EXIF:Software",
  "EXIF:ModifyDate",
  "EXIF:HostComputer",
  "EXIF:ExposureTime",
  "EXIF:FNumber",
  "EXIF:ExposureProgram",
  "EXIF:ISO",
  "EXIF:ExifVersion",
  "EXIF:DateTimeOriginal",
  "EXIF:CreateDate",
  "EXIF:OffsetTime",
  "EXIF:OffsetTimeOriginal",
  "EXIF:OffsetTimeDigitized",
  "EXIF:ShutterSpeedValue",
  "EXIF:ApertureValue",
  "EXIF:BrightnessValue",
  "EXIF:ExposureCompensation",
  "EXIF:MeteringMode",
  "EXIF:Flash",
  "EXIF:FocalLength",
  "EXIF:SubSecTimeOriginal",
  "EXIF:SubSecTimeDigitized",
  "EXIF:ColorSpace",
  "EXIF:ExifImageWidth",
  "EXIF:ExifImageHeight",
  "EXIF:SensingMethod",
  "EXIF:SceneType",
  "EXIF:CustomRendered",
  "EXIF:ExposureMode",
  "EXIF:WhiteBalance",
  "EXIF:FocalLengthIn35mmFormat",
  "EXIF:LensInfo",
  "EXIF:LensMake",
  "EXIF:LensModel",
  "EXIF:GPSLatitudeRef",
  "EXIF:GPSLongitudeRef",
  "EXIF:GPSAltitudeRef",
  "EXIF:GPSAltitude",
  "EXIF:GPSSpeedRef",
  "EXIF:GPSSpeed",
  "EXIF:GPSImgDirectionRef",
  "EXIF:GPSImgDirection",
  "EXIF:GPSDestBearingRef",
  "EXIF:GPSDestBearing",
  "EXIF:GPSDateStamp",
  "EXIF:GPSHPositioningError",
  "XMP:CreateDate",
  "XMP:ModifyDate"
]


remove_metadata_tags_exiftool(file, tags)




