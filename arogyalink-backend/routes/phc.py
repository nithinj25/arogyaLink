from fastapi import APIRouter, Header
from firebase.client import get_firestore
from utils.logger import get_logger

router = APIRouter(prefix="/phc", tags=["phc-operator"])
logger = get_logger(__name__)


@router.get("/alerts")
async def get_phc_alerts(authorization: str = Header(...)):
    """Get incoming emergencies for this PHC (facility_id passed as Bearer token for hackathon)"""
    facility_id = authorization.replace("Bearer ", "")
    fs = get_firestore()
    alerts = (
        fs.collection("cases")
        .where("facility_id", "==", facility_id)
        .where("state", "in", ["dispatched"])
        .order_by("created_at", direction="DESCENDING")
        .limit(20)
        .stream()
    )
    return {"alerts": [a.to_dict() | {"id": a.id} for a in alerts]}


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, authorization: str = Header(...)):
    fs = get_firestore()
    fs.collection("cases").document(alert_id).update({"phc_acknowledged": True})
    return {"status": "acknowledged"}
