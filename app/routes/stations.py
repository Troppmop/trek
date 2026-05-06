from fastapi import APIRouter

router = APIRouter(prefix="/stations")

@router.get("/nearby")
def get_nearby_stations(lat: float, lng: float, radius: float):
    return {"stations": f"Nearby stations for {lat}, {lng} within {radius} meters"}

@router.get("/{station_id}/arrivals")
def get_station_arrivals(station_id: int):
    return {"arrivals": f"Arrivals for station {station_id}"}