from pydantic import BaseModel
from typing import Optional


class Facility(BaseModel):
    id: str
    name: str
    type: str            # 'PHC' | 'CHC' | 'District Hospital' | 'Private'
    lat: float
    lng: float
    address: str
    phone: str
    has_ambulance: bool
    distance_km: Optional[float] = None
    eta_minutes: Optional[int] = None
    is_active: bool = True


class AshaWorker(BaseModel):
    id: str
    name: str
    phone: str
    lat: float
    lng: float
    village: str
    fcm_token: Optional[str] = None
    is_active: bool = True
    distance_km: Optional[float] = None
