"""
This module defines constants used throughout the application.

Constants include:
1. HTTP status codes: Standardized status codes for HTTP responses.
2. Error messages: Reusable error message strings for exceptions and logging.
3. Crawl settings: Parameters for controlling crawler behavior, such as delays and timeouts.

Constants:
----------
- HTTP Status Codes:
  - INTERNAL_SERVER_ERROR (int): Status code for server errors (500).
  - FORBIDDEN (int): Status code for forbidden requests (403).
  - OK (int): Status code for successful requests (200).
  - BAD_REQUEST (int): Status code for bad client requests (400).

- Error Messages:
  - CRAWLING_DISALLOWED_ERROR (str): Error message when crawling is disallowed for a URL.
  - PARSE_PAGE_ERROR (str): Error message when page content parsing fails.
  - RETRIEVE_URLS_ERROR (str): Error message when URL retrieval fails.
  - INVALID_URL_ERROR (str): Error message for invalid URL formats.
  - CRAWLING_NOT_ALLOWED_ERROR (str): Error message for URLs that are not crawlable.

- Crawler Settings:
  - CRAWL_DELAY (int): Delay (in seconds) between crawl requests.
  - FETCH_TIMEOUT (int): Timeout (in seconds) for fetching resources.

Usage:
------
Import this module wherever these constants are needed to maintain consistency
and avoid hardcoding values. For example:

    from app.constants import OK, FETCH_TIMEOUT

This helps ensure clean and maintainable code, especially in larger projects.

"""

INTERNAL_SERVER_ERROR = 500
FORBIDDEN = 403
OK = 200
BAD_REQUEST = 400

CRAWL_DELAY = 1

FETCH_TIMEOUT = 10
