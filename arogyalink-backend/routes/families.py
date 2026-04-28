from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator
from typing import Literal
import re

from firebase.client import (
    get_family_by_phone, create_family, update_family,
    delete_family, list_families,
)
from utils.phone import to_e164
from utils.logger import get_logger

router = APIRouter(prefix="/families", tags=["families"])
logger = get_logger(__name__)


# ── Pydantic models ────────────────────────────────────────────────────────────

class FamilyMember(BaseModel):
    id: str = ""
    name: str
    age: int
    gender: Literal["M", "F", "other"] = "other"
    relationship: str = "other"
    conditions: list[str] = []
    allergies: list[str] = []
    blood_group: str | None = None
    medications: list[str] = []


class FamilyCreate(BaseModel):
    primary_name: str
    phone: str
    address: str = ""
    village: str = ""
    district: str = ""
    state: str = ""
    pin: str | None = None
    language: Literal["en-IN", "hi-IN", "kn-IN", "te-IN"] = "en-IN"
    members: list[FamilyMember] = []

    @field_validator("phone")
    @classmethod
    def normalise_phone(cls, v: str) -> str:
        try:
            return to_e164(v)
        except Exception:
            raise ValueError("Invalid phone number — use E.164 or a local Indian format")


class FamilyUpdate(BaseModel):
    primary_name: str | None = None
    address: str | None = None
    village: str | None = None
    district: str | None = None
    state: str | None = None
    pin: str | None = None
    language: Literal["en-IN", "hi-IN", "kn-IN", "te-IN"] | None = None
    members: list[FamilyMember] | None = None


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("")
async def list_all_families(
    search: str | None = Query(default=None, description="Filter by name, village, or phone"),
    limit: int = Query(default=100, le=500),
):
    """List all registered families, optionally filtered by keyword."""
    results = list_families(search=search, limit=limit)
    return {"families": results, "count": len(results)}


@router.get("/{phone}")
async def get_family(phone: str):
    """Get a single family by phone number."""
    try:
        normalised = to_e164(phone)
    except Exception:
        normalised = phone

    family = get_family_by_phone(normalised)
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    return family


@router.post("", status_code=201)
async def register_family(body: FamilyCreate):
    """Register a new family."""
    existing = get_family_by_phone(body.phone)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"A family is already registered for {body.phone}"
        )

    import uuid
    members = []
    for m in body.members:
        d = m.model_dump()
        if not d.get("id"):
            d["id"] = str(uuid.uuid4())[:8]
        members.append(d)

    data = body.model_dump()
    data["members"] = members

    saved = create_family(data)
    logger.info(f"Family registered: {body.phone} — {body.primary_name}")
    return saved


@router.put("/{phone}")
async def update_family_record(phone: str, body: FamilyUpdate):
    """Partial update of a family record."""
    try:
        normalised = to_e164(phone)
    except Exception:
        normalised = phone

    existing = get_family_by_phone(normalised)
    if not existing:
        raise HTTPException(status_code=404, detail="Family not found")

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if "members" in updates:
        import uuid
        for m in updates["members"]:
            if not m.get("id"):
                m["id"] = str(uuid.uuid4())[:8]

    updated = update_family(normalised, updates)
    logger.info(f"Family updated: {normalised}")
    return updated


@router.delete("/{phone}", status_code=204)
async def remove_family(phone: str):
    """Delete a family record."""
    try:
        normalised = to_e164(phone)
    except Exception:
        normalised = phone

    existing = get_family_by_phone(normalised)
    if not existing:
        raise HTTPException(status_code=404, detail="Family not found")

    delete_family(normalised)
    logger.info(f"Family deleted: {normalised}")
