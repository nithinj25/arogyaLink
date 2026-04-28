from fastapi import APIRouter, BackgroundTasks, HTTPException
from models.emergency import AppEmergencyRequest, AppEmergencyResponse
from firebase.client import create_call_record, get_call_record, get_facilities_near
from agents.orchestrator import run_orchestrator
from utils.id_gen import generate_case_id
from utils.phone import to_e164
from utils.logger import get_logger

router = APIRouter(prefix="/app", tags=["app-mode"])
logger = get_logger(__name__)


@router.post("/emergency", response_model=AppEmergencyResponse)
async def submit_app_emergency(
    request: AppEmergencyRequest,
    background_tasks: BackgroundTasks,
):
    """
    Flutter app entry point. Returns case_id immediately.
    Pipeline runs in background — frontend streams updates from Firebase RTDB.
    """
    phone = to_e164(request.phone)
    case_id = generate_case_id()

    create_call_record(
        case_id=case_id,
        phone=phone,
        source="app",
        lang=request.lang,
    )

    background_tasks.add_task(
        run_orchestrator,
        case_id=case_id,
        phone=phone,
        lang=request.lang,
        transcript=request.symptoms_text,
        lat=request.lat,
        lng=request.lng,
        patient_age=request.patient_age,
        patient_gender=request.patient_gender,
        symptoms_tags=request.symptom_tags,
        source="app",
    )

    logger.info(f"App emergency received | case_id={case_id} | phone={phone}")

    return AppEmergencyResponse(
        case_id=case_id,
        status="processing",
        message="Emergency received. AI agents coordinating response.",
    )


@router.get("/status/{case_id}")
async def get_case_status(case_id: str):
    """Poll for current case state. Use Firebase streaming instead where possible."""
    record = get_call_record(case_id)
    if not record:
        raise HTTPException(status_code=404, detail="Case not found")
    return record


@router.get("/facilities/nearby")
async def get_nearby_facilities(lat: float, lng: float, radius: int = 20):
    facilities = get_facilities_near(lat, lng, radius)
    return {"facilities": facilities}
