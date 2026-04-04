"""
JARVIS EnviroSense Assurance — Main Streamlit Application Entry Point
"""
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
def get_safe_mongodb_uri():
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    
    # If it's an Atlas URI with the unescaped @ in the password, fix it
    if "mongodb+srv://" in uri and "@" in uri.split("://")[1]:
        try:
            # Basic split to isolate user:pass and host
            prefix, rest = uri.split("://")
            userinfo_host = rest.split("/")[0]
            
            if "@" in userinfo_host:
                userinfo, host = userinfo_host.rsplit("@", 1)
                if ":" in userinfo:
                    username, password = userinfo.split(":", 1)
                    # Use quote_plus only if not already encoded
                    if "%" not in password:
                        encoded_pass = urllib.parse.quote_plus(password)
                        new_uri = f"{prefix}://{username}:{encoded_pass}@{host}/"
                        # Append any query params or DB name
                        if "/" in rest:
                            new_uri += rest.split("/", 1)[1]
                        return new_uri
        except Exception:
            pass # Fallback to original if parsing fails
            
    return uri

MONGODB_URI = get_safe_mongodb_uri()
DATABASE_NAME = os.getenv("DATABASE_NAME", "envirosense-assurance")

# ============================================================================
# ML MODEL PATHS
# ============================================================================
RISK_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "risk_model.pkl")
INCOME_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "income_model.pkl")

# ============================================================================
# BUSINESS LOGIC CONSTANTS
# ============================================================================
# Policy Configuration
POLICY_DURATION_DAYS = 7
HOURS_PER_WEEK_MAX = 40
COVERAGE_MULTIPLIER = HOURS_PER_WEEK_MAX

# Premium Calculation (Risk → Premium)
PREMIUM_LOW_RISK = 20.0      # risk < 0.3
PREMIUM_MID_RISK = 30.0      # risk 0.3-0.7
PREMIUM_HIGH_RISK = 45.0     # risk > 0.7

# Fraud Detection Thresholds
FRAUD_SCORE_THRESHOLD = 70.0  # Score above this → "Flagged"
MAX_REPEATED_CLAIMS_PER_WEEK = 3

# ============================================================================
# PARAMETRIC TRIGGER THRESHOLDS
# ============================================================================
RAINFALL_THRESHOLD_MM = 50.0      # Heavy Rain
TEMPERATURE_THRESHOLD_C = 42.0    # Heatwave
AQI_THRESHOLD = 300               # Severe Pollution

# ============================================================================
# EVENT TYPES
# ============================================================================
EVENT_TYPES = {
    "HEAVY_RAIN": {"name": "Heavy Rain", "code": "001"},
    "HEATWAVE": {"name": "Heatwave", "code": "002"},
    "POLLUTION": {"name": "Severe Pollution", "code": "003"},
    "CURFEW": {"name": "Government Curfew", "code": "004"},
    "FLOOD": {"name": "Flooding", "code": "005"},
}

# ============================================================================
# CLAIM STATUS FLOW
# ============================================================================
CLAIM_STATUSES = [
    "Initiated",
    "Validated",
    "Under Review",
    "Approved",
    "Paid",
    "Rejected",
    "Flagged"
]

CLAIM_STATUS_INITIAL = "Initiated"
CLAIM_STATUS_APPROVED = "Approved"
CLAIM_STATUS_PAID = "Paid"
CLAIM_STATUS_FLAGGED = "Flagged"
CLAIM_STATUS_REJECTED = "Rejected"

# ============================================================================
# PAYOUT STATUS FLOW
# ============================================================================
PAYOUT_STATUS_PENDING = "Pending"
PAYOUT_STATUS_COMPLETED = "Completed"
PAYOUT_STATUS_FAILED = "Failed"

# ============================================================================
# ZONE CONFIGURATION
# ============================================================================
DEFAULT_ZONES = [
    {"zone_name": "North", "city": "Delhi", "historical_risk_score": 0.8},
    {"zone_name": "South", "city": "Delhi", "historical_risk_score": 0.3},
    {"zone_name": "East", "city": "Delhi", "historical_risk_score": 0.5},
    {"zone_name": "West", "city": "Delhi", "historical_risk_score": 0.4},
    {"zone_name": "Central", "city": "Delhi", "historical_risk_score": 0.7},
]

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/envirosense.log")

# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================
STREAMLIT_PAGE_CONFIG = {
    "page_title": "JARVIS EnviroSense",
    "page_icon": "🛡️",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Theme colors (Enterprise professional palette)
COLORS = {
    "primary": "#1f3a93",        # Navy blue
    "secondary": "#5a6c7d",      # Slate gray
    "accent": "#0ea5a5",         # Teal
    "success": "#10b981",        # Green
    "warning": "#f59e0b",        # Amber
    "error": "#ef4444",          # Red
    "background": "#f9fafb",     # Light gray
    "surface": "#ffffff",        # White
    "text_primary": "#1f2937",   # Dark gray
    "text_secondary": "#6b7280", # Gray
}

# ============================================================================
# API CONFIGURATION
# ============================================================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "True").lower() == "true"

# ============================================================================
# FEATURE FLAGS
# ============================================================================
ENABLE_PREDICTIVE_ALERTS = True
ENABLE_ZONE_RISK = True
ENABLE_FRAUD_DETECTION = True
ENABLE_API_AUTH = False  # Set to True for production
