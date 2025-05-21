from PIL import Image
import pillow_heif

# Register HEIF plugin for PIL
pillow_heif.register_heif_opener()

# Open HEIC file
image = Image.open("Img/Img1.HEIC")

# Display image info
print(f"Format: {image.format}")
print(f"Mode: {image.mode}")
print(f"Size: {image.size}")

# Extract EXIF data if available
exif_data = image.getexif()
if exif_data:
    print("EXIF Metadata Found:")
    for tag, value in exif_data.items():
        print(f"{tag}: {value}")
else:
    print("No EXIF metadata found.")

