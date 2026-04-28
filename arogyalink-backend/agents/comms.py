import asyncio
from services.sms import send_patient_sms, send_asha_sms, send_phc_sms
from services.fcm import send_fcm_to_asha
from firebase.client import update_agent_status, update_call_field
from models.triage import TriageResult
from models.facility import Facility, AshaWorker
from utils.logger import get_logger

logger = get_logger(__name__)


async def run_comms_agent(
    case_id: str,
    phone: str,
    lang: str,
    triage: TriageResult,
    dispatch: dict,
    facility: Facility | None,
    asha_worker: AshaWorker | None,
    address: str,
    patient_info: str,
    symptoms: str,
) -> bool:
    """Send SMS to patient, ASHA worker, and PHC. Send FCM push to ASHA app."""
    update_agent_status(case_id, "comms", "active")
    logger.info(f"[{case_id}] CommsAgent started")

    tasks = []

    tasks.append(asyncio.to_thread(
        send_patient_sms,
        phone=phone,
        lang=lang,
        case_id=case_id,
        severity=triage.severity.value,
        action=triage.action_summary,
        eta=dispatch.get("eta_minutes", 20),
        facility=dispatch.get("facility_name", "Nearest PHC"),
        asha_name=dispatch.get("asha_name", "ASHA Worker"),
        asha_phone=dispatch.get("asha_phone", ""),
    ))

    if asha_worker and dispatch.get("asha_dispatched"):
        tasks.append(asyncio.to_thread(
            send_asha_sms,
            phone=asha_worker.phone,
            case_id=case_id,
            severity=triage.severity.value,
            patient_info=patient_info,
            address=address,
        ))
        if asha_worker.fcm_token:
            tasks.append(asyncio.to_thread(
                send_fcm_to_asha,
                fcm_token=asha_worker.fcm_token,
                case_id=case_id,
                severity=triage.severity.value,
            ))

    if facility and dispatch.get("ambulance_dispatched"):
        tasks.append(asyncio.to_thread(
            send_phc_sms,
            phone=facility.phone,
            case_id=case_id,
            severity=triage.severity.value,
            eta=dispatch.get("eta_minutes", 20),
            symptoms=symptoms,
        ))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    errors = [r for r in results if isinstance(r, Exception)]
    if errors:
        logger.warning(f"[{case_id}] CommsAgent partial errors: {errors}")

    update_call_field(case_id, "comms_sent", True)
    update_call_field(case_id, "state", "completed")
    update_agent_status(case_id, "comms", "complete")
    logger.info(f"[{case_id}] CommsAgent complete")
    return len(errors) == 0
