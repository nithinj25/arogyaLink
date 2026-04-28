from pydantic import BaseModel, Field
from typing import Optional


class VoiceEmergencyRequest(BaseModel):
    """Internal model — built from Twilio webhook + STT output"""
    case_id: str
    phone: str
    lang: str = "en-IN"
    transcript: str
    recording_url: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class AppEmergencyRequest(BaseModel):
    """Incoming from Flutter app"""
    phone: str
    lang: str = "en-IN"
    symptoms_text: str
    symptom_tags: list[str] = []
    lat: Optional[float] = None
    lng: Optional[float] = None
    patient_age: Optional[str] = None    # 'baby' | 'child' | 'adult' | 'elder'
    patient_gender: Optional[str] = None


class AppEmergencyResponse(BaseModel):
    case_id: str
    status: str
    message: str
