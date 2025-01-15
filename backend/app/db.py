"""
Module for handling database collections based on user roles and URLs.

This module defines the `Role` enum representing user roles in the system and a function,
`create_or_get_database_collection`, that interacts with a database to either create or retrieve
a collection based on the user's role and a provided URL.

Classes:
- Role: Enum class that defines two possible user roles in the system, 'USER' and 'ADMIN'.

Functions:
  `create_or_get_database_collection`: 
  - Creates or retrieves a database collection based on the provided URL and role.
  
  - Parameters:
    - database: The database instance.
    - url (str): The URL associated with the collection.
    - role (Role): The user role associated with the collection.
    - Returns:
      - collection: The database collection (either created or retrieved).
"""

from enum import Enum
from app.utils import get_base_url
import chromadb

client = chromadb.Client()


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


def create_or_get_database_collection(database, url: str, role: Role):
    """
    Creates or retrieves a database collection based on the provided URL and user role.

    This function first generates the collection name using the `get_collection_name` function,
    which combines the provided URL and role information. It then checks if the collection already
    exists in the database. If it does not exist, the collection is created. If it does exist,
    the existing collection is returned.

    Parameters:
    - database: The database instance where the collection will be created or retrieved from.
    - url (str): The URL associated with the collection, used to generate the collection name.
    - role (Role): The role associated with the collection, used to generate the collection name.

    Returns:
    - collection: The database collection, either newly created or existing.
    """

    collection_name = f"{role}_{f"{get_base_url(url)}"}"

    if collection_name not in database.list_collections():
        return database.create_collection(collection_name)

    return database.get_collection(collection_name)
