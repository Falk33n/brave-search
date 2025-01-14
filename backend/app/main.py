from fastapi import FastAPI, HTTPException
from app.crawler import fetch_page, parse_website_content, parse_page_content, retrieve_page_urls, is_crawling_allowed
from app.utils import is_url_valid
from pydantic import BaseModel

app = FastAPI()

class CrawlRequest(BaseModel):
    url: str

@app.post("/crawl-page")
async def crawl_page(request: CrawlRequest) -> str:
    if not is_url_valid(request.url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    elif not is_crawling_allowed(request.url):
        raise HTTPException(status_code=400, detail="URL is not crawlable")
    
    return parse_page_content(request.url)

@app.post("/crawl-urls")
async def crawl_urls(request: CrawlRequest):
    if not is_url_valid(request.url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    elif not is_crawling_allowed(request.url):
        raise HTTPException(status_code=400, detail="URL is not crawlable")
    
    return retrieve_page_urls(request.url)

@app.post("/crawl-website")
async def crawl_website(request: CrawlRequest, depth: int = 2) -> list:
    if not is_url_valid(request.url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    elif not is_crawling_allowed(request.url):
        raise HTTPException(status_code=400, detail="URL is not crawlable")
    
    return parse_website_content(request.url, depth=depth)