import time
from firebase.client import update_agent_status, update_call_field
from models.triage import TriageResult, SeverityLevel
from models.facility import Facility, AshaWorker
from utils.logger import get_logger

logger = get_logger(__name__)


async def run_dispatch_agent(
    case_id: str,
    triage: TriageResult,
    facility: Facility | None,
    asha_worker: AshaWorker | None,
) -> dict:
    """
    Decide what to dispatch based on triage severity.
    In production: call ambulance booking API / 108 integration.
    For hackathon: record dispatch decision in Firebase.
    """
    update_agent_status(case_id, "dispatch", "active")
    logger.info(f"[{case_id}] DispatchAgent started | severity={triage.severity}")

    dispatch_record = {
        "ambulance_dispatched": False,
        "asha_dispatched": False,
        "facility_name": None,
        "eta_minutes": None,
        "dispatch_time": int(time.time() * 1000),
    }

    try:
        if triage.severity in (SeverityLevel.EMERGENCY, SeverityLevel.URGENT):
            if facility and triage.requires_ambulance:
                dispatch_record["ambulance_dispatched"] = True
                dispatch_record["facility_name"] = facility.name
                dispatch_record["eta_minutes"] = facility.eta_minutes
                logger.info(f"[{case_id}] Ambulance dispatched from {facility.name} | ETA {facility.eta_minutes}m")

            if asha_worker and triage.requires_asha:
                dispatch_record["asha_dispatched"] = True
                dispatch_record["asha_name"] = asha_worker.name
                dispatch_record["asha_phone"] = asha_worker.phone
                logger.info(f"[{case_id}] ASHA worker {asha_worker.name} dispatched")

        elif triage.severity == SeverityLevel.MODERATE:
            if asha_worker:
                dispatch_record["asha_dispatched"] = True
                dispatch_record["asha_name"] = asha_worker.name
                dispatch_record["asha_phone"] = asha_worker.phone

        # STABLE: no dispatch, recorded for ASHA follow-up

        update_call_field(case_id, "dispatch", dispatch_record)
        update_call_field(case_id, "state", "dispatched")
        update_agent_status(case_id, "dispatch", "complete")
        logger.info(f"[{case_id}] DispatchAgent complete")
        return dispatch_record

    except Exception as e:
        update_agent_status(case_id, "dispatch", "error")
        logger.error(f"[{case_id}] DispatchAgent error: {e}")
        return dispatch_record
