import os
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import aiohttp
import fitz  # PyMuPDF
from src.Api.api import Api
from pgpt_python.client import PrivateGPTApi

app = FastAPI()

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
            print("Extracted text from page:", page_text)  # Log extracted text from each page
    return text

def split_text_into_chunks(text: str, chunk_size: int = 2048) -> list:
    """Split text into manageable chunks."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

async def summarize_text(text: str) -> str:
    chunks = split_text_into_chunks(text)
    summaries = []
    for chunk in chunks:
        response = pgpt_client.contextual_completions.prompt_completion(prompt=f"Summarize this document:\n{chunk}")
        if response.choices:
            summaries.append(response.choices[0].message.content)
            print(response.choices[0].message.content)
    return " ".join(summaries)

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
async def summarize_pdf(file_name: str):
    file_path = DOWNLOAD_FOLDER / file_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Extract and summarize text
        text = extract_text_from_pdf(file_path)
        if not text.strip():  # Check if the extracted text is empty
            raise ValueError("No text extracted from PDF.")
        
        summary = await summarize_text(text)
        return {"summary": summary, "status_code": 200}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during summarization: {str(e)}")

@app.get("/place-pdf")
async def download_scihub_pdf(doi: str):
    try:
        _, html_content = await Api.get_page(doi)
        
        if not html_content:
            raise HTTPException(status_code=500, detail="Empty response content")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        embed_tag = soup.find("embed")
        
        if embed_tag and 'src' in embed_tag.attrs:
            pdf_url = embed_tag['src']
            if pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url
            pdf_filename = pdf_url.split("/")[-1].split("#")[0]
            
            file_path = await download_pdf(pdf_url, pdf_filename)
            return {"message": "PDF downloaded", "file_path": str(file_path), "status_code": 200}
        else:
            raise HTTPException(status_code=404, detail="PDF link not found in the page content")
    
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
