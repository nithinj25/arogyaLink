import time
import firebase_admin
from firebase_admin import credentials, db, firestore
from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_app = None


def init_firebase():
    global _app
    if _app is None:
        import os
        sa_path = settings.google_application_credentials
        # On Cloud Run the service account JSON is mounted via Secret Manager,
        # or we use Application Default Credentials (workload identity).
        if sa_path and os.path.exists(sa_path):
            cred = credentials.Certificate(sa_path)
        else:
            cred = credentials.ApplicationDefault()
        _app = firebase_admin.initialize_app(cred, {
            'databaseURL': settings.firebase_database_url,
            'projectId': settings.firebase_project_id,
        })
        logger.info("Firebase initialized")
    return _app


def get_rtdb():
    return db


def get_firestore():
    return firestore.client()


# ─── Realtime DB helpers ──────────────────────────────────────────────────────

def create_call_record(case_id: str, phone: str, source: str, lang: str):
    ref = db.reference(f"calls/{case_id}")
    ref.set({
        "case_id": case_id,
        "phone": phone,
        "source": source,
        "lang": lang,
        "state": "processing",
        "agent_statuses": {
            "orchestrator": "pending",
            "triage": "pending",
            "location": "pending",
            "dispatch": "pending",
            "comms": "pending",
        },
        "created_at": int(time.time() * 1000),
        "updated_at": int(time.time() * 1000),
    })
    return ref


def update_agent_status(case_id: str, agent: str, status: str):
    """
    status: 'pending' | 'active' | 'complete' | 'error'
    agent: 'orchestrator' | 'triage' | 'location' | 'dispatch' | 'comms'
    """
    db.reference(f"calls/{case_id}/agent_statuses/{agent}").set(status)
    db.reference(f"calls/{case_id}/updated_at").set(int(time.time() * 1000))


def update_call_field(case_id: str, field: str, value):
    db.reference(f"calls/{case_id}/{field}").set(value)
    db.reference(f"calls/{case_id}/updated_at").set(int(time.time() * 1000))


def get_call_record(case_id: str) -> dict | None:
    return db.reference(f"calls/{case_id}").get()


# ─── Firestore helpers ────────────────────────────────────────────────────────

def get_caller_profile(phone: str) -> dict | None:
    fs = get_firestore()
    doc = fs.collection("callers").document(phone).get()
    return doc.to_dict() if doc.exists else None


def upsert_caller_profile(phone: str, data: dict):
    fs = get_firestore()
    from google.cloud.firestore import SERVER_TIMESTAMP
    data["updated_at"] = SERVER_TIMESTAMP
    fs.collection("callers").document(phone).set(data, merge=True)


def get_asha_workers_near(lat: float, lng: float, radius_km: int = 10) -> list[dict]:
    """
    Returns ASHA workers within rough bounding box.
    1 degree lat ≈ 111 km — good enough for hackathon; use geohash in production.
    """
    fs = get_firestore()
    delta = radius_km / 111.0
    workers = (
        fs.collection("asha_workers")
        .where("lat", ">=", lat - delta)
        .where("lat", "<=", lat + delta)
        .where("is_active", "==", True)
        .limit(10)
        .stream()
    )
    return [w.to_dict() | {"id": w.id} for w in workers]


def get_facilities_near(lat: float, lng: float, radius_km: int = 30) -> list[dict]:
    fs = get_firestore()
    delta = radius_km / 111.0
    facilities = (
        fs.collection("facilities")
        .where("lat", ">=", lat - delta)
        .where("lat", "<=", lat + delta)
        .where("is_active", "==", True)
        .limit(10)
        .stream()
    )
    return [f.to_dict() | {"id": f.id} for f in facilities]


def save_case_to_firestore(case_id: str, data: dict):
    fs = get_firestore()
    from google.cloud.firestore import SERVER_TIMESTAMP
    data["created_at"] = SERVER_TIMESTAMP
    fs.collection("cases").document(case_id).set(data)


# ─── Family Registry ──────────────────────────────────────────────────────────

def get_family_by_phone(phone: str) -> dict | None:
    """Look up a registered family. Phone (E.164) is the document ID."""
    doc = get_firestore().collection("families").document(phone).get()
    return doc.to_dict() if doc.exists else None


def create_family(data: dict) -> dict:
    """Create a new family record. data must contain 'phone' (E.164)."""
    from google.cloud.firestore import SERVER_TIMESTAMP
    phone = data["phone"]
    payload = {**data, "call_count": 0, "last_call_at": None,
               "created_at": SERVER_TIMESTAMP, "updated_at": SERVER_TIMESTAMP}
    get_firestore().collection("families").document(phone).set(payload)
    return {**payload, "created_at": None, "updated_at": None}


def update_family(phone: str, data: dict) -> dict:
    """Partial-merge update of a family record."""
    from google.cloud.firestore import SERVER_TIMESTAMP
    data["updated_at"] = SERVER_TIMESTAMP
    get_firestore().collection("families").document(phone).set(data, merge=True)
    doc = get_firestore().collection("families").document(phone).get()
    return doc.to_dict() if doc.exists else {}


def delete_family(phone: str):
    get_firestore().collection("families").document(phone).delete()


def list_families(search: str = None, limit: int = 100) -> list[dict]:
    """List all families, with optional client-side keyword search."""
    docs = get_firestore().collection("families").order_by("primary_name").limit(limit).stream()
    results = [d.to_dict() for d in docs]
    if search:
        sl = search.lower()
        results = [f for f in results if
                   sl in (f.get("primary_name") or "").lower()
                   or sl in (f.get("village") or "").lower()
                   or sl in (f.get("phone") or "").lower()]
    return results


def increment_family_call_count(phone: str):
    from google.cloud.firestore import SERVER_TIMESTAMP, Increment
    get_firestore().collection("families").document(phone).update({
        "call_count": Increment(1),
        "last_call_at": SERVER_TIMESTAMP,
    })
