from fastapi import APIRouter, Request, HTTPException
import json
from sqlalchemy import text


router = APIRouter(prefix="/routes")

@router.get("/")
async def get_all_routes(request: Request):
    query = text("""
        SELECT 
            route_id, 
            route_short_name, 
            route_long_name, 
            route_type,
            route_color,
            route_text_color
        FROM public.routes
        ORDER BY route_short_name ASC
    """)
    
    result = await request.app.state.postgres_dal.execute_query(query, {})
    
    # Since 'result' is already a list, we use _mapping to convert to dict
    # This works for SQLAlchemy Row objects found in a list
    return [dict(row._mapping) for row in result]

@router.get("/{route_id}/geometry")
async def get_route_geometry(route_id: str, request: Request):
    query = text("""
        SELECT ST_AsGeoJSON(ST_MakeLine(geom ORDER BY seq)) as geometry
        FROM (
            SELECT DISTINCT ON (shape_pt_sequence) 
                ST_SetSRID(ST_MakePoint(CAST(shape_pt_lon AS FLOAT), CAST(shape_pt_lat AS FLOAT)), 4326) as geom,
                CAST(shape_pt_sequence AS INT) as seq
            FROM public.shapes s
            JOIN public.trips t ON s.shape_id = t.shape_id
            WHERE t.route_id = :route_id
        ) AS sorted_points
    """)

    result = await request.app.state.postgres_dal.execute_query(query, {"route_id": route_id})

    # FIX: Use ._mapping to check the column by name
    if not result or not result[0]._mapping['geometry']:
        raise HTTPException(status_code=404, detail="Geometry not found for this route")

    # Convert the GeoJSON string (from Postgres) into a Python dict
    import json
    return json.loads(result[0]._mapping['geometry'])

@router.get("/{route_id}/stops")
async def get_route_stops(request: Request, route_id: str):
    query = text("""
        SELECT DISTINCT ON (s.stop_id)
            s.stop_id, 
            s.stop_name, 
            s.stop_lat, 
            s.stop_lon,
            st.stop_sequence
        FROM public.stops s
        JOIN public.stop_times st ON s.stop_id = st.stop_id
        JOIN public.trips t ON st.trip_id = t.trip_id
        WHERE t.route_id = :route_id
        ORDER BY s.stop_id, CAST(st.stop_sequence AS INT) ASC
    """)
    
    rows = await request.app.state.postgres_dal.execute_query(query, {"route_id": route_id})

    
    # Convert each Row to a dictionary using _mapping
    return [dict(row._mapping) for row in rows]