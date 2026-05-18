"""
MongoDB connection and helper functions.
Used for bulk data storage from OpenAlex (universities, academics).
SQLite remains for the main UI; MongoDB handles large-scale data sync.
"""

import os

from pymongo import MongoClient
from pymongo.database import Database

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "akademik_ai")


def get_mongo_client() -> MongoClient:
    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)


def get_mongo_db() -> Database:
    client = get_mongo_client()
    return client[MONGO_DB_NAME]


def init_mongo_indexes():
    """Create indexes for efficient querying."""
    db = get_mongo_db()

    # Universities collection
    db.universities.create_index("openalex_id", unique=True, sparse=True)
    db.universities.create_index("name")
    db.universities.create_index("city")
    db.universities.create_index("country_code")

    # Academics collection
    db.academics.create_index("openalex_id", unique=True, sparse=True)
    db.academics.create_index("name")
    db.academics.create_index("university_openalex_id")
    db.academics.create_index([("name", "text")])

    # Publications collection
    db.publications.create_index("openalex_id", unique=True, sparse=True)
    db.publications.create_index("author_openalex_ids")
    db.publications.create_index("institution_openalex_ids")
    db.publications.create_index("year")
    db.publications.create_index("doi", sparse=True)
    db.publications.create_index([("title", "text")])

    # Sync status collection
    db.sync_status.create_index("sync_type", unique=True)

    print("[MongoDB] Indexes created.")


def get_sync_status(sync_type: str) -> dict:
    """Get the last sync status for resume capability."""
    db = get_mongo_db()
    status = db.sync_status.find_one({"sync_type": sync_type})
    return status or {}


def update_sync_status(sync_type: str, data: dict):
    """Update sync status for resume capability."""
    db = get_mongo_db()
    db.sync_status.update_one(
        {"sync_type": sync_type},
        {"$set": data},
        upsert=True,
    )
