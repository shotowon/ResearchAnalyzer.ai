from pathlib import Path

DB_PATH = Path("file_gpt_map.db")
S3_BUCKET = "ra-ai"
DOWNLOAD_FOLDER = Path("../Media")
DOWNLOAD_FOLDER.mkdir(exist_ok=True)
