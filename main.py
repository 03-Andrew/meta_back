from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import time
import os
import uuid
import shutil
import exiftool
import json
import tempfile
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "https://docs.google.com"],  # ✅ Use your React dev server URL
    allow_credentials=True,
    allow_methods=["*"],  # or restrict to ['POST']
    allow_headers=["*"],  # or restrict to ['Content-Type', 'Authorization']
)

TEMP_DIR = "uploads"
MAX_AGE_SECONDS = 5 * 60  # 5 minutes

os.makedirs(TEMP_DIR, exist_ok=True)


def delete_old_files():
    now = time.time()
    for file in Path(TEMP_DIR).glob("*"):
        if file.is_file() and now - file.stat().st_mtime > MAX_AGE_SECONDS:
            try:
                file.unlink()
                print(f"🗑️ Deleted: {file}")
            except Exception as e:
                print(f"⚠️ Failed to delete {file}: {e}")

def view_metadata(file_bytes, suffix):
    """Reads metadata from raw file bytes using a temporary file."""

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

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        tmp_path = tmp.name
        
    with exiftool.ExifTool() as et:
        result = et.execute(b"-json", tmp_path.encode('utf-8'))
        metadata = json.loads(result)[0]

    filtered = {tag: metadata[tag] for tag in friendly_tags if tag in metadata}
    return metadata, filtered

def save_file_bytes(file_bytes: bytes, original_filename: str):
    upload_dir = os.path.join(os.getcwd(), TEMP_DIR)
    
    # Split filename and extension
    filename_base, ext = os.path.splitext(original_filename)
    ext = ext or ".bin"  # Default to .bin if no extension
    
    # Create unique filename while preserving original name
    unique_filename = f"{filename_base}_{uuid.uuid4().hex[:8]}{ext}"
    dest = os.path.join(upload_dir, unique_filename)

    with open(dest, "wb") as buffer:
        buffer.write(file_bytes)
    
    return unique_filename

# ----------------------------------- 
#               APIs
# -----------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background cleanup task
    async def cleanup_loop():
        while True:
            delete_old_files()
            await asyncio.sleep(60)  # run every minute

    task = asyncio.create_task(cleanup_loop())

    yield  # app is now running

    # Cleanup when app shuts down
    task.cancel()

@app.post("/viewmetadata/")
async def view_metadata_endpoint(file: UploadFile = File(...)):
    file_bytes = await file.read()
    metadata, filtered = view_metadata(file_bytes, suffix=f".{file.filename.split('.')[-1]}")

    return {
        "filename": file.filename, 
        "metadata": metadata, 
        "filtered": filtered
    }

@app.post("/uploadfilev1/")
async def upload_v1(file: UploadFile = File(...)):
    file_bytes = await file.read()
    metadata, filtered = view_metadata(file_bytes, suffix=f".{file.filename.split('.')[-1]}")

    return {
        "filename": file.filename, 
        "metadata": metadata, 
        "filtered": filtered
    }

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    # Read the entire file once
    file_bytes = await file.read()

    # Get metadata first from the bytes
    metadata, filtered = view_metadata(file_bytes, suffix=f".{file.filename.split('.')[-1]}")

    # Then save the same bytes to disk
    file_id = save_file_bytes(file_bytes, file.filename)

    return {
        "filename": file.filename,
        "fileid": file_id,
        "filetype": file.content_type,
        "metadata": metadata,
        "filtered": filtered
    }

@app.get("/getfile/{file_id}")
async def get_file(file_id: str):
    file_path = os.path.join(TEMP_DIR, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)


@app.get("/clean/{file_id}")
async def clean_file(file_id: str):
    file_path = os.path.join(TEMP_DIR, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Create cleaned filename safely
    cleaned_file_path = os.path.join(TEMP_DIR, f"cleaned_{file_id}")
    shutil.copy2(file_path, cleaned_file_path)

    # Clean the duplicate only
    with exiftool.ExifTool() as et:
        et.execute(b"-overwrite_original", b"-all=", cleaned_file_path.encode('utf-8'))

    # Read the cleaned file to get its metadata
    with open(cleaned_file_path, 'rb') as f:
        cleaned_bytes = f.read()
    
    # Get metadata of cleaned file
    metadata, filtered = view_metadata(cleaned_bytes, suffix=os.path.splitext(file_id)[1])

    return {
        "message": "File cleaned successfully",
        "original_file": file_id,
        "cleaned_file": f"cleaned_{file_id}",
        "metadata": metadata,
        "filtered_metadata": filtered,
        "download_url": f"/download/cleaned/{file_id}"
    }

@app.get("/download/cleaned/{file_id}")
async def download_cleaned_file(file_id: str):
    cleaned_file_path = os.path.join(TEMP_DIR, f"cleaned_{file_id}")
    if not os.path.exists(cleaned_file_path):
        raise HTTPException(status_code=404, detail="Cleaned file not found")
    
    return FileResponse(cleaned_file_path, filename=f"cleaned_{file_id}")

@app.delete("/delete/{file_id}")
async def delete_file(file_id: str):
    file_path = os.path.join(TEMP_DIR, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(file_path)
    return {"message": "File deleted successfully"}


@app.post("/upload/clean/")
async def upload_clean_file(file: UploadFile = File(...)):
    file_bytes = await file.read()

    file_id = save_file_bytes(file_bytes, file.filename)
    file_path = os.path.join(TEMP_DIR, file_id)
    cleaned_file_path = os.path.join(TEMP_DIR, f"cleaned_{file_id}")
    shutil.copy2(file_path, cleaned_file_path)
    with exiftool.ExifTool() as et:
        et.execute(b"-overwrite_original", b"-all=", cleaned_file_path.encode('utf-8'))
    
     # Read the cleaned file to get its metadata
    with open(cleaned_file_path, 'rb') as f:
        cleaned_bytes = f.read()

    # Get metadata of cleaned file
    metadata, filtered = view_metadata(cleaned_bytes, suffix=os.path.splitext(file_id)[1])

    return {
        "message": "File cleaned successfully",
        "original_file": file_id,
        "cleaned_file": f"cleaned_{file_id}",
        "metadata": metadata,
        "filtered_metadata": filtered,
        "download_url": f"/download/cleaned/{file_id}"
    }


