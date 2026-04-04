"""
MongoDB Database Connection & Setup
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ServerSelectionTimeoutError
import streamlit as st
import json
import os
from dateutil import parser
from config.settings import MONGODB_URI, DATABASE_NAME

# Singleton pattern for DB connection
_db_client = None
_database = None


def get_db_client():
    """Get or create MongoDB client connection."""
    global _db_client
    if _db_client is None:
        try:
            _db_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            _db_client.admin.command("ping")
        except ServerSelectionTimeoutError:
            print(f"ERROR: Could not connect to MongoDB at {MONGODB_URI}")
            raise
    return _db_client


def get_database():
    """Get database instance."""
    global _database
    if _database is None:
        client = get_db_client()
        _database = client[DATABASE_NAME]
    return _database


def close_db_connection():
    """Close MongoDB connection."""
    global _db_client, _database
    if _db_client is not None:
        _db_client.close()
        _db_client = None
        _database = None


def init_collections():
    """Initialize database collections with proper indexes."""
    db = get_database()

    # ========================================================================
    # WORKERS COLLECTION
    # ========================================================================
    if "workers" not in db.list_collection_names():
        db.create_collection("workers")

    workers_col = db["workers"]
    workers_col.create_index("worker_id", unique=True)
    workers_col.create_index("city")
    workers_col.create_index("delivery_zone")
    workers_col.create_index("created_at", background=True)

    # ========================================================================
    # POLICIES COLLECTION
    # ========================================================================
    if "policies" not in db.list_collection_names():
        db.create_collection("policies")

    policies_col = db["policies"]
    policies_col.create_index("policy_id", unique=True)
    policies_col.create_index("worker_id")
    policies_col.create_index("active_status")
    policies_col.create_index("start_date")
    policies_col.create_index("end_date")
    policies_col.create_index([("worker_id", ASCENDING), ("active_status", ASCENDING)])

    # ========================================================================
    # CLAIMS COLLECTION
    # ========================================================================
    if "claims" not in db.list_collection_names():
        db.create_collection("claims")

    claims_col = db["claims"]
    claims_col.create_index("claim_id", unique=True)
    claims_col.create_index("worker_id")
    claims_col.create_index("policy_id")
    claims_col.create_index("claim_status")
    claims_col.create_index("created_at")
    claims_col.create_index([("worker_id", ASCENDING), ("created_at", DESCENDING)])
    claims_col.create_index([("claim_status", ASCENDING), ("created_at", DESCENDING)])

    # ========================================================================
    # PAYOUTS COLLECTION
    # ========================================================================
    if "payouts" not in db.list_collection_names():
        db.create_collection("payouts")

    payouts_col = db["payouts"]
    payouts_col.create_index("payout_id", unique=True)
    payouts_col.create_index("claim_id")
    payouts_col.create_index("worker_id")
    payouts_col.create_index("status")
    payouts_col.create_index("timestamp")
    payouts_col.create_index([("worker_id", ASCENDING), ("timestamp", DESCENDING)])

    # ========================================================================
    # ZONES COLLECTION
    # ========================================================================
    if "zones" not in db.list_collection_names():
        db.create_collection("zones")

    zones_col = db["zones"]
    zones_col.create_index("zone_name", unique=True)
    zones_col.create_index("city")

    # ========================================================================
    # AUDIT LOGS COLLECTION
    # ========================================================================
    if "audit_logs" not in db.list_collection_names():
        db.create_collection("audit_logs")

    audit_col = db["audit_logs"]
    audit_col.create_index("timestamp")
    audit_col.create_index("worker_id")
    audit_col.create_index("operation")
    audit_col.create_index([("timestamp", DESCENDING)])

    print("[OK] All collections initialized with indexes")
    
    # ========================================================================
    # SEED DATA LOADING
    # ========================================================================
    # Only seed if workers collection is empty
    if db["workers"].count_documents({}) == 0:
        seed_path = os.path.join(os.path.dirname(__file__), "..", "data", "seed_data.json")
        if os.path.exists(seed_path):
            try:
                with open(seed_path, "r") as f:
                    seed_data = json.load(f)
                
                print(f"🌱 Empty database detected. Seeding data from {seed_path}...")
                
                for collab_name, docs in seed_data.items():
                    if docs and collab_name in ["workers", "policies", "claims", "payouts", "zones"]:
                        # Convert ISO date strings back to datetime objects
                        for doc in docs:
                            for key, value in doc.items():
                                if isinstance(value, str) and (key.endswith("_at") or key.endswith("_date") or key == "timestamp"):
                                    try:
                                        doc[key] = parser.parse(value)
                                    except:
                                        pass
                        
                        db[collab_name].insert_many(docs)
                        print(f"✅ Instrumented {len(docs)} documents into '{collab_name}'")
                
                st.info("💡 Demo data pre-loaded from seed file.")
            except Exception as e:
                print(f"❌ Error seeding data: {e}")
                
    return db


def verify_db_connection():
    """Verify database connection and initialize collections."""
    try:
        client = get_db_client()
        db = get_database()

        # Ping to verify connection
        client.admin.command("ping")
        st.success("✅ MongoDB connection successful")

        # Initialize collections
        init_collections()
        return True
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        return False


# Cache the connection using Streamlit's cache
@st.cache_resource
def get_db_connection():
    """Cached database connection for Streamlit."""
    return get_database()
