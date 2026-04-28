from pydantic import BaseModel
from typing import Optional
from enum import Enum


class SeverityLevel(str, Enum):
    EMERGENCY = "emergency"   # Life-threatening, act in minutes
    URGENT = "urgent"         # Serious, act in hours
    MODERATE = "moderate"     # Needs care, not immediately life-threatening
    STABLE = "stable"         # Can wait for scheduled visit


class TriageResult(BaseModel):
    severity: SeverityLevel
    diagnosis: str
    action_summary: str
    requires_ambulance: bool
    requires_asha: bool
    home_care_instructions: Optional[str] = None
    follow_up_question: Optional[str] = None
    confidence: float = 0.85
