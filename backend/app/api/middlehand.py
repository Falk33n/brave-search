"""
This module provides functionality to fetch search result analysis from 
OpenAI's GPT-4 model.

It includes the following key functionality:
1. Loading the OpenAI API key from a `.env` file.
2. Defining a function `get_openai_search_analysis` to fetch an analysis of search results 
  based on a query and previous chat history.
3. Communicating with OpenAI's API to generate an analysis of the search results, which 
  includes summarizing relevant information, highlighting useful links, and providing suggestions.

Modules:
- `os`: For interacting with the environment and file paths.
- `typing`: Provides `List` and `Dict` types for type hinting.
- `dotenv`: To load environment variables from a `.env` file.
- `openai`: The OpenAI Python client library to interact with GPT-4.
- `fastapi`: Provides the `HTTPException` for error handling in case of 
  issues with the OpenAI request.
- `app.lib.constants`: Contains constants for error handling like `INTERNAL_SERVER_ERROR`.

Functions:
- `get_openai_search_analysis`: 
  - This function constructs a series of messages, including a system message, 
    previous chat history (excluding the latest message), and a user message with 
    the query and search results.
  - It sends these messages to OpenAI's GPT-4 model and returns the analysis of the search results.

Raises:
- `HTTPException`: If there is an error during the OpenAI request or if the 
  process encounters any issue.
"""

import os
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import HTTPException
from app.lib.constants import INTERNAL_SERVER_ERROR

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

client = OpenAI(
    api_key=os.getenv("SECRET_OPENAI_KEY"),
)


def get_openai_search_analysis(
    query: str, search_results: dict, chat_history: List[Dict[str, str]]
):
    """
    Fetches an analysis of search results from OpenAI based on the user's query
    and previous chat history.

    This function constructs a series of messages for the OpenAI API, including a
    system prompt that describes the assistant's task, the previous chat history
    (excluding the last message), and a user prompt containing the search query and its
    associated search results. It sends the request to OpenAI's GPT-4 model and returns
    the analysis result.

    Parameters:
    - query (str): The search query provided by the user.
    - search_results (dict): The search results in JSON format from a search engine, to be analyzed.
    - chat_history (List[Dict[str, str]]): A list of previous chat messages between the
      user and the assistant,
      with each message represented as a dictionary containing 'role' and 'content' keys.

    Returns:
    - str: The OpenAI-generated analysis of the search results.

    Raises:
    - HTTPException: If there is an error with the OpenAI request or any other
      issue during the process.
    """

    try:
        openai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant whose name is MinitronAI. 
                      You are tasked with analyzing search results and providing meaningful 
                      insights or answers. Based on the user's query and the provided 
                      results: 
                      1. Summarize the most relevant information. 
                      2. Highlight any useful links. 
                      3. Provide additional suggestions or insights if necessary.""",
                },
                *chat_history[:-1],
                {
                    "role": "user",
                    "content": f"""The search query was: '{query}'. Here are the search 
                      results in JSON format: {search_results}""",
                },
            ],
        )

        return openai_response.choices[0].message.content
    except Exception as error:
        raise HTTPException(
            status_code=INTERNAL_SERVER_ERROR,
            detail=f"Error fetching OpenAI response: {str(error)}",
        ) from error
