import sqlite3

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import uvicorn

from src.consts import DB_PATH
from src.api.routers.main import router
from src.init import logger, cfg


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS file_gpt_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            doc_id TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router)
