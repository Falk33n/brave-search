from fastapi import FastAPI, HTTPException
from app.crawler import fetch_page, parse_page_to_markdown, retrieve_page_urls, is_crawling_allowed
from app.utils import is_url_valid
from pydantic import BaseModel

app = FastAPI()

class CrawlRequest(BaseModel):
    url: str

@app.post("/crawl-page")
async def crawl_page(request: CrawlRequest) -> str:
    url = request.url
    if not is_url_valid(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    elif not is_crawling_allowed(url):
        raise HTTPException(status_code=400, detail="URL is not crawlable")
    
    html_content = fetch_page(url)
    return parse_page_to_markdown(html_content)

@app.post("/crawl-urls")
async def crawl_page(request: CrawlRequest):
    url = request.url
    if not is_url_valid(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    elif not is_crawling_allowed(url):
        raise HTTPException(status_code=400, detail="URL is not crawlable")
    
    html_content = fetch_page(url)
    return retrieve_page_urls(html_content, url)