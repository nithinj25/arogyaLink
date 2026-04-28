import asyncio
from services.maps import get_distance_and_eta, reverse_geocode
from firebase.client import (
    update_agent_status, get_asha_workers_near,
    get_facilities_near, update_call_field
)
from models.facility import Facility, AshaWorker
from utils.logger import get_logger

logger = get_logger(__name__)


async def run_location_agent(
    case_id: str,
    lat: float | None,
    lng: float | None,
    requires_ambulance: bool = True,
    requires_asha: bool = True,
) -> dict:
    """
    Find nearest facility and ASHA worker.
    Runs distance matrix queries in parallel.
    Returns {'facility': Facility | None, 'asha_worker': AshaWorker | None, 'address': str}
    """
    update_agent_status(case_id, "location", "active")
    logger.info(f"[{case_id}] LocationAgent started | lat={lat}, lng={lng}")

    if lat is None or lng is None:
        update_agent_status(case_id, "location", "error")
        logger.warning(f"[{case_id}] No location data — LocationAgent degraded")
        return {"facility": None, "asha_worker": None, "address": "Unknown location"}

    try:
        address_task = reverse_geocode(lat, lng)
        facilities_task = asyncio.to_thread(get_facilities_near, lat, lng, 30)
        asha_task = asyncio.to_thread(get_asha_workers_near, lat, lng, 10)

        address, facilities, asha_workers = await asyncio.gather(
            address_task, facilities_task, asha_task
        )

        nearest_facility = None
        if facilities:
            eta_tasks = [
                get_distance_and_eta(lat, lng, f["lat"], f["lng"])
                for f in facilities[:3]
            ]
            etas = await asyncio.gather(*eta_tasks)
            best = None
            best_eta = float("inf")
            for i, facility_data in enumerate(facilities[:3]):
                dist_km, eta_min = etas[i]
                if requires_ambulance and not facility_data.get("has_ambulance"):
                    continue
                if eta_min < best_eta:
                    best_eta = eta_min
                    best = Facility(
                        **facility_data,
                        distance_km=dist_km,
                        eta_minutes=eta_min,
                    )
            nearest_facility = best or Facility(
                **facilities[0], distance_km=etas[0][0], eta_minutes=etas[0][1]
            )

        nearest_asha = None
        if asha_workers:
            asha_eta_tasks = [
                get_distance_and_eta(lat, lng, w["lat"], w["lng"])
                for w in asha_workers[:3]
            ]
            asha_etas = await asyncio.gather(*asha_eta_tasks)
            min_idx = min(range(len(asha_etas)), key=lambda i: asha_etas[i][1])
            w = asha_workers[min_idx]
            nearest_asha = AshaWorker(
                **w,
                distance_km=asha_etas[min_idx][0],
            )

        update_call_field(case_id, "address", address)
        if nearest_facility:
            update_call_field(case_id, "facility", {
                "name": nearest_facility.name,
                "lat": nearest_facility.lat,
                "lng": nearest_facility.lng,
                "eta_minutes": nearest_facility.eta_minutes,
            })

        update_agent_status(case_id, "location", "complete")
        logger.info(f"[{case_id}] LocationAgent complete | facility={nearest_facility and nearest_facility.name}")

        return {
            "facility": nearest_facility,
            "asha_worker": nearest_asha,
            "address": address,
        }

    except Exception as e:
        update_agent_status(case_id, "location", "error")
        logger.error(f"[{case_id}] LocationAgent error: {e}")
        return {"facility": None, "asha_worker": None, "address": "Unknown"}
