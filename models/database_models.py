"""
Data Models for GigShield AI
Pydantic models for API and database operations
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================
class ClaimStatus(str, Enum):
    """Claim lifecycle statuses"""
    INITIATED = "Initiated"
    VALIDATED = "Validated"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    PAID = "Paid"
    REJECTED = "Rejected"
    FLAGGED = "Flagged"


class PayoutStatus(str, Enum):
    """Payout transaction statuses"""
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"


class FraudStatus(str, Enum):
    """Fraud assessment statuses"""
    CLEARED = "Cleared"
    SUSPICIOUS = "Suspicious"
    FLAGGED = "Flagged"


# ============================================================================
# WORKER MODELS
# ============================================================================
class WorkerProfileBase(BaseModel):
    """Base worker profile model"""
    name: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=50)
    delivery_zone: str = Field(..., min_length=1, max_length=50)
    avg_hourly_income: float = Field(..., gt=0, le=10000)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ramesh Kumar",
                "city": "Delhi",
                "delivery_zone": "North",
                "avg_hourly_income": 120.0
            }
        }


class WorkerProfileCreate(WorkerProfileBase):
    """Request model for worker registration"""
    pass


class WorkerProfile(WorkerProfileBase):
    """Complete worker profile with metadata"""
    worker_id: str
    kyc_status: str = "Verified"
    rating: float = Field(default=4.5, ge=0.0, le=5.0)
    total_deliveries: int = Field(default=0, ge=0)
    total_earnings: float = Field(default=0.0, ge=0)
    total_payouts: float = Field(default=0.0, ge=0)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# POLICY MODELS
# ============================================================================
class PolicyBase(BaseModel):
    """Base policy model"""
    worker_id: str
    weekly_premium: float = Field(..., gt=0)
    coverage_limit: float = Field(..., gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "worker_id": "W001",
                "weekly_premium": 30.0,
                "coverage_limit": 4800.0
            }
        }


class PolicyCreate(PolicyBase):
    """Request model for policy creation"""
    pass


class Policy(PolicyBase):
    """Complete policy with metadata"""
    policy_id: str
    start_date: datetime
    end_date: datetime
    active_status: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CLAIM MODELS
# ============================================================================
class ClaimEventInfo(BaseModel):
    """Event information for a claim"""
    event_type: str
    trigger_conditions: List[str]
    triggered_at: datetime


class ClaimBase(BaseModel):
    """Base claim model"""
    policy_id: str
    worker_id: str
    event_type: str
    trigger_conditions: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "policy_id": "P001",
                "worker_id": "W001",
                "event_type": "Heavy Rain",
                "trigger_conditions": ["rainfall > 50mm (65mm detected)"]
            }
        }


class ClaimCreate(ClaimBase):
    """Request model for claim creation"""
    disruption_hours: float = Field(..., gt=0, le=24)
    gps_movement_score: float = Field(default=2.0, ge=0, le=15)


class Claim(ClaimBase):
    """Complete claim with full lifecycle info"""
    claim_id: str
    claim_status: str = ClaimStatus.INITIATED
    fraud_score: float = Field(default=0.0, ge=0.0, le=100.0)
    fraud_status: str = FraudStatus.CLEARED
    estimated_loss: float = Field(default=0.0, ge=0)
    approved_payout: float = Field(default=0.0, ge=0)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PAYOUT MODELS
# ============================================================================
class PayoutBase(BaseModel):
    """Base payout model"""
    claim_id: str
    worker_id: str
    amount: float = Field(..., gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": "CLM001",
                "worker_id": "W001",
                "amount": 480.0
            }
        }


class PayoutCreate(PayoutBase):
    """Request model for payout creation"""
    pass


class Payout(PayoutBase):
    """Complete payout record"""
    payout_id: str
    status: str = PayoutStatus.PENDING
    upi_txn_id: Optional[str] = None
    timestamp: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# ZONE MODELS
# ============================================================================
class ZoneBase(BaseModel):
    """Base zone model"""
    zone_name: str = Field(..., min_length=1, max_length=50)
    city: str = Field(..., min_length=1, max_length=50)
    historical_risk_score: float = Field(..., ge=0.0, le=1.0)

    class Config:
        json_schema_extra = {
            "example": {
                "zone_name": "North",
                "city": "Delhi",
                "historical_risk_score": 0.8
            }
        }


class Zone(ZoneBase):
    """Complete zone record"""
    last_updated: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AUDIT LOG MODELS
# ============================================================================
class AuditLog(BaseModel):
    """Audit log entry"""
    worker_id: str
    operation: str
    entity_type: str  # "claim", "payout", "policy", etc.
    entity_id: str
    details: Dict[str, Any]
    timestamp: datetime
    status: str = "Success"  # "Success", "Failed", etc.

    class Config:
        from_attributes = True


# ============================================================================
# API RESPONSE MODELS
# ============================================================================
class RegistrationResponse(BaseModel):
    """Response for worker registration"""
    success: bool
    worker_id: str
    message: str
    worker_profile: WorkerProfile
    policy: Optional[Policy] = None


class ClaimResponse(BaseModel):
    """Response for claim operations"""
    success: bool
    claim_id: str
    message: str
    claim: Claim
    estimated_loss: float


class PayoutResponse(BaseModel):
    """Response for payout operations"""
    success: bool
    payout_id: str
    message: str
    amount: float
    upi_txn_id: Optional[str]
    timestamp: datetime


class DashboardData(BaseModel):
    """Aggregated dashboard data"""
    active_worker_count: int
    active_policy_count: int
    claims_processed_today: int
    claims_processed_week: int
    total_payouts: float
    success_rate_percent: float
    avg_claim_processing_hours: float
    recent_claims: List[Claim]
    recent_payouts: List[Payout]
    alerts: List[str]


# ============================================================================
# RISK & PREMIUM MODELS
# ============================================================================
class RiskAssessment(BaseModel):
    """Risk assessment result"""
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str  # "Low", "Medium", "High"
    top_risk_factor: str
    ai_confidence: float = Field(..., ge=0.0, le=1.0)


class PremiumCalculation(BaseModel):
    """Premium calculation result"""
    risk_score: float
    weekly_premium: float
    ai_recommendation: str


class EventDetectionResult(BaseModel):
    """Event detection result"""
    event_detected: bool
    event_type: Optional[str] = None
    trigger_conditions: List[str]
    severity: Optional[str] = None  # "Low", "Medium", "High"


# ============================================================================
# ERROR & STATUS MODELS
# ============================================================================
class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    api: str
    models: str
    timestamp: datetime
