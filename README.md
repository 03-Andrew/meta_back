# 🧼 Metastrip Backend


## 🧪 Running the Server

### 1. Install Dependencies

Make sure all Python dependencies are installed:

```bash
pip install -r requirements.txt
```
### 2. Install ExifTool
This project requires ExifTool to be installed on your system.

- On macOS (using Homebrew):
```bash
brew install exiftool
```
- On Ubuntu/Debian:
```bash
sudo apt-get install libimage-exiftool-perl
```
- On Windows:
Download and install from the official ExifTool site.

### 3. Run the Server
Start the FastAPI backend server:
```bash
python main.py
```
The server will run at:
http://localhost:8000

You can access the interactive API docs at:
http://localhost:8000/docs
