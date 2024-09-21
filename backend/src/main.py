import os
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pathlib import Path
import aiohttp
from src.Api.api import Api 

app = FastAPI()


DOWNLOAD_FOLDER = Path("../downloaded_pdfs")
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
    
    

@app.get("/place-pdf")
async def download_scihub_pdf(doi: str):
    print(doi)
    try:
        response, html_content = await Api.get_page(doi)
        
        print(f"Response status: {response.status}")
        print(f"Response headers: {response.headers}")
        print(f"Response cookies: {response.cookies}")
        print(f"Content length: {len(html_content)}")
        
        if not html_content:
            raise HTTPException(status_code=500, detail="Empty response content")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        embed_tag = soup.find("embed")
        
        if embed_tag and 'src' in embed_tag.attrs:
            pdf_url = embed_tag['src']
            if pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url
            pdf_filename = pdf_url.split("/")[-1].split("#")[0]
            print(f"PDF URL: {pdf_url}")
            print(f"PDF Filename: {pdf_filename}")
            
            file_path = await download_pdf(pdf_url, pdf_filename)
            return {"message": "PDF downloaded", "file_path": str(file_path)}
        else:
            raise HTTPException(status_code=404, detail="PDF link not found in the page content")
    
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")