import os
from enum import Enum
from urllib.parse import urlparse
from dotenv import load_dotenv
from fastapi import HTTPException
from app.lib.constants import INTERNAL_SERVER_ERROR
from app.lib.utils import chunk_text
import chromadb
from openai import OpenAI


load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

openai_client = OpenAI(
    api_key=os.getenv("SECRET_OPENAI_KEY"),
)

chromadb_client = chromadb.PersistentClient(path="./chroma")


class Role(Enum):
    """
    Enum representing user roles within the system.

    This class defines the two possible roles a user can have:
    - USER: Represents a regular user with limited access and privileges.
    - ADMIN: Represents an administrator with elevated access and control.

    Attributes:
    - USER (str): The role for regular users.
    - ADMIN (str): The role for administrators.

    Usage:
    - Role.USER: Access the 'user' role.
    - Role.ADMIN: Access the 'admin' role.
    """

    USER = "user"
    ADMIN = "admin"


def create_or_get_database_collection(url: str, role: Role):
    parsed_url = urlparse(url)
    base_name = parsed_url.netloc
    collection_name = f"{role}_{f"{base_name}"}"

    try:
        return chromadb_client.get_or_create_collection(collection_name)
    except Exception as error:
        raise HTTPException(
            status_code=INTERNAL_SERVER_ERROR,
            detail=f"Error creating/retrieving collection: {str(error)}",
        ) from error


def add_page_to_collection(collection, page: str, page_metadata):
    try:
        text = page.replace("\n", " ")
        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            embeddings = (
                openai_client.embeddings.create(
                    input=[chunk], model="text-embedding-3-small"
                )
                .data[0]
                .embedding
            )
            chunk_metadata = {**page_metadata, "chunk_index": i}

            collection.add(
                documents=[chunk],
                embeddings=[embeddings],
                ids=[f"{page_metadata['url']}#chunk-{i}"],
                metadatas=[chunk_metadata],
            )
    except Exception as error:
        raise HTTPException(
            status_code=INTERNAL_SERVER_ERROR,
            detail=f"Error adding page to collection: {str(error)}",
        ) from error


def query_collection(collection, query, results=10):
    try:
        return collection.query(
            query_texts=[query], n_results=results, include=["documents", "metadatas"]
        )
    except Exception as error:
        raise HTTPException(
            status_code=INTERNAL_SERVER_ERROR,
            detail=f"Error querying collection: {str(error)}",
        ) from error
