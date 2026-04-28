from fastapi import APIRouter, Header, HTTPException
from firebase.client import get_firestore
from utils.logger import get_logger

router = APIRouter(prefix="/asha", tags=["asha-worker"])
logger = get_logger(__name__)


@router.get("/cases")
async def get_asha_cases(authorization: str = Header(...)):
    """Get active cases assigned to this ASHA worker (phone passed as Bearer token for hackathon)"""
    phone = authorization.replace("Bearer ", "")
    fs = get_firestore()
    cases = (
        fs.collection("cases")
        .where("asha_phone", "==", phone)
        .where("state", "in", ["dispatched", "processing"])
        .order_by("created_at", direction="DESCENDING")
        .limit(20)
        .stream()
    )
    return {"cases": [c.to_dict() | {"id": c.id} for c in cases]}


@router.post("/cases/{case_id}/accept")
async def accept_case(case_id: str, authorization: str = Header(...)):
    fs = get_firestore()
    fs.collection("cases").document(case_id).update({"asha_accepted": True})
    return {"status": "accepted"}


@router.post("/cases/{case_id}/update")
async def update_case(case_id: str, body: dict, authorization: str = Header(...)):
    fs = get_firestore()
    fs.collection("cases").document(case_id).update(body)
    return {"status": "updated"}
