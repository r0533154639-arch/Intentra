from __future__ import annotations

from typing import Any

from pymongo.collection import Collection


class MongoRepository:
    def __init__(self, collection: Collection[dict[str, Any]]):
        self.collection = collection

    def insert(self, document: dict[str, Any]) -> None:
        self.collection.insert_one(document)

    def get_by_query(self, query: dict[str, Any]) -> dict[str, Any] | None:
        return self.collection.find_one(query)

    def list_by_query(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return list(self.collection.find(query or {}))

    def upsert(self, query: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
        values = {key: value for key, value in document.items() if key != "_id"}
        update: dict[str, Any] = {"$set": values}
        if "_id" in document and "_id" not in query:
            update["$setOnInsert"] = {"_id": document["_id"]}
        self.collection.update_one(query, update, upsert=True)
        result = self.collection.find_one(query)
        if result is None:
            raise RuntimeError("MongoDB upsert completed without a matching document")
        return result

    def update(self, query: dict[str, Any], update: dict[str, Any]) -> bool:
        return self.collection.update_one(query, {"$set": update}).matched_count == 1

    def delete(self, query: dict[str, Any]) -> bool:
        return self.collection.delete_one(query).deleted_count == 1
