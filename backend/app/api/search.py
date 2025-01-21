"""
Module for interacting with the Brave Search API.

This module provides a function `get_brave_search_results` to send a search query to the Brave
Search API and retrieve the search results in JSON format. It handles error cases, such as missing
API keys or failed requests, and raises appropriate HTTP exceptions.

Dependencies:
- `requests`: For making HTTP requests to the Brave Search API.
- `dotenv`: For loading environment variables from a `.env` file.
- `fastapi`: For raising HTTP exceptions in the event of errors.

Functions:
- `get_brave_search_results(query: str)`: Sends a GET request to the Brave Search API with the
  given query and returns the search results in JSON format. Raises HTTP exceptions on failure.

Environment Variables:
- `SECRET_BRAVE_KEY`: The subscription token for authenticating with the Brave Search API.

Constants:
- `INTERNAL_SERVER_ERROR`: HTTP status code for internal server errors.
- `FETCH_TIMEOUT`: Timeout duration for the requests.
- `OK`: HTTP status code for a successful request.
"""

import os
from dotenv import load_dotenv
import requests
from requests import RequestException
from fastapi import HTTPException
from app.lib.constants import INTERNAL_SERVER_ERROR, FETCH_TIMEOUT, OK

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
brave_key = os.getenv("SECRET_BRAVE_KEY")


def get_brave_search_results(query: str):
    """
    Fetches search results from the Brave Search API using the provided query.

    This function sends a GET request to the Brave Search API with the specified search query
    and returns the results in JSON format. It includes error handling to raise appropriate
    HTTP exceptions if the request fails or if the API key is missing.

    Parameters:
    - query (str): The search query to be passed to the Brave Search API.

    Returns:
    - dict: The JSON response from the Brave Search API containing the search results.

    Raises:
    - HTTPException: If the API key is missing, the API request fails, or any other error occurs
      during the request.
    """

    if not brave_key:
        raise HTTPException(
            status_code=INTERNAL_SERVER_ERROR, detail="Something went wrong"
        )

    base_url = "https://api.search.brave.com/res/v1/web/search"
    params = {"q": query}
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": brave_key,
    }

    try:
        response = requests.get(
            base_url, params=params, headers=headers, timeout=FETCH_TIMEOUT
        )

        if response.status_code == OK:
            return response.json()

        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to fetch from Brave Search, status code {response.status_code}",
        )
    except RequestException as error:
        raise HTTPException(
            status_code=INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while requesting Brave Search: {str(error)}",
        ) from error
