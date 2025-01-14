import re
from bs4 import BeautifulSoup

def is_url_valid(url: str):
    regex = r'^(?:http|ftp)s?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+(/[^ ]*)?$'
    return re.match(regex, url) is not None

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
    elif element_type == 'a':
        href = element.get('href', '#')
        return f"[{element.get_text()}]({href})"
    elif element_type == 'ul':
        return "\n".join([f"- {li.get_text()}" for li in element.find_all('li')])
    elif element_type == 'ol':
        return "\n".join([f"{idx}. {li.get_text()}" for idx, li in enumerate(element.find_all('li'), start=1)])
    
    return ""