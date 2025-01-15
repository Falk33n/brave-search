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
- `random`: For introducing random crawl delays.
- `urllib.parse`: For URL parsing and resolving relative links.
- `time`: For sleeping between requests to avoid overwhelming the server.
- `datetime`: For tracking when pages were last crawled.
- `fastapi.HTTPException`: For raising HTTP exceptions on errors.

Constants:
- `MIN_CRAWL_DELAY`: Minimum time in seconds to wait between requests.
- `MAX_CRAWL_DELAY`: Maximum time in seconds to wait between requests.

Functions:
- `get_parsed_page_content(url: str)`: Crawls the provided URL and extracts the relevant 
  content in Markdown format.
- `get_parsed_website_content(url: str, visited_urls: set | None = None, depth=2)`: Recursively 
  crawls a website from the given URL, retrieving and formatting content up to the specified depth.
- `get_page_urls(url: str)`: Extracts and returns a list of valid URLs found on the provided page.
"""

import random
from urllib.parse import urljoin, urlparse
from time import sleep
from datetime import datetime
from fastapi import HTTPException
from app.utils import (
    format_markdown,
    is_crawling_allowed,
    is_url_valid,
    remove_unwanted_tags,
    get_parsed_html,
)
from app.constants import (
    INTERNAL_SERVER_ERROR,
    PARSE_PAGE_ERROR,
    CRAWLING_DISALLOWED_ERROR,
    FORBIDDEN,
    MIN_CRAWL_DELAY,
    MAX_CRAWL_DELAY,
    RETRIEVE_URLS_ERROR,
)


def get_parsed_page_content(url: str):
    """
    Crawls the provided URL and extracts the relevant content in Markdown format.

    This function retrieves the HTML content of the given URL, parses it using BeautifulSoup,
    removes unwanted tags, and extracts the text content from the relevant HTML elements
    (such as paragraphs, headings, lists, and links). The extracted content is returned as
    a dictionary containing the page's title and the formatted Markdown content.

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
        relevant_elements = [
            "p",
            "div",
            "span",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ul",
            "ol",
            "a",
        ]

        if parsed_html.title:
            title = parsed_html.title.get_text()

        remove_unwanted_tags(parsed_html)

        for relevant_element in relevant_elements:
            for element in parsed_html.find_all(relevant_element):
                extracted_markdown.append(format_markdown(element, relevant_element))

        return {"title": title, "content": "\n\n".join(extracted_markdown)}
    except Exception as error:
        raise HTTPException(
            status_code=INTERNAL_SERVER_ERROR,
            detail=f"{PARSE_PAGE_ERROR} {error}",
        ) from error


def get_parsed_website_content(url: str, visited_urls: set | None = None, depth=2):
    """
    Crawls a website starting from the given URL, recursively retrieving and formatting
    content from linked pages up to the specified depth.

    Parameters:
    url (str): The URL to start crawling from.
    visited_urls (set, optional): A set of already crawled URLs. Defaults to None.
    depth (int, optional): The depth of the crawl. Defaults to 2.

    Returns:
    list: A list of dictionaries containing the crawled content and
      metadata (title, word count, etc.)

    Raises:
    HTTPException: If crawling is disallowed for the URL.

    Notes:
    - The crawl respects robots.txt and introduces a random delay between requests.
    """

    if visited_urls is None:
        visited_urls = set()
    if depth == 0 or url in visited_urls:
        return []

    sleep(random.uniform(MIN_CRAWL_DELAY, MAX_CRAWL_DELAY))

    visited_urls.add(url)
    page_content = get_parsed_page_content(url)
    metadata = {
        "url": url,
        "title": page_content["title"],
        "word_count": len(page_content["content"].split()),
        "last_crawled": datetime.now().strftime("%Y-%m-%d"),
        "depth": depth,
    }
    crawled_data = [{"content": page_content["content"], "metadata": metadata}]

    if not is_crawling_allowed(url):
        raise HTTPException(
            status_code=FORBIDDEN, detail=f"{CRAWLING_DISALLOWED_ERROR} {url}"
        )

    for link in get_page_urls(url):
        if link not in visited_urls and is_url_valid(link):
            crawled_data.extend(
                get_parsed_website_content(link, visited_urls, depth - 1)
            )

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
            detail=f"{RETRIEVE_URLS_ERROR} {error}",
        ) from error
