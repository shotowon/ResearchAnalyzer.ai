import os
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from pathlib import Path
import aiohttp
from src.Api.api import Api 

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
        print("exists")
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")



@app.get("/place-pdf")
async def download_scihub_pdf(doi: str):
    print(doi)
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