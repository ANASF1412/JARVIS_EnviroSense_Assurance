"""
Standalone DB Controller - Dummy Connection Handler for Hackathon Demo
This ensures the app never crashes due to MongoDB connection errors.
"""
import streamlit as st

def get_db_client():
    """Dummy client."""
    return None

def get_database():
    """Dummy database context."""
    return {}

def close_db_connection():
    """Dummy close."""
    pass

def init_collections():
    """Initial collections - no-op for memory repo."""
    print("[OK] Session-State Collections Initialized (No External DB Needed)")
    return {}

def verify_db_connection():
    """Always return True to allow the UI to function."""
    st.success("✅ Hackathon Demo Mode: Active (Zero-Latency Data Store)")
    return True

@st.cache_resource
def get_db_connection():
    """Cached connection mockup."""
    return {}
