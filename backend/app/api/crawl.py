"""
This module provides functionality to crawl web pages, extract and format content in
Markdown, and recursively crawl linked pages up to a specified depth. It respects
robots.txt rules for crawling and introduces random delays between requests to avoid
overloading the server.

Key functions include:
- Crawling a webpage and extracting relevant content in Markdown format.
- Recursively crawling linked pages while gathering metadata.
- Extracting valid URLs from a given page.
- Handling exceptions related to crawling and content retrieval.

Modules used:
- `urllib.parse`: For URL parsing and resolving relative links.
- `time`: For sleeping between requests to avoid overwhelming the server.
- `datetime`: For tracking when pages were last crawled.
- `fastapi.HTTPException`: For raising HTTP exceptions on errors.

Constants:
- `CRAWL_DELAY`: Time in seconds to wait between requests.

Functions:
- `get_parsed_page_content(url: str)`: Crawls the provided URL and extracts the relevant 
  content in Markdown format.
- `get_parsed_website_content(url: str, visited_urls: set | None = None, depth=2)`: Recursively 
  crawls a website from the given URL, retrieving and formatting content up to the specified depth.
- `get_page_urls(url: str)`: Extracts and returns a list of valid URLs found on the provided page.
"""

import os
from urllib.parse import urljoin, urlparse
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from fastapi import HTTPException
from openai import OpenAI
from app.lib.constants import CRAWL_DELAY, INTERNAL_SERVER_ERROR
from app.lib.db import add_page_to_collection, create_or_get_database_collection
from app.lib.utils import (
    format_markdown,
    is_url_valid,
    remove_unwanted_tags,
    get_parsed_html,
)

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

client = OpenAI(
    api_key=os.getenv("SECRET_OPENAI_KEY"),
)


def get_parsed_page_content(url: str):
    """
    Crawls the provided URL and extracts the relevant content in Markdown format.

    This function retrieves the HTML content of the given URL, parses it using BeautifulSoup,
    removes unwanted tags, and extracts the text content from the relevant HTML elements.

    Parameters:
    url (str): The URL of the page to be crawled and parsed.

    Returns:
    dict: A dictionary with the following structure:
          - 'title' (str): The title of the page.
          - 'content' (str): The extracted content formatted as Markdown.

    Raises:
    HTTPException: If an error occurs during the crawling or parsing process,
                   an HTTPException is raised with an appropriate error message.
    """
    try:
        parsed_html = get_parsed_html(url)
        title = "No Title"
        extracted_markdown = []
        irrelevant_elements = [
            "script",
            "noscript",
            "head",
            "svg",
            "input",
            "label",
            "button",
            "img",
            "select",
        ]

        if parsed_html.title:
            title = parsed_html.title.get_text(strip=True)

        for tag in parsed_html.find_all(irrelevant_elements):
            tag.decompose()

        cleaned_html = str(parsed_html)

        openai_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant named MinitronAI, tasked with cleaning 
                    HTML content based on specific rules. 
                    Your task is to extract only the relevant elements from the HTML, which include text-based elements and inline anchor tags (a). You must:
                    1. Retain elements like paragraphs (p), inline code (code), preformatted code blocks (pre), bold (b), emphasis (em), blockquote, tables, ordered and unordered lists (ol, ul), headings (h1 to h6), and links (a) when they are inline (i.e., part of text content).
                    2. Remove any unnecessary container elements that do not contain text themselves but might contain text within their children. For example, remove a <div> that only holds other elements and not text directly.
                    3. For anchor tags (a), remove them if they are not inline with text, i.e., if they are part of navigation lists or inside list items (li), unless they are part of actual content, such as references or citations.
                    4. Only retain the href attribute from anchor tags, discarding other attributes. Remove entire anchor tags if they do not have relevant text within them or if they are not inline.
                    5. Retain other relevant tags like <strong>, <sub>, <sup>, <del>, and <s> where appropriate, based on their semantic meaning.
                    6. If an element contains empty text (i.e., only whitespace), remove it.
                    7. If headings (h1-h6) are used for navigation purposes, especially in lists, remove them.
                    8. Ensure that all retained content is clean and properly formatted, removing unnecessary attributes or extraneous content.

                    After processing the HTML, return a clean version where:
                    - Unnecessary elements are removed.
                    - Inline links are retained with only their href.
                    - Headings that are part of navigation are discarded.
                    - Text elements are kept intact, with no unnecessary containers or irrelevant attributes.

                    The final output should be in plain HTML string format with only the 
                    cleaned relevant elements. The text should be properly stripped of any 
                    extra spaces or unwanted attributes.""",
                },
                {
                    "role": "user",
                    "content": f"Here is the HTML content to clean: {cleaned_html}",
                },
            ],
        )

        cleaned_html_from_openai = openai_response.choices[0].message.content
        parsed_cleaned_html = BeautifulSoup(cleaned_html_from_openai, "html.parser")

        for element in parsed_cleaned_html.find_all():
            print("before markdown")
            markdown_output = format_markdown(element, url)
            print("after markdown")

            if markdown_output.strip():
                print("before append")
                extracted_markdown.append(markdown_output)
                print("after append")

        page_content = "\n\n".join(extracted_markdown)
        metadata = {
            "url": url,
            "title": title,
            "word_count": len(page_content.split()),
            "last_crawled": datetime.now().strftime("%Y-%m-%d"),
        }
        collection = create_or_get_database_collection(url, "USER")
        add_page_to_collection(collection, page_content, metadata)

        return page_content
    except Exception as error:
        raise HTTPException(
            status_code=INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse page content: {error}",
        ) from error


def get_parsed_website_content(url: str, max_depth=3, omit_url_keywords=None):
    """
    Crawls a website starting from the given URL, retrieving and formatting content
    from linked pages up to the specified maximum depth.

    Parameters:
    url (str): The URL to start crawling from.
    max_depth (int, optional): The maximum depth to crawl. Defaults to 3.
    omit_url_keywords (list of str, optional): A list of keywords. If any keyword is found
        in a URL, that URL will be excluded from crawling. Defaults to None.

    Returns:
    list: A list of dictionaries containing the crawled page content and metadata:
        - "content": The page content.
        - "metadata": Includes "url", "title", "word_count", "last_crawled", and "depth".

    Raises:
    HTTPException: If the URL is not allowed to be crawled.
    """

    urls_to_crawl = {url}
    visited_urls = set()
    crawled_data = []
    omit_url_keywords = omit_url_keywords or []
    base_path = urlparse(url).path.rstrip("/")

    for _ in range(max_depth + 1):
        new_urls_to_crawl = set()

        for current_url in urls_to_crawl:
            if current_url not in visited_urls:
                sleep(CRAWL_DELAY)

                page_content = get_parsed_page_content(current_url)
                visited_urls.add(current_url)
                crawled_data.append(page_content)

                for link in get_page_urls(current_url):
                    parsed_link = urlparse(link)

                    if (
                        parsed_link.path.startswith(base_path)
                        and link not in visited_urls
                        and link not in new_urls_to_crawl
                        and is_url_valid(link)
                        and not any(keyword in link for keyword in omit_url_keywords)
                    ):
                        new_urls_to_crawl.add(link)

        urls_to_crawl = new_urls_to_crawl

    return crawled_data


def get_page_urls(url: str):
    """
    Extracts and returns a list of valid URLs found on the provided page.

    This function retrieves the HTML content of the page, parses it, and extracts all
      anchor (`<a>`) tags.
    It filters out URLs that are fragments (i.e., contain `#`), relative paths,
      or invalid links.
    It resolves relative URLs to absolute ones and ensures that only links within the
      same domain are included.

    Parameters:
    - url (str): The URL of the page to crawl and extract links from.

    Returns:
    - list: A list of valid URLs found on the page. The list includes the provided
      URL as the first element.

    Raises:
    - HTTPException: If an error occurs while retrieving or parsing the page content,
      an HTTPException is raised with status code 500 and an error message.
    """

    try:
        parsed_html = get_parsed_html(url)
        link_urls = [url]

        remove_unwanted_tags(parsed_html)

        for element in parsed_html.find_all("a"):
            link_url = element.get("href")

            if link_url:
                has_fragment = "#" in link_url
                has_relative_current_path = link_url.startswith("./")
                has_relative_backwards_path = link_url.startswith("../")

                if (
                    has_fragment
                    or has_relative_current_path
                    or has_relative_backwards_path
                ):
                    continue

                resolved_url = urljoin(url, link_url)

                if urlparse(resolved_url).netloc == urlparse(url).netloc:
                    link_urls.append(resolved_url)

        return link_urls
    except Exception as error:
        raise HTTPException(
            status_code=INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve URLs: {error}",
        ) from error
