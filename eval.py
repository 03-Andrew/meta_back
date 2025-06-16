import os
import time
import psutil
import requests
import pandas as pd
from collections import defaultdict

API_UPLOAD_URL = "http://localhost:8000/upload/"
API_CLEAN_URL = "http://localhost:8000/clean/batch/v2/"
TEST_FILE_DIR = "test-files"
REPEAT = 5

proc = psutil.Process(os.getpid())
results = defaultdict(list)

# Get all files from test directory
all_files = []
for root, _, files in os.walk(TEST_FILE_DIR):
    for file in files:
        if file.startswith("."):
            continue
        all_files.append(os.path.join(root, file))

def safe_avg(values):
    vals = [v for v in values if v is not None]
    return round(sum(vals) / len(vals), 4) if vals else None

for filepath in all_files:
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()
    cpu_samples, wall_samples, mem_samples = [], [], []

    for _ in range(REPEAT):
        try:
            with open(filepath, "rb") as f:
                file_data = f.read()

            # === Step 1: Upload ===
            upload_start = time.perf_counter()
            proc.cpu_percent(interval=None)
            mem_start = proc.memory_info().rss

            upload_resp = requests.post(
                API_UPLOAD_URL,
                files={"files": (filename, file_data)},
                data={"clean": "false"}
            )
            cpu_upload = proc.cpu_percent(interval=0.2)
            upload_end = time.perf_counter()
            mem_mid = proc.memory_info().rss

            if upload_resp.status_code != 200:
                raise Exception("Upload failed")

            upload_json = upload_resp.json()
            file_obj = upload_json["files"][0]
            file_id = file_obj["fileid"]
            selectable = file_obj.get("selectable", [])

            # === Step 2: Clean ===
            # Build correct payload format
            if ext in [".docx", ".xlsx"]:
                clean_payload = {file_id: selectable}
            else:
                clean_payload = {file_id: ["all"]}

            clean_start = time.perf_counter()
            clean_resp = requests.post(API_CLEAN_URL, json=clean_payload)
            cpu_clean = proc.cpu_percent(interval=0.2)
            clean_end = time.perf_counter()
            mem_end = proc.memory_info().rss

            if clean_resp.status_code != 200:
                raise Exception("Clean failed")

            # === Combine measurements ===
            wall_time = (upload_end - upload_start) + (clean_end - clean_start)
            avg_cpu = (cpu_upload + cpu_clean) / 2
            mem_diff = (mem_end - mem_start) / (1024 * 1024)

            wall_samples.append(wall_time)
            cpu_samples.append(avg_cpu)
            mem_samples.append(mem_diff)

        except Exception as e:
            wall_samples.append(None)
            cpu_samples.append(None)
            mem_samples.append(None)

    results["file"].append(filename)
    results["avg_wall_time"].append(safe_avg(wall_samples))
    results["avg_cpu_percent"].append(safe_avg(cpu_samples))
    results["avg_mem_MB"].append(safe_avg(mem_samples))
    results["runs"].append(len([x for x in wall_samples if x is not None]))

# Convert to DataFrame
df = pd.DataFrame(results)
df.to_csv("api_cleaning_benchmark.csv", index=False)
print(df)
