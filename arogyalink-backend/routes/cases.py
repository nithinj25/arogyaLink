from fastapi import APIRouter, Query, HTTPException
from firebase.client import get_rtdb, get_call_record
from utils.logger import get_logger

router = APIRouter(prefix="/cases", tags=["cases"])
logger = get_logger(__name__)


@router.get("")
async def list_cases(limit: int = Query(default=50, le=200)):
    """Return the most recent cases from RTDB, sorted newest first."""
    try:
        snapshot = get_rtdb().reference("calls").order_by_child("created_at").limit_to_last(limit).get()
        if not snapshot:
            return {"cases": [], "count": 0}
        cases = list(snapshot.values())
        cases.sort(key=lambda c: c.get("created_at", 0), reverse=True)
        return {"cases": cases, "count": len(cases)}
    except Exception as e:
        logger.error(f"Error fetching cases: {e}")
        return {"cases": [], "count": 0}


@router.get("/stats")
async def dashboard_stats():
    """Aggregate counts for the dashboard header cards."""
    try:
        snapshot = get_rtdb().reference("calls").get() or {}
        all_cases = list(snapshot.values())

        import time
        now_ms = int(time.time() * 1000)
        day_ms = 86_400_000

        today = [c for c in all_cases if now_ms - c.get("created_at", 0) < day_ms]
        active = [c for c in all_cases if c.get("state") == "processing"]

        return {
            "total_cases": len(all_cases),
            "today_cases": len(today),
            "active_calls": len(active),
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"total_cases": 0, "today_cases": 0, "active_calls": 0}


@router.get("/{case_id}")
async def get_case(case_id: str):
    """Get full details for a single case."""
    record = get_call_record(case_id)
    if not record:
        raise HTTPException(status_code=404, detail="Case not found")
    return record
