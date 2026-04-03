"""
Audit Log Repository - Record all operations for compliance
"""
from datetime import datetime
from typing import Dict, Any, List
from services.repositories.base_repository import BaseRepository


class AuditLogRepository(BaseRepository):
    """Repository for audit log operations."""

    def __init__(self):
        """Initialize audit log repository."""
        super().__init__("audit_logs")

    def log_operation(self, worker_id: str, operation: str, entity_type: str,
                     entity_id: str, details: Dict[str, Any],
                     status: str = "Success") -> None:
        """
        Log an operation for audit trail.

        Args:
            worker_id: Worker ID
            operation: Operation name (e.g., "claim_created")
            entity_type: Type of entity (e.g., "claim", "payout")
            entity_id: ID of entity
            details: Operation details
            status: Status ("Success", "Failed", etc.)
        """
        log_entry = {
            "worker_id": worker_id,
            "operation": operation,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details,
            "timestamp": datetime.now(),
            "status": status,
        }
        self.create(log_entry)

    def get_worker_audit_logs(self, worker_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs for a worker."""
        return self.find_many(
            {"worker_id": worker_id},
            limit=limit,
            sort_field="timestamp",
            sort_order=-1
        )

    def get_logs_by_operation(self, operation: str, limit: int = 0) -> List[Dict[str, Any]]:
        """Get all logs for a specific operation."""
        return self.find_many(
            {"operation": operation},
            limit=limit,
            sort_field="timestamp",
            sort_order=-1
        )
