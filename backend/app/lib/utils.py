"""
This module provides a set of functions to handle web scraping tasks, including URL validation, 
crawling permission checking, HTML content extraction, and HTML parsing. It integrates with the 
FastAPI framework for raising HTTPExceptions when errors occur during web scraping.

Functions:

- is_url_valid(url: str): Validates whether the given URL matches a standard format for HTTP, 
  HTTPS, or FTP URLs.
- get_base_url(url: str): Extracts the base URL (scheme and netloc) from a given URL.
- get_html_content(url: str): Fetches the HTML content of a given URL.
- get_crawling_rules(robots_content: str): Parses a `robots.txt` file to extract the crawling rules.
- is_crawling_allowed(url: str): Checks if crawling is allowed for a given URL based on the site's 
  `robots.txt` file.
- validate_url(url: str): Validates the given URL and checks if crawling is allowed.
- remove_unwanted_tags(parsed_html: BeautifulSoup): Removes unwanted HTML tags such as `<script>`, 
  `<noscript>`, and `<head>` from the parsed HTML content.
- get_parsed_html(url: str): Fetches and parses the HTML content of a given URL into a BeautifulSoup 
  object.

Constants:
- OK, FETCH_TIMEOUT, INTERNAL_SERVER_ERROR, FORBIDDEN, CRAWLING_NOT_ALLOWED_ERROR, 
  INVALID_URL_ERROR, BAD_REQUEST: Predefined constants used for handling HTTP responses and errors.
"""

from urllib.parse import urljoin, urlparse
from re import match
from bs4 import BeautifulSoup
import requests
from requests import RequestException
from fastapi import HTTPException
from app.lib.constants import (
    OK,
    FETCH_TIMEOUT,
    INTERNAL_SERVER_ERROR,
    FORBIDDEN,
    BAD_REQUEST,
)


def is_url_valid(url: str):
    """
    Validates whether the provided URL matches a standard format for HTTP, HTTPS, or FTP URLs.

    This function uses a regular expression to check if the given URL is valid. It matches URLs
    that begin with "http://", "https://", or "ftp://", followed by an optional "www." and then
    a domain name (with alphanumeric characters and hyphens), a period, and a domain extension.
    The URL can optionally include a path.

    Returns:
    - bool: True if the URL matches the pattern, otherwise False.
    """

    regex = r"^(?:http|ftp)s?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+(/[^ ]*)?$"
    return match(regex, url) is not None


def get_base_url(url: str):
    """
    Extracts the base URL (scheme and netloc) from a given URL.

    This function parses the provided URL and constructs a new URL containing only the scheme
    (e.g., "http", "https") and netloc (e.g., "www.example.com") parts of the original URL,
    excluding the path, query parameters, or fragments.

    Parameters:
    - url (str): The full URL from which the base URL will be extracted.

    Returns:
    - str: The base URL in the format "{scheme}://{netloc}".
    """

    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def get_html_content(url: str):
    """
    Fetches the HTML content of a given URL.

    This function sends an HTTP GET request to the provided URL and retrieves its HTML content.
    If the request is successful, the HTML content is returned as a string.
    In case of any error during the request (such as a timeout or invalid URL), an
    HTTPException is raised with an appropriate error message.

    Parameters:
    - url (str): The URL of the page to fetch.

    Returns:
    - str: The HTML content of the page as a string.

    Raises:
    - HTTPException: If a request error occurs (e.g., network issues, timeout, invalid URL),
      an HTTPException is raised with status code 500 and an error message indicating the failure.
    """

    try:
        response = requests.get(url, timeout=FETCH_TIMEOUT)
        response.raise_for_status()
        return response.text
    except RequestException as error:
        raise HTTPException(
            status_code=INTERNAL_SERVER_ERROR, detail=f"Failed to fetch page: {error}"
        ) from error


def get_crawling_rules(robots_content: str):
    """
    Parses the content of a robots.txt file to extract crawling rules.

    This function processes the raw content of a `robots.txt` file, which contains rules
    for web crawlers such as which pages or paths can or cannot be accessed. It builds a
    dictionary mapping user agents to their respective "Allow" and "Disallow" paths,
    indicating which pages or sections of the website are permitted or restricted for crawling.

    Parameters:
    - robots_content (str): The raw content of a `robots.txt` file, typically
      retrieved from a website's `robots.txt` file.

    Returns:
    - dict: A dictionary where keys are user agents (as strings), and the values
      are another dictionary with "Allow" and "Disallow" keys, each containing
      a list of paths that are allowed or disallowed for crawling by the respective user agent.
    """

    rules = {}
    current_user_agent = None
    lines = robots_content.splitlines()

    for line in lines:
        line = line.strip()

        if line.startswith("User-agent:"):
            current_user_agent = line.split(":", 1)[1].strip()
            rules[current_user_agent] = {"Allow": [], "Disallow": []}
        elif current_user_agent:
            if line.startswith("Allow:"):
                path = line.split(":", 1)[1].strip()
                rules[current_user_agent]["Allow"].append(path)
            elif line.startswith("Disallow:"):
                path = line.split(":", 1)[1].strip()
                rules[current_user_agent]["Disallow"].append(path)

    return rules


def is_crawling_allowed(url: str):
    """
    Checks if crawling is allowed for a given URL based on the site's robots.txt file.

    This function retrieves the `robots.txt` file from the base URL of the provided URL, parses it,
    and determines whether the URL is allowed to be crawled according to the rules defined in the
    file. It considers the `Disallow` and `Allow` directives for the user-agent "*" (wildcard) in
    the robots.txt file.

    Parameters:
    - url (str): The URL to check for crawling permission. The base URL of this URL is used to
      retrieve the robots.txt file.

    Returns:
    - bool: Returns `True` if crawling is allowed for the given URL based on the rules in
      the robots.txt file, and `False` if it is disallowed. If an error occurs or the robots.txt
      file is not accessible, it defaults to returning `True`.

    Raises:
    - HTTPException: Raises an HTTPException if an error occurs while fetching or
      processing the robots.txt file.
    """

    try:
        base_url = get_base_url(url)
        response = requests.get(urljoin(base_url, "robots.txt"), timeout=FETCH_TIMEOUT)
        response.raise_for_status()

        if response.status_code == OK:
            rules = get_crawling_rules(response.text)
            disallow_paths = rules.get("Disallow", [])

            if not disallow_paths:
                return True

            for disallow_path in disallow_paths:
                if disallow_path in url:
                    return False

            return True

        return True
    except RequestException:
        return True


def validate_url(url: str):
    """
    Validates the given URL and checks if crawling is allowed.

    Parameters:
    - url (str): The URL to validate.

    Raises:
    - HTTPException: If the URL is invalid or crawling is not allowed.
    """

    if not is_url_valid(url):
        raise HTTPException(status_code=BAD_REQUEST, detail="Invalid URL format")
    if not is_crawling_allowed(url):
        raise HTTPException(status_code=FORBIDDEN, detail="URL is not crawlable")


def remove_unwanted_tags(parsed_html: BeautifulSoup):
    """
    Removes unwanted HTML tags from the parsed HTML content.

    This function decomposes specific HTML tags such as `<script>`, `<noscript>`, and `<head>` from
    the parsed HTML content. These tags are typically not needed when extracting the main content of
    a webpage, and removing them helps clean up the HTML for further processing.

    Parameters:
    - parsed_html (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content
      from which unwanted tags will be removed.

    Returns:
    - None: The function modifies the `parsed_html` object in place by removing the specified tags.
    """

    for tag in parsed_html(["script", "noscript", "head"]):
        tag.decompose()


def format_markdown_headings(element_type: str, element_text: str):
    markdown = ""

    if element_type == "h1":
        markdown = f"# {element_text}"
    elif element_type == "h2":
        markdown = f"## {element_text}"
    elif element_type == "h3":
        markdown = f"### {element_text}"
    elif element_type == "h4":
        markdown = f"#### {element_text}"
    elif element_type == "h5":
        markdown = f"##### {element_text}"
    elif element_type == "h6":
        markdown = f"###### {element_text}"

    return markdown


def format_markdown_lists(element: BeautifulSoup, element_type: str):
    markdown = ""

    if element_type in ["ul", "ol"]:
        li_elements = element.find_all("li")
        list_markdown = []
        list_type_markdown = "-"

        for i, li in enumerate(li_elements):
            li_text = li.get_text().strip()

            if element_type == "ol":
                list_type_markdown = f"{i + 1}."

            if li_text:
                list_markdown.append(f"{list_type_markdown} {li_text}")

        markdown = "\n".join(list_markdown)

    return markdown


def format_markdown_tables(element: BeautifulSoup, element_type: str):
    markdown = ""

    if element_type == "table":
        rows = element.find_all("tr")
        table_markdown = []

        for i, row in enumerate(rows):
            cells = row.find_all(["th", "td"])
            cell_texts = [cell.get_text(strip=True) for cell in cells]

            if i == 0:
                table_markdown.append("| " + " | ".join(cell_texts) + " |")
                table_markdown.append(
                    "| " + " | ".join("---" for _ in cell_texts) + " |"
                )
            else:
                table_markdown.append("| " + " | ".join(cell_texts) + " |")

        markdown = "\n".join(table_markdown)

    return markdown


def format_markdown(element: BeautifulSoup, url: str):
    """
    Converts a given HTML element into its corresponding Markdown format based on its type.

    This function takes a BeautifulSoup element and its type (such as heading, paragraph, link,
    or list) and converts it to the appropriate Markdown syntax. It supports headings (h1 to h6),
    paragraphs, links, and unordered/ordered lists.

    Parameters:
    - element (BeautifulSoup): The BeautifulSoup element representing the HTML content to
      be formatted.
    - element_type (str): The type of HTML element (e.g., "h1", "h2", "p", "a", "ul", "ol").

    Returns:
    - str: The element's content formatted as a Markdown string.
    """

    element_text = element.get_text().strip()
    element_type = element.name
    markdown = ""
    heading_elements = ["h1", "h2", "h3", "h4", "h5", "h6"]

    if element_type == "table":
        markdown = format_markdown_tables(element, element_type)
    elif element_type in heading_elements:
        markdown = format_markdown_headings(element_type, element_text)
    elif element_type in ["ol", "ul"]:
        markdown = format_markdown_lists(element, element_type)
    elif element_type == "a":
        base_url = get_base_url(url)
        resolved_url = urljoin(base_url, element.get("href"))
        markdown = f"[{element_text}]({resolved_url})"
    elif element_type in ["p", "span", "div", "sup", "sub"]:
        markdown = element_text
    elif element_type in ["strong", "b"]:
        markdown = f"**{element_text}**"
    elif element_type in ["em", "i"]:
        markdown = f"*{element_text}*"
    elif element_type == "blockquote":
        markdown = f"> {element_text}"
    elif element_type in ["del", "s"]:
        markdown = f"~~{element_text}~~"
    elif element_type == "pre":
        markdown = f"```\n{element_text}\n```"
    elif element_type == "code":
        markdown = f"`{element_text}`"

    return markdown.strip()


def get_parsed_html(url: str):
    """
    Fetches and parses the HTML content of the given URL.

    This function retrieves the raw HTML content of the specified URL, then
    parses it using BeautifulSoup with the "html.parser" parser.

    Parameters:
    - url (str): The URL of the page to fetch and parse.

    Returns:
    - BeautifulSoup: A BeautifulSoup object containing the parsed HTML content of the page.
    """

    return BeautifulSoup(get_html_content(url), "html.parser")


def chunk_text(text: str, chunk_size: int = 1000, overlap: float = 0.1):
    """
    Split text into chunks of a specified size with a given percentage of overlap.

    Parameters:
        text (str): The text to chunk.
        chunk_size (int): The number of words per chunk.
        overlap (float): The percentage of overlap between consecutive chunks.

    Returns:
        List[str]: A list of text chunks.
    """
    words = text.split()
    overlap_size = int(chunk_size * overlap)
    chunks = []

    for i in range(0, len(words), chunk_size - overlap_size):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words):
            break

    return chunks
