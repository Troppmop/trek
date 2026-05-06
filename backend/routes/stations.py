from fastapi import APIRouter

router = APIRouter()

@router.get("/v1/stations/nearby")
def get_nearby_stations(lat: float, lng: float, radius: float):
    pass

@router.get("/v1/stations/{station_id}/arrivals")
def get_station_arrivals(station_id: int):
    pass
