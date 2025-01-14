import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fastapi import HTTPException

def fetch_page(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        raise HTTPException(status_code=500, detail=f"Failed to fetch page: {error}")

def format_markdown(element: BeautifulSoup, element_type: str):
    if element_type == 'h1':
        return f"# {element.get_text()}"
    elif element_type == 'h2':
        return f"## {element.get_text()}"
    elif element_type == 'h3':
        return f"### {element.get_text()}"
    elif element_type == 'h4':
        return f"#### {element.get_text()}"
    elif element_type == 'h5':
        return f"##### {element.get_text()}"
    elif element_type == 'h6':
        return f"###### {element.get_text()}"
    elif element_type == 'p':
        return element.get_text()
    elif element_type == 'li':
        return f"- {element.get_text()}"
    elif element_type == 'blockquote':
        return f"> {element.get_text()}"
    elif element_type == 'a':
        href = element.get('href', '#')
        return f"[{element.get_text()}]({href})"
    elif element_type == 'ul':
        return "\n".join([f"- {li.get_text()}" for li in element.find_all('li')])
    elif element_type == 'ol':
        return "\n".join([f"{idx}. {li.get_text()}" for idx, li in enumerate(element.find_all('li'), start=1)])
    return ""

def parse_page_to_markdown(html_content: str):
    try:
        parsed_html = BeautifulSoup(html_content, 'html.parser')

        for tag in parsed_html(['script', 'style', 'noscript', 'meta', 'head', 'link']):
            tag.decompose()

            extracted_markdown = []
            relevant_elements = ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'ul', 'ol', 'a', 'article', 'section', 'header', 'footer', 'main', 'nav', 'aside', 'strong', 'em', 'b', 'i', 'code', 'pre', 'mark', 'abbr', 'del', 'ins', 'time', 'label', 'fieldset', 'legend', 'summary', 'address', 'table', 'tr', 'td', 'th', 'caption', 'form', 'input', 'textarea', 'button']

        for relevant_element in relevant_elements:
            elements = parsed_html.find_all(relevant_element)
            for element in elements:
                extracted_markdown.append(format_markdown(element, relevant_element).strip())

        return "\n\n".join(extracted_markdown)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to parse page content: {error}")
    
def retrieve_page_urls(html_content: str, url: str):
    try:
        parsed_html = BeautifulSoup(html_content, 'html.parser')
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        for tag in parsed_html(['script', 'style', 'noscript', 'meta', 'head', 'link']):
            tag.decompose()

        link_urls = [url]
        elements = parsed_html.find_all('a')
        for element in elements:
            link_url = element.get('href')
            if link_url:
                resolved_url = urljoin(base_url, link_url)
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
                    if url.startswith(urljoin(base_url, disallow_path)):
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