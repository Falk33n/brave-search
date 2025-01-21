from typing import List, Dict
import re
from pydantic import BaseModel
from fastapi import FastAPI, APIRouter
from app.lib.utils import validate_url
from app.api.crawl import (
    get_parsed_website_content,
    get_parsed_page_content,
    get_page_urls,
)
from app.lib.db import query_collection, create_or_get_database_collection
from app.api.search import get_brave_search_results
from app.api.middlehand import get_openai_search_analysis

app = FastAPI()
crawl_router = APIRouter(prefix="/crawl", tags=["Crawl API"])
chat_router = APIRouter(prefix="/chat", tags=["OpenAI Chat API"])
search_router = APIRouter(tags=["Brave Search API"])
query_router = APIRouter(tags=["ChromaDB Query API"])
middlehand_router = APIRouter(
    prefix="/middlehand", tags=["OpenAI Middlehand Assistant"]
)


class CrawlPageRequest(BaseModel):
    """
    Represents a request to crawl a page, containing the URL to be crawled.

    This class is used to validate and parse the incoming request body for the `/crawl/page`
    endpoint. It ensures that the request includes a valid URL.

    Attributes:
    - url (str): The URL of the page to crawl.

    """

    url: str


@crawl_router.post("/page")
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


@crawl_router.post("/urls")
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
    Represents a request to crawl a website starting from a given URL.

    Inherits:
    CrawlPageRequest: The base class containing common attributes for page crawling.

    Attributes:
    max_depth (int): The maximum depth to crawl. Defaults to 3.
      - Depth 0: Crawls the starting URL.
      - Depth 1: Crawls all URLs found on the starting URL.
      - Depth 2: Crawls URLs found on pages from depth 1, and so on.
    omit_url_keywords (list of str, optional): A list of keywords. If any keyword is found
      in a URL, that URL will be excluded from crawling. Defaults to None.
    """

    max_depth: int = 3
    omit_url_keywords: list[str] | None = None


@crawl_router.post("/website")
async def crawl_website(request: CrawlWebsiteRequest):
    """
    API endpoint to crawl a website starting from a given URL.

    This endpoint validates the input URL and initiates a crawling process up to the
    specified maximum depth, optionally excluding URLs containing specific keywords.

    Parameters:
    request (CrawlWebsiteRequest): The request body containing:
        - url (str): The starting URL for the crawl.
        - max_depth (int): The maximum depth to crawl. Defaults to 3.
        - omit_url_keywords (list of str, optional): A list of keywords to exclude from
          crawling. URLs containing any of these keywords will be skipped. Defaults to None.

    Returns:
    list: A list of dictionaries containing crawled page content and metadata.

    Raises:
    HTTPException: If the URL is invalid or crawling fails.
    """

    validate_url(request.url)
    return get_parsed_website_content(
        request.url, request.max_depth, request.omit_url_keywords
    )


class BraveSearchRequest(BaseModel):
    """
    Represents a request to fetch search results from the Brave Search API.

    This class is used to model the request payload for fetching search results from Brave Search,
    including the search query and the chat history. It is designed to be used with FastAPI to
    validate incoming request data.

    Attributes:
    - query (str): The search query to be passed to the Brave Search API.
    - chat_history (List[Dict[str, str]]): A list of previous chat messages, each represented as
      a dictionary with 'role' and 'content' keys, used to provide context for the assistant.

    Example:
    - query: "Python programming tutorials"
    - chat_history: [
        {"role": "user", "content": "Can you recommend Python tutorials?"},
        {"role": "assistant", "content": "Sure! Here are some tutorials..."}
      ]
    """

    query: str
    chat_history: List[Dict[str, str]]


@search_router.post("/search")
async def brave_search(request: BraveSearchRequest):
    """
    Endpoint to perform a search using Brave Search and analyze the results with OpenAI.

    This FastAPI endpoint receives a search query and chat history in the form of a POST request.
    It then fetches the search results from the Brave Search API and uses
    OpenAI to analyze the results, generating meaningful insights based on the query
    and the previous chat history.

    Parameters:
    - request (BraveSearchRequest): The request body containing the search query and chat history.
      The `query` field is the search query to be passed to Brave Search, and
      `chat_history` is a list of previous chat messages providing context.

    Returns:
    - str: The OpenAI-generated analysis of the Brave Search results, returned as the response.

    Raises:
    - HTTPException: If there is an error with the Brave Search request,
      OpenAI analysis, or any other issue during the process.
    """

    return get_openai_search_analysis(
        request.query, get_brave_search_results(request.query), request.chat_history
    )


class QueryRequest(CrawlPageRequest):
    query: str


@query_router.post("/query")
async def query_database(request: QueryRequest):
    collection = create_or_get_database_collection(request.url, "USER")
    url_pattern = r"https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    plain_query = re.sub(url_pattern, "", request.query)
    return query_collection(collection, plain_query)


app.include_router(crawl_router)
app.include_router(chat_router)
app.include_router(search_router)
app.include_router(middlehand_router)
app.include_router(query_router)
