from firebase_admin import messaging
from utils.logger import get_logger

logger = get_logger(__name__)


def send_fcm_to_asha(fcm_token: str, case_id: str, severity: str):
    """Push notification to ASHA worker's Flutter app"""
    severity_labels = {
        "emergency": "EMERGENCY",
        "urgent": "URGENT",
        "moderate": "New Case",
        "stable": "New Case",
    }
    title = f"ArogyaLink: {severity_labels.get(severity, 'New Case')} Assigned"
    body = "Tap to view patient details and navigate to location"

    try:
        message = messaging.Message(
            token=fcm_token,
            notification=messaging.Notification(title=title, body=body),
            data={"case_id": case_id, "severity": severity, "screen": "asha_case"},
            android=messaging.AndroidConfig(priority="high"),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound="default", badge=1)
                )
            ),
        )
        messaging.send(message)
        logger.info(f"FCM sent to ASHA for case {case_id}")
    except Exception as e:
        logger.error(f"FCM failed: {e}")
