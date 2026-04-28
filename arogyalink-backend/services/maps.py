import httpx
import math
from config.settings import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


async def reverse_geocode(lat: float, lng: float) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(GEOCODING_URL, params={
            "latlng": f"{lat},{lng}",
            "key": settings.google_maps_api_key,
            "language": "en",
        })
        data = r.json()
        if data["status"] == "OK" and data["results"]:
            return data["results"][0]["formatted_address"]
        return f"{lat:.4f}, {lng:.4f}"


async def get_distance_and_eta(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
) -> tuple[float, int]:
    """Returns (distance_km, eta_minutes) using driving mode, Haversine as fallback."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(DISTANCE_MATRIX_URL, params={
            "origins": f"{origin_lat},{origin_lng}",
            "destinations": f"{dest_lat},{dest_lng}",
            "mode": "driving",
            "key": settings.google_maps_api_key,
        })
        data = r.json()
        try:
            element = data["rows"][0]["elements"][0]
            if element["status"] == "OK":
                distance_m = element["distance"]["value"]
                duration_s = element["duration"]["value"]
                return round(distance_m / 1000, 1), round(duration_s / 60)
        except (KeyError, IndexError):
            pass
    return _haversine(origin_lat, origin_lng, dest_lat, dest_lng), 20


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return round(2 * R * math.asin(math.sqrt(a)), 1)
