from Google import Create_Service
import io
import os
from googleapiclient.http import MediaIoBaseDownload

CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

file_ids = ['1FZN8VdNgPbBnBYyfEh5fZL_26ZW1GUSYXhFtyKEqjgY']
file_names = ['test.docx']

# Use MIME type for .docx
export_mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

for file_id, file_name in zip(file_ids, file_names):
    request = service.files().export_media(fileId=file_id, mimeType=export_mime)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f'Download progress: {int(status.progress() * 100)}%')

    fh.seek(0)
    with open(file_name, 'wb') as f:
        f.write(fh.read())

    print(f'{file_name} downloaded successfully')
