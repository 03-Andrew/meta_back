
# @app.get("/clean_docx/{file_id}")
# async def clean_docx_file(file_id: str):
#     file_path = os.path.join(TEMP_DIR, file_id)
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not found")
    
#     cleaned_file_path = remove_metadata_docx(file_path, file_id)

#     with open(cleaned_file_path, 'rb') as f:
#         cleaned_bytes = f.read()
    
#     # Get metadata of cleaned file
#     metadata, filtered = view_metadata(cleaned_bytes, suffix=os.path.splitext(file_id)[1])

#     return {
#         "message": "File cleaned successfully",
#         "file": file_id,
#         "metadata": metadata,
#         "filtered_metadata": filtered,
#         "download_url": f"/download/cleaned/{file_id}"
#     }



from fastapi import FastAPI, UploadFile, File, HTTPException, Body
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
from typing import List
from pathlib import Path
# import aspose.words as aw
from zipfile import ZipFile
from io import BytesIO
# -------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173","https://docs.google.com"],  # ✅ Use your React dev server URL
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

def remove_metadata_exiftool(file_path):
    with exiftool.ExifTool() as et:
        et.execute(b"-overwrite_original", b"-all=", file_path.encode('utf-8'))

def remove_metadata_docx(file_path, file_id):
    # doc = aw.Document(file_path)
    # doc.built_in_document_properties.clear()
    # doc.custom_document_properties.clear()
    # doc.accept_all_revisions()
    
    # doc.save(os.path.join(TEMP_DIR, f"{file_id}"))
    return os.path.join(TEMP_DIR, f"{file_id}")

def create_zip_file(file_paths, zip_name):
    zip_name = f"{zip_name}_{uuid.uuid4().hex[:8]}"
    zip_path = os.path.join(TEMP_DIR, f"{zip_name}.zip")
    
    with ZipFile(zip_path, 'w') as zip_file:
        for file_path in file_paths:
            zip_file.write(file_path, arcname=os.path.basename(file_path))
    
    return f"{zip_name}.zip"  

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"🗑️ Deleted: {file_path}")
        return True
    except FileNotFoundError:
        print(f"⚠️ File not found: {file_path}")
        return False
    
def get_file_extension(file_path):
    return os.path.splitext(file_path)[1].lower()
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


@app.get("/viewmetadata1/{file_id}")
async def view_metadata_file(file_id: str):
    file_path = os.path.join(TEMP_DIR, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    metadata, filtered = view_metadata(file_bytes, suffix=os.path.splitext(file_id)[1])

    return {
        "filename": file_id,
        "metadata": metadata,
        "filtered": filtered
    }

@app.post("/upload/")
async def create_upload_files(files: List[UploadFile] = File(...), clean: bool = False):
    async def process_single_file(file: UploadFile):
        try:
            file_bytes = await file.read()
            metadata, filtered = view_metadata(
                file_bytes, 
                suffix=f".{file.filename.split('.')[-1]}"
            )
            file_id = save_file_bytes(file_bytes, file.filename)
            
            result = {
                "status": "success",
                "filename": file.filename,
                "fileid": file_id,
                "filetype": file.content_type,
                "metadata": metadata,
                "filtered": filtered
            }

            if clean:
                cleaned_result = await clean_file(file_id)
                result["cleaned"] = cleaned_result

            return result
        except Exception as e:
            return {
                "status": "error",
                "filename": file.filename,
                "error": str(e)
            }

    results = await asyncio.gather(
        *[process_single_file(file) for file in files]
    )
    
    file_ids = [r["fileid"] for r in results if r["status"] == "success"]
    
    return {
        "total_files": len(files),
        "successful": len([r for r in results if r["status"] == "success"]),
        "files": results,
        "file_ids": file_ids,
        "cleaned": clean
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

    if get_file_extension(file_path) in ['.docx', '.doc']:
        # If it's a DOCX file, use Aspose to clean it
        cleaned_file_path = remove_metadata_docx(file_path, file_id)
    else:
        remove_metadata_exiftool(file_path)

    # Read the cleaned file to get its metadata
    with open(file_path, 'rb') as f:
        cleaned_bytes = f.read()
    
    # Get metadata of cleaned file
    metadata, filtered = view_metadata(cleaned_bytes, suffix=os.path.splitext(file_id)[1])

    return {
        "message": "File cleaned successfully",
        "file": file_id,
        "metadata": metadata,
        "filtered_metadata": filtered,
        "download_url": f"/download/cleaned/{file_id}"
    }

@app.post("/clean/batch")
async def clean_files(file_ids: List[str] = Body(...)):
    cleaned_results = []
    # file_paths = []

    for file_id in file_ids:
        file_path = os.path.join(TEMP_DIR, file_id)

        if not os.path.exists(file_path):
            cleaned_results.append({
                "file": file_id,
                "error": "File not found"
            })
            continue

        try:
            if get_file_extension(file_path) in ['.docx', '.doc']:
                cleaned_file_path = remove_metadata_docx(file_path, file_id)
            else:
                remove_metadata_exiftool(file_path)

            with open(file_path, 'rb') as f:
                cleaned_bytes = f.read()

            metadata, filtered = view_metadata(cleaned_bytes, suffix=os.path.splitext(file_id)[1])

            # file_paths.append(cleaned_file_path)

            cleaned_results.append({
                "message": "File cleaned successfully",
                "file": file_id,
                "metadata": metadata,
                "filtered_metadata": filtered,
                "download_url": f"/download/cleaned/{file_id}"
            })
        except Exception as e:
            cleaned_results.append({
                "file": file_id,
                "error": str(e)
            })

    # # Create a zip file of all cleaned files
    # if len(file_paths) > 1:
    #     zip_name = "cleaned_files"
    #     zip_filename = create_zip_file(file_paths, zip_name)
    #     cleaned_results.append({
    #         "zip_download_url": f"/download/cleaned/{zip_filename}"
    #     })
    

    return {"results": cleaned_results}


@app.get("/download/cleaned/{file_id}")
async def download_cleaned_file(file_id: str):
    cleaned_file_path = os.path.join(TEMP_DIR, file_id)
    if not os.path.exists(cleaned_file_path):
        raise HTTPException(status_code=404, detail="Cleaned file not found")
    
    return FileResponse(cleaned_file_path, filename=f"{file_id}")


@app.post("/upload/clean/")
async def upload_clean_file(file: UploadFile = File(...)):
    file_bytes = await file.read()

    file_id = save_file_bytes(file_bytes, file.filename)
    file_path = os.path.join(TEMP_DIR, file_id)
    cleaned_file_path = os.path.join(TEMP_DIR, {file_id})

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
        "file": file_id,
        "metadata": metadata,
        "filtered_metadata": filtered,
        "download_url": f"/download/cleaned/{file_id}"
    }