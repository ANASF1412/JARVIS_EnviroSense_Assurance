"""
Base Repository - Generic CRUD operations for MongoDB collections
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pymongo.collection import Collection
from config.database import get_database


class BaseRepository:
    """Base repository class with common CRUD operations."""

    def __init__(self, collection_name: str):
        """Initialize repository with collection name."""
        self.db = get_database()
        self.collection: Collection = self.db[collection_name]

    def create(self, document: Dict[str, Any]) -> str:
        """
        Create a new document.

        Args:
            document: Document to insert

        Returns:
            Inserted document ID
        """
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def find_by_id(self, doc_id: str, id_field: str = "_id") -> Optional[Dict]:
        """
        Find document by ID.

        Args:
            doc_id: Document ID
            id_field: Field name to search (default: _id)

        Returns:
            Document or None
        """
        return self.collection.find_one({id_field: doc_id})

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict]:
        """
        Find one document by query.

        Args:
            query: MongoDB query

        Returns:
            Document or None
        """
        return self.collection.find_one(query)

    def find_many(self, query: Dict[str, Any], limit: int = 0, skip: int = 0,
                  sort_field: str = None, sort_order: int = -1) -> List[Dict]:
        """
        Find multiple documents.

        Args:
            query: MongoDB query
            limit: Number of documents to return (0 = no limit)
            skip: Number of documents to skip
            sort_field: Field to sort by
            sort_order: Sort order (-1 for descending, 1 for ascending)

        Returns:
            List of documents
        """
        cursor = self.collection.find(query)

        if sort_field:
            cursor = cursor.sort(sort_field, sort_order)

        if skip > 0:
            cursor = cursor.skip(skip)

        if limit > 0:
            cursor = cursor.limit(limit)

        return list(cursor)

    def find_all(self) -> List[Dict]:
        """
        Find all documents.

        Returns:
            List of all documents
        """
        return list(self.collection.find({}))

    def update(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False) -> bool:
        """
        Update document(s).

        Args:
            query: MongoDB query
            update: Update document (should use $set, $inc, etc.)
            upsert: Create if doesn't exist

        Returns:
            True if update was successful
        """
        result = self.collection.update_one(query, update, upsert=upsert)
        return result.modified_count > 0 or result.upserted_id is not None

    def update_by_id(self, doc_id: str, update_data: Dict[str, Any],
                     id_field: str = "_id") -> bool:
        """
        Update document by ID.

        Args:
            doc_id: Document ID
            update_data: Fields to update (without $set)
            id_field: Field name for ID

        Returns:
            True if successful
        """
        update_data["updated_at"] = datetime.now()
        return self.update(
            {id_field: doc_id},
            {"$set": update_data}
        )

    def update_many(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        Update multiple documents.

        Args:
            query: MongoDB query
            update: Update document

        Returns:
            Number of documents updated
        """
        result = self.collection.update_many(query, update)
        return result.modified_count

    def delete(self, query: Dict[str, Any]) -> bool:
        """
        Delete document(s).

        Args:
            query: MongoDB query

        Returns:
            True if document was deleted
        """
        result = self.collection.delete_one(query)
        return result.deleted_count > 0

    def delete_by_id(self, doc_id: str, id_field: str = "_id") -> bool:
        """
        Delete document by ID.

        Args:
            doc_id: Document ID
            id_field: Field name for ID

        Returns:
            True if successful
        """
        return self.delete({id_field: doc_id})

    def delete_many(self, query: Dict[str, Any]) -> int:
        """
        Delete multiple documents.

        Args:
            query: MongoDB query

        Returns:
            Number of documents deleted
        """
        result = self.collection.delete_many(query)
        return result.deleted_count

    def count(self, query: Dict[str, Any] = None) -> int:
        """
        Count documents.

        Args:
            query: MongoDB query (None = all documents)

        Returns:
            Document count
        """
        if query is None:
            query = {}
        return self.collection.count_documents(query)

    def exists(self, query: Dict[str, Any]) -> bool:
        """
        Check if document exists.

        Args:
            query: MongoDB query

        Returns:
            True if document exists
        """
        return self.collection.find_one(query) is not None

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict]:
        """
        Run aggregation pipeline.

        Args:
            pipeline: MongoDB aggregation pipeline

        Returns:
            Aggregation results
        """
        return list(self.collection.aggregate(pipeline))

    def bulk_insert(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple documents.

        Args:
            documents: List of documents to insert

        Returns:
            List of inserted IDs
        """
        if not documents:
            return []
        result = self.collection.insert_many(documents)
        return [str(doc_id) for doc_id in result.inserted_ids]

    def create_index(self, field_name: str, unique: bool = False):
        """
        Create index on field.

        Args:
            field_name: Field to index
            unique: Whether index should be unique
        """
        self.collection.create_index(field_name, unique=unique)

    def delete_index(self, field_name: str):
        """
        Delete index on field.

        Args:
            field_name: Field to remove index from
        """
        self.collection.drop_index(f"{field_name}_1")
