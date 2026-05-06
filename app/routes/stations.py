from unittest import result

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from schemas.stops import Stop
from datetime import datetime
from zoneinfo import ZoneInfo

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

@router.get("/{stop_id}/arrivals")
async def get_stop_arrivals(request:Request, stop_id: int):
    # Get current time in HH:MM:SS format
    israel_tz = ZoneInfo("Asia/Jerusalem")
    now = datetime.now(israel_tz).strftime("%H:%M:%S")
    
    query = text("""
        SELECT 
            r.route_short_name as line,
            t.trip_headsign as destination,
            st.arrival_time as arrival,
            t.wheelchair_accessible as accessible
        FROM stop_times st
        JOIN trips t ON st.trip_id = t.trip_id
        JOIN routes r ON t.route_id = r.route_id
        WHERE st.stop_id = :stop_id
          AND st.arrival_time >= :now
        ORDER BY st.arrival_time ASC
        LIMIT 10
    """)
    
        # FIXED VERSION
    result = await request.app.state.postgres_dal.execute_query(query, {"stop_id": stop_id, "now": now})
    # The modern SQLAlchemy 2.0 way
    arrivals = [dict(row._mapping) for row in result]
        
    return {
        "stop_id": stop_id,
        "current_time": now,
        "arrivals": arrivals
    }