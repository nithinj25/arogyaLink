from services.gemma import call_gemma_json
from models.triage import TriageResult, SeverityLevel
from firebase.client import update_agent_status
from utils.logger import get_logger

logger = get_logger(__name__)

TRIAGE_SYSTEM_PROMPT = """You are TriageAgent, a medical triage AI for rural India emergency response.

Your job: Analyze a patient's symptom description and return a triage assessment.

SEVERITY LEVELS:
- emergency: Life-threatening. Unconscious, not breathing, severe bleeding, chest pain, stroke signs, snake bite, severe burns, pregnancy complications. Dispatch ambulance IMMEDIATELY.
- urgent: Serious but not immediately life-threatening. High fever in child, moderate injury, vomiting with dehydration. Needs care within 2-4 hours.
- moderate: Needs medical attention but can wait. Minor injuries, mild fever in adult, rash.
- stable: Can be managed at home with guidance. Mild cold, minor pain.

ALWAYS respond with valid JSON only. No markdown fences. No preamble.

JSON schema:
{
  "severity": "emergency" | "urgent" | "moderate" | "stable",
  "diagnosis": "Plain language diagnosis (in the same language as the input)",
  "action_summary": "One sentence: what is being done right now",
  "requires_ambulance": true | false,
  "requires_asha": true | false,
  "home_care_instructions": "Only if moderate/stable. Null otherwise.",
  "follow_up_question": "Ask ONE follow-up question if critical info is missing. Null if not needed.",
  "confidence": 0.0 to 1.0
}"""


async def run_triage_agent(
    case_id: str,
    transcript: str,
    patient_age: str | None = None,
    patient_gender: str | None = None,
    lang: str = "en-IN",
) -> TriageResult:
    update_agent_status(case_id, "triage", "active")
    logger.info(f"[{case_id}] TriageAgent started")

    context = f"Patient transcript: {transcript}"
    if patient_age:
        context += f"\nPatient age group: {patient_age}"
    if patient_gender:
        context += f"\nPatient gender: {patient_gender}"
    context += f"\nLanguage: {lang}"

    try:
        result_dict = await call_gemma_json(TRIAGE_SYSTEM_PROMPT, context)
        result = TriageResult(
            severity=SeverityLevel(result_dict.get("severity", "urgent")),
            diagnosis=result_dict.get("diagnosis", "Unable to determine"),
            action_summary=result_dict.get("action_summary", "Coordinating response"),
            requires_ambulance=result_dict.get("requires_ambulance", True),
            requires_asha=result_dict.get("requires_asha", True),
            home_care_instructions=result_dict.get("home_care_instructions"),
            follow_up_question=result_dict.get("follow_up_question"),
            confidence=float(result_dict.get("confidence", 0.8)),
        )
        update_agent_status(case_id, "triage", "complete")
        logger.info(f"[{case_id}] TriageAgent complete: {result.severity}")
        return result
    except Exception as e:
        update_agent_status(case_id, "triage", "error")
        logger.error(f"[{case_id}] TriageAgent error: {e}")
        # Safe fallback — always treat as urgent if AI fails
        return TriageResult(
            severity=SeverityLevel.URGENT,
            diagnosis="Unable to assess — treating as urgent",
            action_summary="Dispatching ASHA worker for assessment",
            requires_ambulance=False,
            requires_asha=True,
            confidence=0.0,
        )
