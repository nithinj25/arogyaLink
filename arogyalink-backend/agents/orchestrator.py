import asyncio
from firebase.client import (
    create_call_record, update_agent_status,
    update_call_field, save_case_to_firestore
)
from agents.triage import run_triage_agent
from agents.location import run_location_agent
from agents.dispatch import run_dispatch_agent
from agents.comms import run_comms_agent
from utils.logger import get_logger

logger = get_logger(__name__)


async def run_orchestrator(
    case_id: str,
    phone: str,
    lang: str,
    transcript: str,
    lat: float | None = None,
    lng: float | None = None,
    patient_age: str | None = None,
    patient_gender: str | None = None,
    symptoms_tags: list[str] | None = None,
    source: str = "app",
) -> dict:
    """
    Main agent pipeline. Called as a FastAPI background task.

    EXECUTION FLOW:
    1. Mark orchestrator active
    2. TriageAgent + LocationAgent run IN PARALLEL — the key demo moment
    3. DispatchAgent runs with combined results
    4. CommsAgent sends all notifications
    5. Case saved to Firestore for history
    """
    update_agent_status(case_id, "orchestrator", "active")
    logger.info(f"[{case_id}] OrchestratorAgent started | source={source} | phone={phone}")

    try:
        # ═══════════════════════════════════════════════════════════════
        # STEP 1: PARALLEL — TriageAgent + LocationAgent simultaneously
        # ═══════════════════════════════════════════════════════════════
        logger.info(f"[{case_id}] Launching TriageAgent + LocationAgent in parallel")

        triage_result, location_result = await asyncio.gather(
            run_triage_agent(
                case_id=case_id,
                transcript=transcript,
                patient_age=patient_age,
                patient_gender=patient_gender,
                lang=lang,
            ),
            run_location_agent(
                case_id=case_id,
                lat=lat,
                lng=lng,
                requires_ambulance=True,
                requires_asha=True,
            ),
        )

        update_agent_status(case_id, "orchestrator", "active")

        update_call_field(case_id, "triage_level", triage_result.severity.value)
        update_call_field(case_id, "diagnosis", triage_result.diagnosis)
        update_call_field(case_id, "action_summary", triage_result.action_summary)

        facility = location_result["facility"]
        asha_worker = location_result["asha_worker"]
        address = location_result["address"]

        # ═══════════════════════════════════════════════════
        # STEP 2: DispatchAgent (needs both triage + location)
        # ═══════════════════════════════════════════════════
        dispatch_result = await run_dispatch_agent(
            case_id=case_id,
            triage=triage_result,
            facility=facility,
            asha_worker=asha_worker,
        )

        # ═══════════════════════════════════════════════════
        # STEP 3: CommsAgent — notify everyone
        # ═══════════════════════════════════════════════════
        patient_info = f"Age: {patient_age or 'unknown'}, Gender: {patient_gender or 'unknown'}"
        symptoms_str = ", ".join(symptoms_tags or [transcript[:100]])

        await run_comms_agent(
            case_id=case_id,
            phone=phone,
            lang=lang,
            triage=triage_result,
            dispatch=dispatch_result,
            facility=facility,
            asha_worker=asha_worker,
            address=address,
            patient_info=patient_info,
            symptoms=symptoms_str,
        )

        # ═══════════════════════════════════════════════════
        # STEP 4: Mark complete, persist to Firestore
        # ═══════════════════════════════════════════════════
        update_agent_status(case_id, "orchestrator", "complete")

        final_record = {
            "case_id": case_id,
            "phone": phone,
            "source": source,
            "lang": lang,
            "transcript": transcript,
            "lat": lat,
            "lng": lng,
            "address": address,
            "severity": triage_result.severity.value,
            "diagnosis": triage_result.diagnosis,
            "action_summary": triage_result.action_summary,
            "requires_ambulance": triage_result.requires_ambulance,
            "facility_name": facility.name if facility else None,
            "facility_eta": facility.eta_minutes if facility else None,
            "asha_name": asha_worker.name if asha_worker else None,
            "asha_phone": asha_worker.phone if asha_worker else None,
            "ambulance_dispatched": dispatch_result.get("ambulance_dispatched"),
            "patient_age": patient_age,
            "patient_gender": patient_gender,
        }
        save_case_to_firestore(case_id, final_record)

        logger.info(f"[{case_id}] Pipeline COMPLETE | severity={triage_result.severity.value}")
        return final_record

    except Exception as e:
        update_agent_status(case_id, "orchestrator", "error")
        update_call_field(case_id, "state", "error")
        logger.error(f"[{case_id}] Orchestrator FAILED: {e}", exc_info=True)
        raise
