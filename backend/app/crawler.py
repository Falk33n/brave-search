import requests
from bs4 import BeautifulSoup

def fetch_page(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        return response.text
    except requests.RequestException as error:
        return f"Error: {error}"

def extract_content(html_content: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    paragraphs = soup.find_all('p')
    content = "\n".join([p.get_text() for p in paragraphs])
    
    return content

def can_crawl(url: str):
    try:
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException:
        return False