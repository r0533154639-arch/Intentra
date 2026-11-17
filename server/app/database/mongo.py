from functools import lru_cache
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app.core.config import get_settings


@lru_cache
def get_mongo_client() -> MongoClient[dict[str, Any]]:
    settings = get_settings()
    return MongoClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=settings.mongo_server_selection_timeout_ms,
        tz_aware=True,
    )


def get_database() -> Database[dict[str, Any]]:
    settings = get_settings()
    return get_mongo_client().get_database(settings.mongo_db_name)


def get_collection(name: str) -> Collection[dict[str, Any]]:
    return get_database().get_collection(name)


def verify_mongo_connection() -> None:
    get_mongo_client().admin.command("ping")


def close_mongo_connection() -> None:
    if get_mongo_client.cache_info().currsize:
        get_mongo_client().close()
        get_mongo_client.cache_clear()
