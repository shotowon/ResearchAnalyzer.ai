import aiohttp
from fastapi import HTTPException
class Api:
    __url = "https://sci-hub.ru"

    @staticmethod
    async def request(url: str, method: str, data: dict = None, headers: dict = {}) -> aiohttp.ClientResponse:
        try:
            
            conn = aiohttp.TCPConnector(limit_per_host=10, keepalive_timeout=60)
            async with aiohttp.ClientSession(connector=conn) as session:
                async with session.request(method, url, ssl=True , data=data, headers=headers) as response:
                    html_content = await response.text()
                    return response, html_content
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

    @staticmethod
    async def get_page(doi: str):
        url = f"{Api.__url}/{doi}"
        print("fetching this ",url)
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
        response, html_content = await Api.request(url, "GET", headers=headers)
        print(response)
        
        return response, html_content
        
    

    @staticmethod
    async def get_pdf(pdf_url: str):
        return await Api.request(pdf_url, "GET")