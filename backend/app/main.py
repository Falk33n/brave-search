"""
Module for handling web crawling API endpoints using FastAPI.

This module defines an API with endpoints for crawling and retrieving content from web pages
and websites. It uses the `CrawlPageRequest` and `CrawlWebsiteRequest` Pydantic 
models for request validation and provides functions to retrieve parsed content and 
URLs from the provided URLs.

Endpoints:
- /crawl-page: Crawls a single page and returns its parsed content.
- /crawl-urls: Crawls a single page and returns the list of URLs found on that page.
- /crawl-website: Crawls a website starting from the provided URL and retrieves its parsed content
  up to the specified depth.

Classes:
- CrawlPageRequest: A Pydantic model representing a request to crawl a page with a URL.
- CrawlWebsiteRequest: A Pydantic model that extends `CrawlPageRequest` and adds 
  an optional `depth` parameter to specify how deep the crawler should explore linked pages.

Usage:
- This module allows users to submit requests to crawl web pages and websites 
  via the FastAPI framework. It performs URL validation and content extraction, 
  ensuring that the crawled data is properly parsed and formatted.
"""

from pydantic import BaseModel
from fastapi import FastAPI
from app.utils import validate_url
from app.crawl import get_parsed_website_content, get_parsed_page_content, get_page_urls


api = FastAPI()


class CrawlPageRequest(BaseModel):
    """
    Represents a request to crawl a page, containing the URL to be crawled.

    This class is used to validate and parse the incoming request body for the `/crawl-page`
    endpoint. It ensures that the request includes a valid URL.

    Attributes:
    - url (str): The URL of the page to crawl.

    """

    url: str


@api.post("/crawl-page")
async def crawl_page(request: CrawlPageRequest):
    """
    Crawls the provided URL and returns the parsed content of the page.

    This function validates the provided URL and checks if crawling is allowed. If the URL is valid
    and crawling is permitted, it proceeds to extract and return the parsed content of the page.

    Parameters:
    - request (CrawlPageRequest): The request body containing the URL to crawl.

    Returns:
    - A dict with the parsed content of the page in a suitable format and the metadata of the page.
    """

    validate_url(request.url)
    return get_parsed_page_content(request.url)


@api.post("/crawl-urls")
async def crawl_urls(request: CrawlPageRequest):
    """
    Crawls the provided URL and returns a list of URLs found on the page.

    This function validates the provided URL and checks if crawling is allowed. If the URL is valid
    and crawling is permitted, it proceeds to extract and return the URLs found on the page.

    Parameters:
    - request (CrawlPageRequest): The request body containing the URL to crawl.

    Returns:
    - list: A string list of URLs found on the page.
    """

    validate_url(request.url)
    return get_page_urls(request.url)


class CrawlWebsiteRequest(CrawlPageRequest):
    """
    Represents a request to crawl a website with a specified depth.

    This class extends `CrawlPageRequest` and adds an optional `depth` attribute, which indicates
    how many levels deep the crawler should explore when processing the provided URL. The default
    value for depth is 2.

    Attributes:
    - url (str): The URL of the website to be crawled.
    - depth (int): The depth (or number of levels) the crawler should explore within the website.
      Defaults to 2 if not specified.

    Usage:
    - This class is used as the request body for the `/crawl-website` endpoint to define the URL
      and crawling depth.
    """

    depth: int = 2


@api.post("/crawl-website")
async def crawl_website(request: CrawlWebsiteRequest):
    """
    Crawls a website starting from the provided URL and retrieves its parsed content.

    This function validates the provided URL, checks if crawling is allowed, and then crawls the
    website to extract the relevant content, based on the specified depth.

    Parameters:
    - request (CrawlWebsiteRequest): The request body containing the URL and the optional depth
      parameter. The depth specifies how deep the crawler should go to explore linked pages.

    Returns:
    - A list containing dicts containing the parsed content of the website, which may
      include text, links, or other relevant data from the crawled pages.
    """

    validate_url(request.url)
    return get_parsed_website_content(request.url, request.depth)
