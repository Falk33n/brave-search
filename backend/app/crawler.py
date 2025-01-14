import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fastapi import HTTPException
from app.utils import format_markdown
from app.utils import is_url_valid
import time
from datetime import datetime
import random

MIN_DELAY = 1
MAX_DELAY = 3

def fetch_page(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        raise HTTPException(status_code=500, detail=f"Failed to fetch page: {error}")

def parse_page_content(url: str):
    try:
        html_content = fetch_page(url)
        parsed_html = BeautifulSoup(html_content, 'html.parser')
        title = parsed_html.title.get_text() if parsed_html.title else "No title"

        for tag in parsed_html(['script', 'noscript', 'head']):
            tag.decompose()

            extracted_markdown = []
            relevant_elements = ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'a']

        for relevant_element in relevant_elements:
            elements = parsed_html.find_all(relevant_element)

            for element in elements:
                extracted_markdown.append(format_markdown(element, relevant_element).strip())

        return {"title": title, "content": "\n\n".join(extracted_markdown)}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to parse page content: {error}")
    
def parse_website_content(url: str, visited_urls=None, depth=6) -> list:
    if visited_urls is None:
        visited_urls = set()
    if depth == 0 or url in visited_urls:
        return []

    visited_urls.add(url)
    page_metadata = parse_page_content(url)

    metadata = {
        "url": url,
        "title": page_metadata["title"],
        "word_count": len(page_metadata["content"].split()),
        "last_crawled": datetime.now().strftime("%Y-%m-%d"),
        "depth": depth
    }

    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    if not is_crawling_allowed(url):
        raise HTTPException(status_code=403, detail=f"Crawling disallowed for {url}")

    urls = retrieve_page_urls(url)
    crawled_data = [{"content": page_metadata["content"], "metadata": metadata}]
    
    print(f"Crawled one page: {url}")

    for link in urls:
        if link not in visited_urls and is_url_valid(link):
            print(f"Next URL to crawl: {link}")
            crawled_data.extend(parse_website_content(link, visited_urls, depth-1))

    return crawled_data
    
def retrieve_page_urls(url: str):
    try:
        html_content = fetch_page(url)
        parsed_html = BeautifulSoup(html_content, 'html.parser')
        parsed_url = urlparse(url)

        for tag in parsed_html(['script', 'noscript', 'head']):
            tag.decompose()

        link_urls = [url]
        elements = parsed_html.find_all('a')

        for element in elements:
            link_url = element.get('href')

            if link_url:
                if '#' in link_url or link_url.startswith('./') or link_url.startswith('../'):
                    continue

                resolved_url = urljoin(url, link_url)
                resolved_netloc = urlparse(resolved_url).netloc

                if resolved_netloc == parsed_url.netloc:
                    link_urls.append(resolved_url)

        return link_urls
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve URLs: {error}")

def is_crawling_allowed(url: str):
    try:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = urljoin(base_url, "robots.txt")
        response = requests.get(robots_url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            rules = {}
            current_user_agent = None
            lines = response.text.splitlines()

            for line in lines:
                line = line.strip()

                if line.startswith("User-agent:"):
                    current_user_agent = line.split(":", 1)[1].strip()
                    rules[current_user_agent] = {"Allow": [], "Disallow": []}
                elif current_user_agent and line.startswith("Allow:"):
                    path = line.split(":", 1)[1].strip()
                    rules[current_user_agent]["Allow"].append(path)
                elif current_user_agent and line.startswith("Disallow:"):
                    path = line.split(":", 1)[1].strip()
                    rules[current_user_agent]["Disallow"].append(path)

            matched_rules = rules.get("*")

            if matched_rules:
                for disallow_path in matched_rules["Disallow"]:
                    if disallow_path == "": 
                        continue
                    elif url.startswith(urljoin(base_url, disallow_path)):
                        return False
                    
                for allow_path in matched_rules["Allow"]:
                    if url.startswith(urljoin(base_url, allow_path)):
                        return True

            return True
        return True
    except requests.RequestException as error:
        if error.response.status_code in [404, 400, 307]:
            return True
        
        return False