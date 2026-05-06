from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from schemas.stops import Stop

router = APIRouter(prefix="/stations")

@router.get("/nearby", response_model=List[Stop])
async def get_nearby_stops(
    request: Request,
    lat: float = Query(...),
    lon: float = Query(...),
    limit: int = Query(10)
):
    query = text("""
        SELECT id, name, latitude, longitude, description, stop_code
        FROM stations
        ORDER BY geom <-> ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
        LIMIT :limit
    """)

    # This call is awaited because it's the DB communication
    rows = await request.app.state.postgres_dal.execute_query(query, {"lat": lat, "lon": lon, "limit": limit})
    
    # Since rows is a list of Row objects, we can validate them
    return [Stop.model_validate(row, from_attributes=True) for row in rows]

@router.get("/{station_id}/arrivals")
async def get_station_arrivals(station_id: int):
    return {"arrivals": f"Arrivals for station {station_id}"}