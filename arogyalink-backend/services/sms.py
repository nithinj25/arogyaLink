from twilio.rest import Client
from config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

_client = None


def get_twilio_client() -> Client:
    global _client
    if _client is None:
        _client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    return _client


SMS_TEMPLATES = {
    "patient_en": (
        "ArogyaLink Emergency Alert\n"
        "Case: {case_id}\n"
        "Severity: {severity}\n"
        "Action: {action}\n"
        "Ambulance ETA: ~{eta} mins from {facility}\n"
        "ASHA Worker: {asha_name} ({asha_phone})\n"
        "Stay calm. Help is on the way."
    ),
    "patient_kn": (
        "ArogyaLink ತುರ್ತು ಸಂದೇಶ\n"
        "Case: {case_id}\n"
        "ತೀವ್ರತೆ: {severity}\n"
        "ಆಂಬ್ಯುಲೆನ್ಸ್ ಬರಲು: ~{eta} ನಿಮಿಷ\n"
        "ಸಹಾಯ ಬರುತ್ತಿದೆ. ಶಾಂತವಾಗಿರಿ."
    ),
    "asha_en": (
        "ArogyaLink: New case assigned\n"
        "Case: {case_id} | Severity: {severity}\n"
        "Patient: {patient_info}\n"
        "Location: {address}\n"
        "Please respond immediately."
    ),
    "phc_en": (
        "ArogyaLink: Incoming emergency\n"
        "Case: {case_id} | Severity: {severity}\n"
        "ETA: ~{eta} mins\n"
        "Symptoms: {symptoms}\n"
        "Please prepare."
    ),
}


def send_sms(to: str, body: str) -> bool:
    try:
        client = get_twilio_client()
        message = client.messages.create(
            body=body,
            from_=settings.twilio_phone_number,
            to=to,
        )
        logger.info(f"SMS sent to {to}: SID={message.sid}")
        return True
    except Exception as e:
        logger.error(f"SMS failed to {to}: {e}")
        return False


def send_patient_sms(phone: str, lang: str, case_id: str, severity: str,
                     action: str, eta: int, facility: str,
                     asha_name: str, asha_phone: str):
    template_key = f"patient_{lang.split('-')[0]}"
    template = SMS_TEMPLATES.get(template_key, SMS_TEMPLATES["patient_en"])
    body = template.format(
        case_id=case_id, severity=severity, action=action,
        eta=eta, facility=facility, asha_name=asha_name, asha_phone=asha_phone,
    )
    send_sms(phone, body)


def send_asha_sms(phone: str, case_id: str, severity: str,
                  patient_info: str, address: str):
    body = SMS_TEMPLATES["asha_en"].format(
        case_id=case_id, severity=severity,
        patient_info=patient_info, address=address,
    )
    send_sms(phone, body)


def send_phc_sms(phone: str, case_id: str, severity: str,
                 eta: int, symptoms: str):
    body = SMS_TEMPLATES["phc_en"].format(
        case_id=case_id, severity=severity, eta=eta, symptoms=symptoms,
    )
    send_sms(phone, body)
