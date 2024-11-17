import os
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi import File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import aiohttp
import fitz  # PyMuPDF
from src.Api.api import Api
from pgpt_python.client import PrivateGPTApi
import sqlite3


DB_PATH = Path("file_gpt_map.db")
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_gpt_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            doc_id TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_mapping(filename: str, doc_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO file_gpt_map (filename, doc_id) VALUES (?, ?)", (filename, doc_id))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"File '{filename}' already exists in the database.")
    finally:
        conn.close()

# Fetch a mapping from the database
def get_mapping(filename: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT doc_id FROM file_gpt_map WHERE filename = ?", (filename,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        raise HTTPException(status_code=404, detail=f"No mapping found for file '{filename}'.")

# Initialize the database
init_db()


app = FastAPI()
summaries_store = {}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # for frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_FOLDER = Path("../Media")
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# Initialize PrivateGPT client
pgpt_client = PrivateGPTApi(base_url="http://localhost:8001")

async def download_pdf(pdf_url: str, filename: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                if response.status == 200:
                    file_path = DOWNLOAD_FOLDER / filename
                    with open(file_path, 'wb') as f:
                        f.write(await response.read())
                    return file_path
                else:
                    raise HTTPException(status_code=404, detail="Failed to download PDF")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

def extract_text_from_pdf(file_path: Path) -> str:
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            page_text = page.get_text()
            text += page_text
    return text


def split_text_into_chunks(text: str, chunk_size: int = 2048) -> list:
    """Split text into manageable chunks."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


async def summarize_text(text: str) -> str:
    
    chunks = split_text_into_chunks(text)
    summaries = []
    try:
        
        for chunk in chunks:
            response = pgpt_client.contextual_completions.prompt_completion(prompt=f"Summarize this document:\n{chunk}")
            print(response.choices[0].message.content)

            summaries.append(response.choices[0].message.content)
            return " ".join(summaries)
       
    except Exception as e:
        print(f"An error occurred during summarization: {str(e)}")
        summaries.append(f"An error occurred during summarization. {str(e)}")
    return " ".join(summaries)


async def background_summarize(file_path: Path, file_name: str):
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise ValueError("No text extracted from PDF.")
    summary = await summarize_text(text)
    summaries_store[file_name] = {"summary": summary, "status": "completed"}

    print(f"Summary for {file_path.name}: {summary}")

@app.get("/files")
async def list_files():
    try:
        files = [
            {"name": file.name, "path": str(file.resolve())}
            for file in DOWNLOAD_FOLDER.iterdir()
            if file.is_file() and file.suffix == ".pdf"
        ]
        return {"files": files, "status_code": 200}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

@app.get("/file/{file_name}")
async def get_file(file_name: str):
    file_path = DOWNLOAD_FOLDER / file_name  
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/summarize/{file_name}")
async def summarize_pdf(file_name: str, background_tasks: BackgroundTasks):
    file_path = DOWNLOAD_FOLDER / file_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Add the summarization task to the background, passing both arguments
    background_tasks.add_task(background_summarize, file_path, file_name)
    
    return {"message": "Summarization started, you will be notified when it's done.", "status_code": 202}


@app.get("/summary/{file_name}")
async def get_summary(file_name: str):
    if file_name in summaries_store:
        return summaries_store[file_name]
    else:
        raise HTTPException(status_code=404, detail="Summary not found or still processing.")
    
    
    
    
def ingest_file_and_store(file_path: str, filename: str):
    with open(file_path, "rb") as f:
        ingested_file_doc_id = pgpt_client.ingestion.ingest_file(file=f, timeout=500).data[0].doc_id
    print(f"Ingested file doc_id: {ingested_file_doc_id}")
    insert_mapping(filename, ingested_file_doc_id)

@app.post("/process-pdf")
async def process_pdf(
    file: UploadFile = File(None),
    doi: str = Form(None),
    background_tasks: BackgroundTasks = None,
):
    try:
        if file and doi:
            raise HTTPException(status_code=400, detail="Provide either a DOI or a file, not both.")
        if not file and not doi:
            raise HTTPException(status_code=400, detail="Provide either a DOI or a file.")

        # Handle File Upload
        if file:
            if file.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail="Uploaded file must be a PDF")

            file_path = DOWNLOAD_FOLDER / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # Queue background ingestion
            background_tasks.add_task(ingest_file_and_store, str(file_path), file.filename)

            return {"message": "PDF uploaded successfully. Processing in background.", "file_path": str(file_path)}

        # Handle DOI Input (For simplicity, assuming this doesn't involve a background task)
        if doi:
            _, html_content = await Api.get_page(doi)
            if not html_content:
                raise HTTPException(status_code=500, detail="Empty response content")

            # Extract PDF URL and download it
            soup = BeautifulSoup(html_content, "html.parser")
            download_button = soup.select_one("#buttons button[onclick]")
            if download_button:
                onclick_attr = download_button.get("onclick")
                if onclick_attr:
                    url_start = onclick_attr.find("location.href='") + len("location.href='")
                    url_end = onclick_attr.find("'", url_start)
                    pdf_url = onclick_attr[url_start:url_end]

                    # Construct absolute URL if needed
                    if pdf_url.startswith("/"):
                        pdf_url = "https://sci-hub.ru" + pdf_url
                    pdf_filename = pdf_url.split("/")[-1].split("?")[0]
                    file_path = await download_pdf(pdf_url, pdf_filename)

                    # Queue background ingestion
                    background_tasks.add_task(ingest_file_and_store, str(file_path), pdf_filename)

                    return {"message": "PDF downloaded successfully. Processing in background.", "file_path": str(file_path)}

            raise HTTPException(status_code=404, detail="PDF download URL not found in the page content")

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/mapping/{filename}")
def get_file_mapping(filename: str):
    """Fetch the GPT document ID for a given file."""
    doc_id = get_mapping(filename)
    return {"filename": filename, "doc_id": doc_id}
