"""
Base Repository - Memory-First CRUD operations for Streamlit Hackathon Demos
(Uses a globally shared @st.cache_resource dict as a reliable database simulator)
"""
import streamlit as st
import json
import os
import uuid
from datetime import datetime
from dateutil import parser
from typing import Optional, List, Dict, Any

@st.cache_resource
def get_global_db_storage():
    """Returns a globally shared dictionary to simulate a database across all user sessions."""
    return {}

class BaseRepository:
    """Base repository class with common CRUD operations using global shared storage."""

    def __init__(self, collection_name: str):
        """Initialize with global shared storage, pre-populated from seed if available."""
        self.collection_name = collection_name
        self.db_storage = get_global_db_storage()
        
        # --- Supabase Initialization ---
        self.supabase = None
        try:
            from services.supabase_service import get_supabase_client
            self.supabase = get_supabase_client()
        except:
            self.supabase = None
        
        # Absolute path to seed data
        self.seed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed_data.json"))
        
        # Always ensure the collection is initialized
        if self.collection_name not in self.db_storage or not self.db_storage[self.collection_name]:
            self.db_storage[self.collection_name] = []
            self._load_seed_data()

    def _save_to_disk(self):
        """Persist the current global state back to seed_data.json for persistence across reboots."""
        try:
            # Prepare data (convert datetime objects back to ISO strings)
            export_data = {}
            for col_name, docs in self.db_storage.items():
                processed_docs = []
                for doc in docs:
                    new_doc = doc.copy()
                    for k, v in new_doc.items():
                        if isinstance(v, datetime):
                            new_doc[k] = v.isoformat()
                    processed_docs.append(new_doc)
                export_data[col_name] = processed_docs
                
            with open(self.seed_path, "w") as f:
                json.dump(export_data, f, indent=4)
        except Exception as e:
            print(f"FAILED TO PERSIST: {e}")

    def _load_seed_data(self):
        """Pre-populate the collection from data/seed_data.json."""
        if os.path.exists(self.seed_path):
            try:
                with open(self.seed_path, "r") as f:
                    all_seed_data = json.load(f)
                
                if self.collection_name in all_seed_data:
                    raw_docs = all_seed_data[self.collection_name]
                    processed_docs = []
                    for doc in raw_docs:
                        for k, v in doc.items():
                            if isinstance(v, str) and (k.endswith("_at") or k.endswith("_date") or k == "timestamp" or k == "completed_at" or k == "start_date" or k == "end_date"):
                                try:
                                    doc[k] = parser.parse(v)
                                except: pass
                        processed_docs.append(doc)
                    
                    self.db_storage[self.collection_name] = processed_docs
            except Exception as e:
                print(f"Error seeding {self.collection_name}: {e}")

    def create(self, document: Dict[str, Any]) -> str:
        """Create a new document in memory."""
        # Ensure it has an ID
        if "_id" not in document:
            document["_id"] = str(uuid.uuid4())
        if "created_at" not in document:
            document["created_at"] = datetime.now()
        
        self.db_storage[self.collection_name].append(document)
        self._save_to_disk()
        
        # Supabase Push Sync (Fallback Mode Supported)
        if self.supabase:
            try:
                # Prepare supabase compatible payload (convert datetimes)
                sb_doc = {}
                for k, v in document.items():
                    sb_doc[k] = v.isoformat() if isinstance(v, datetime) else v
                self.supabase.table(self.collection_name).insert(sb_doc).execute()
            except Exception as e:
                import logging
                logging.warning(f"Supabase sync failed for {self.collection_name}: {e}")

        return str(document["_id"])

    def _process_supabase_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ISO strings back to datetime objects and inject defaults for data normalization."""
        new_doc = {}
        for k, v in doc.items():
            if isinstance(v, str) and (k.endswith("_at") or k.endswith("_date") or k == "timestamp" or k == "completed_at" or k == "start_date" or k == "end_date"):
                try:
                    parsed = parser.parse(v)
                    new_doc[k] = parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
                except:
                    new_doc[k] = v
            else:
                new_doc[k] = v
        
        # --- DATA NORMALIZATION / DEFAULT INJECTION (PHASE 2 & 5) ---
        if self.collection_name == "workers":
            new_doc.setdefault("avg_hourly_income", 40.0)
            new_doc.setdefault("ncb_streak", 0)
            new_doc.setdefault("ncb_discount_rate", 0.0)
            new_doc.setdefault("rating", 4.5)
            new_doc.setdefault("city", "Chennai")
            new_doc.setdefault("delivery_zone", "General")
        
        elif self.collection_name == "policies":
            new_doc.setdefault("premium_paid", new_doc.get("weekly_premium", 0.0))
            if "status" not in new_doc:
                new_doc["status"] = "Active" if new_doc.get("active_status", True) else "Inactive"
            if "active_status" not in new_doc:
                new_doc["active_status"] = (new_doc.get("status") == "Active")
            # Ensure dates are present
            if "start_date" not in new_doc: new_doc["start_date"] = datetime.now()
            if "end_date" not in new_doc: new_doc["end_date"] = datetime.now() + timedelta(days=7)
                
        elif self.collection_name == "claims":
            if "status" not in new_doc:
                new_doc["status"] = new_doc.get("claim_status", "Pending")
            if "claim_status" not in new_doc:
                new_doc["claim_status"] = new_doc.get("status", "Pending")
            new_doc.setdefault("governance_status", "PENDING")
            
            # --- PHASE 2 SMART FALLBACK ENGINE ---
            
            # 1. Payout Impact / Estimated Loss
            if not new_doc.get("estimated_loss"):
                # derive from avg_hourly_income * 8 or use safe default
                new_doc["estimated_loss"] = 40.0 * 8
                new_doc["estimated_loss_source"] = "derived"
            else:
                new_doc["estimated_loss_source"] = "actual"
                
            # 2. Fraud Score (Deterministic, NO randomness)
            if new_doc.get("fraud_score") is None or new_doc.get("fraud_score") == 0:
                zone_risk = (
                    new_doc.get("zone_risk_level")
                    or new_doc.get("risk_level")
                    or new_doc.get("zone_status")
                    or "SAFE"
                )
                if isinstance(zone_risk, str):
                    zone_risk = zone_risk.upper()
                
                if zone_risk == "CRITICAL" or "CRITICAL" in str(zone_risk):
                    f_val = 35.0
                elif zone_risk == "HIGH" or "HIGH" in str(zone_risk):
                    f_val = 25.0
                elif zone_risk in ["WATCH", "MEDIUM"] or "WATCH" in str(zone_risk):
                    f_val = 18.0
                else:
                    f_val = 12.0
                new_doc["fraud_score"] = f_val
                new_doc["fraud_score_source"] = "derived"
            else:
                new_doc["fraud_score_source"] = "actual"

            # 3. Loyalty Score
            if new_doc.get("loyalty_score") is None:
                l_score = min(1.0, 0.5 + (new_doc.get("ncb_streak", 0) * 0.1))
                new_doc["loyalty_score"] = round(l_score, 2)
                new_doc["loyalty_score_source"] = "derived"
            else:
                new_doc["loyalty_score_source"] = "actual"

            # 4. Decision Confidence
            if new_doc.get("decision_confidence") is None or new_doc.get("decision_confidence") == 0:
                f_score = float(new_doc.get("fraud_score", 0))
                l_score = float(new_doc.get("loyalty_score", 0.9))
                # Safe formula derivation matching logic
                computed_confidence = (100 - f_score) * 0.7 + (l_score * 30)
                clamped_confidence = min(99.0, max(65.0, computed_confidence))
                new_doc["decision_confidence"] = round(clamped_confidence, 2)
                new_doc["decision_confidence_source"] = "derived"
                new_doc["decision_reason"] = f"Derived using fraud_score={f_score}, loyalty_score={l_score}"
            else:
                ex_conf = float(new_doc.get("decision_confidence", 85.0))
                clamped_confidence = min(99.0, max(65.0, ex_conf))
                new_doc["decision_confidence"] = round(clamped_confidence, 2)
                new_doc["decision_confidence_source"] = "actual"

            # Ensure claim_status is CamelCase for UI consistency
            if "claim_status" in new_doc:
                s = new_doc["claim_status"]
                if isinstance(s, str) and s.isupper(): new_doc["claim_status"] = s.capitalize()
        
        elif self.collection_name == "payouts":
            if "timestamp" not in new_doc:
                new_doc["timestamp"] = new_doc.get("created_at") or new_doc.get("date") or datetime.now()
            new_doc.setdefault("status", "COMPLETED")
            
        elif self.collection_name == "zones":
            if "zone_name" not in new_doc:
                new_doc["zone_name"] = new_doc.get("zone_id", "Unknown Zone")
            if "zone_id" not in new_doc:
                new_doc["zone_id"] = new_doc["zone_name"]
            new_doc.setdefault("historical_risk_score", 0.2)

        return new_doc

    def _sync_to_local_cache(self, fetched_docs_or_doc):
        """Safely upsert fetched remote documents into the local in-memory dict."""
        if not fetched_docs_or_doc: return
        
        # Ensure list processing
        docs = fetched_docs_or_doc if isinstance(fetched_docs_or_doc, list) else [fetched_docs_or_doc]
        
        current_cache = self.db_storage[self.collection_name]
        
        for doc in docs:
            # Figure out primary key natively without rewriting legacy logic
            id_val = doc.get("worker_id") or doc.get("policy_id") or doc.get("claim_id") or doc.get("_id")
            id_key = "worker_id" if "worker_id" in doc else ("policy_id" if "policy_id" in doc else ("claim_id" if "claim_id" in doc else "_id"))
            
            if not id_val:
                continue
                
            # Upsert into cache
            idx_to_replace = None
            for i, c_doc in enumerate(current_cache):
                if c_doc.get(id_key) == id_val:
                    idx_to_replace = i
                    break
                    
            if idx_to_replace is not None:
                current_cache[idx_to_replace] = doc
            else:
                current_cache.append(doc)
                
        self.db_storage[self.collection_name] = current_cache

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict]:
        """Find one document by simple field match (Delegates to find_many for robust query support)."""
        results = self.find_many(query, limit=1)
        return results[0] if results else None

    def find_by_id(self, doc_id: str, id_field: str = "_id") -> Optional[Dict]:
        """Find document by ID."""
        return self.find_one({id_field: doc_id})

    def find_many(self, query: Dict[str, Any], limit: int = 0, skip: int = 0,
                  sort_field: str = None, sort_order: int = -1) -> List[Dict]:
        """Find multiple documents with basic filtering and sorting."""
        if self.supabase:
            try:
                q = self.supabase.table(self.collection_name).select("*")
                for key, val in query.items():
                    if isinstance(val, dict):
                        if "$in" in val:
                            q = q.in_(key, val["$in"])
                        if "$gte" in val:
                            val_gte = val["$gte"].isoformat() if isinstance(val["$gte"], datetime) else val["$gte"]
                            q = q.gte(key, val_gte)
                        if "$lte" in val:
                            val_lte = val["$lte"].isoformat() if isinstance(val["$lte"], datetime) else val["$lte"]
                            q = q.lte(key, val_lte)
                    else:
                        q = q.eq(key, val)
                
                if sort_field:
                    q = q.order(sort_field, desc=(sort_order == -1))
                if limit > 0:
                    # Fetching limit + skip to slice safely in memory
                    q = q.limit(limit + skip)
                    
                res = q.execute()
                processed = [self._process_supabase_doc(d) for d in res.data]
                
                # Cloud-Sync Local Cache
                self._sync_to_local_cache(processed)
                
                # If Supabase returned nothing, check local cache as a second-chance (Phase 5 Consistency Fix)
                if not processed and query:
                    local_processed = self._find_many_local(query, limit, skip, sort_field, sort_order)
                    if local_processed:
                        return local_processed
                
                if skip > 0:
                    processed = processed[skip:]
                
                # Apply limits purely incase db wrapper didnt
                if limit > 0 and len(processed) > limit:
                    processed = processed[:limit]
                    
                return processed
            except Exception as e:
                import logging
                logging.warning(f"Supabase find_many failed, falling back to local: {e}")
                
            
        return self._find_many_local(query, limit, skip, sort_field, sort_order)

    def _find_many_local(self, query: Dict[str, Any], limit: int = 0, skip: int = 0,
                        sort_field: str = None, sort_order: int = -1) -> List[Dict]:
        """Extracted local find logic for fallback and second-chance queries."""
        results = []
        for doc in self.db_storage[self.collection_name]:
            match = True
            for key, val in query.items():
                doc_val = doc.get(key)
                
                # --- NORMALIZE LOCAL DATA ON-THE-FLY ---
                if self.collection_name == "workers":
                    if key == "worker_id" and not doc_val: match=False; break
                
                # Handle MongoDB-style operators
                if isinstance(val, dict):
                    # Robust type conversion for datetime comparisons
                    compare_val = val.get("$gte") or val.get("$lte") or val.get("$lt") or val.get("$gt")
                    if isinstance(compare_val, datetime) and isinstance(doc_val, str):
                        try:
                            # Try to parse the doc_val into a datetime for comparison
                            doc_val = datetime.fromisoformat(doc_val.replace("Z", "+00:00"))
                        except:
                            pass

                    if "$in" in val and doc_val not in val["$in"]:
                        match = False; break
                    if "$gte" in val:
                        if not doc_val or doc_val < val["$gte"]: match = False; break
                    if "$lte" in val:
                        if not doc_val or doc_val > val["$lte"]: match = False; break
                    if "$lt" in val:
                        if not doc_val or doc_val >= val["$lt"]: match = False; break
                    if "$gt" in val:
                        if not doc_val or doc_val <= val["$gt"]: match = False; break
                elif doc_val != val:
                    # Special check for status/active_status alias
                    if key == "status" and "active_status" in doc:
                        mapped_status = "Active" if doc["active_status"] else "Inactive"
                        if mapped_status != val: match = False; break
                    elif key == "active_status" and "status" in doc:
                        mapped_active = (doc["status"] == "Active")
                        if mapped_active != val: match = False; break
                    else:
                        match = False; break
            if match:
                # Apply defaults even to local docs to ensure consistency
                results.append(self._process_supabase_doc(doc))

        # Sort
        if sort_field:
            reverse = True if sort_order == -1 else False
            results.sort(key=lambda x: x.get(sort_field, ""), reverse=reverse)

        # Skip and Limit
        if skip > 0:
            results = results[skip:]
        if limit > 0:
            results = results[:limit]
            
        return results

    def reset_to_defaults(self, default_zones: List[Dict]):
        """Wipe all zones and restore from defaults (Memory Store)."""
        self.db_storage["zones"] = []
        for z in default_zones:
            self.create(z)

    def find_all(self) -> List[Dict]:
        """Find all documents in collection."""
        if self.supabase:
            try:
                res = self.supabase.table(self.collection_name).select("*").execute()
                processed = [self._process_supabase_doc(d) for d in res.data]
                self._sync_to_local_cache(processed)
                return processed
            except Exception as e:
                import logging
                logging.warning(f"Supabase find_all failed, falling back: {e}")
                
        # --- LOCAL FALLBACK ---
        return [self._process_supabase_doc(d) for d in self.db_storage[self.collection_name]]

    def update(self, query: Dict[str, Any], update_data: Dict[str, Any], upsert: bool = False) -> bool:
        """Update multiple documents (In MEMORY)."""
        modified = False
        target_docs = self.find_many(query)
        
        # Simple $set logic simulation
        data_to_set = update_data.get("$set", update_data)
        
        for doc in target_docs:
            doc.update(data_to_set)
            modified = True
            
        if modified:
            self._save_to_disk()
            # Push changes to Supabase
            if self.supabase:
                try:
                    for doc in target_docs:
                        sb_doc = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in doc.items()}
                        id_val = doc.get("worker_id") or doc.get("policy_id") or doc.get("claim_id") or doc.get("_id")
                        id_key = "worker_id" if "worker_id" in doc else ("policy_id" if "policy_id" in doc else ("claim_id" if "claim_id" in doc else "_id"))
                        self.supabase.table(self.collection_name).update(sb_doc).eq(id_key, id_val).execute()
                except Exception as e:
                    pass
            
        if not modified and upsert:
            self.create(query | data_to_set)
            return True
            
        return modified

    def update_by_id(self, doc_id: str, update_data: Dict[str, Any], id_field: str = "_id") -> bool:
        """Update by ID."""
        update_data["updated_at"] = datetime.now()
        return self.update({id_field: doc_id}, {"$set": update_data})

    def update_many(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update many (basic count)."""
        target_docs = self.find_many(query)
        data_to_set = update.get("$set", update)
        for doc in target_docs:
            doc.update(data_to_set)
        return len(target_docs)

    def delete(self, query: Dict[str, Any]) -> bool:
        """Delete from memory."""
        initial_count = len(self.db_storage[self.collection_name])
        self.db_storage[self.collection_name] = [
            doc for doc in self.db_storage[self.collection_name] 
            if not all(doc.get(k) == v for k, v in query.items())
        ]
        return len(self.db_storage[self.collection_name]) < initial_count

    def delete_by_id(self, doc_id: str, id_field: str = "_id") -> bool:
        """Delete by ID."""
        return self.delete({id_field: doc_id})

    def delete_many(self, query: Dict[str, Any]) -> int:
        """Delete many."""
        initial_count = len(self.db_storage[self.collection_name])
        self.db_storage[self.collection_name] = [
            doc for doc in self.db_storage[self.collection_name] 
            if not all(doc.get(k) == v for k, v in query.items())
        ]
        return initial_count - len(self.db_storage[self.collection_name])

    def count(self, query: Dict[str, Any] = None) -> int:
        """Count matching documents."""
        if not query:
            return len(self.db_storage[self.collection_name])
        return len(self.find_many(query))

    def exists(self, query: Dict[str, Any]) -> bool:
        """Check exists."""
        return self.find_one(query) is not None

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict]:
        """Simple aggregation layer for counts (Simulated for Hackathon UI)."""
        # We only need to support basic counts for the dashboard charts
        return self.find_all()

    def bulk_insert(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Bulk insert."""
        ids = []
        for doc in documents:
            ids.append(self.create(doc))
        return ids

    def create_index(self, field_name: str, unique: bool = False): pass
    def delete_index(self, field_name: str): pass
