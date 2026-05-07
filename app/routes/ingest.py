import io
import os
import uuid
import shutil
import zipfile
import pandas as pd

from fastapi import APIRouter, Request, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy import text

# Assuming your DAL (Data Access Layer) is in this path
# Adjust this based on your actual folder structure
from dal.postgres import PostgresDAL

async def run_background_ingest(task_id, zip_path, dal):
    try:
        z = zipfile.ZipFile(zip_path)
        processed_tables = []
        
        for filename in z.namelist():
            if not filename.endswith('.txt'): continue
            base_name = filename.split('/')[-1]
            table_name = base_name.replace('.txt', '')
            
            with z.open(filename) as f:
                # Same Pandas logic as before, but wrapped in this task
                df_sample = pd.read_csv(f, nrows=0, dtype=str)
                clean_cols = [col.strip().replace('"', '') for col in df_sample.columns]
                
                await dal.execute_query(text(f'DROP TABLE IF EXISTS public."{table_name}" CASCADE;'), {})
                cols_definition = [f'"{col}" TEXT' for col in clean_cols]
                create_stmt = f'CREATE TABLE public."{table_name}" ({", ".join(cols_definition)});'
                await dal.execute_query(text(create_stmt), {})

                f.seek(0)
                for chunk in pd.read_csv(f, chunksize=50000, dtype=str, encoding='utf-8-sig'):
                    chunk.columns = clean_cols
                    await dal.bulk_copy(table_name, chunk)
            
            processed_tables.append(table_name)
            ingestion_status[task_id]["tables"] = processed_tables
        
        ingestion_status[task_id]["status"] = "success"
        
    except Exception as e:
        print(f"Background Ingest Error: {e}")
        ingestion_status[task_id]["status"] = "failed"
        ingestion_status[task_id]["error"] = str(e)
    finally:
        # Clean up the temp file
        if os.path.exists(zip_path):
            os.remove(zip_path)

# Store status in memory (for a simple implementation)
ingestion_status = {}
router = APIRouter()
@router.post("/ingest-zip")
async def ingest_gtfs_zip(
    background_tasks: BackgroundTasks, 
    request: Request, 
    file: UploadFile = File(...)
):
    task_id = str(uuid.uuid4())
    temp_zip_path = f"/tmp/{task_id}.zip"
    
    # 1. Save the file locally to avoid keeping the whole 140MB in RAM
    with open(temp_zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    ingestion_status[task_id] = {"status": "processing", "tables": []}
    
    # 2. Start the heavy processing in the background
    background_tasks.add_task(
        run_background_ingest, 
        task_id, 
        temp_zip_path, 
        request.app.state.postgres_dal
    )
    
    # 3. Return immediately!
    return {
        "status": "accepted", 
        "task_id": task_id, 
        "message": "Ingestion started in background."
    }

@router.get("/ingest-status/{task_id}")
async def get_ingest_status(task_id: str):
    status = ingestion_status.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status


@router.post("/run-indexing")
async def run_indexing(request: Request):
    # Define the commands as a list of strings
    commands = [
        # 1. Setup Extensions
        "CREATE EXTENSION IF NOT EXISTS postgis",
        
        # 2. Fix Stops & Spatial Data
        "ALTER TABLE public.stops DROP COLUMN IF EXISTS geom CASCADE",
        "ALTER TABLE public.stops ADD COLUMN geom geometry(Point, 4326)",
        """
        UPDATE public.stops 
        SET geom = ST_SetSRID(ST_MakePoint(CAST(stop_lon AS FLOAT), CAST(stop_lat AS FLOAT)), 4326)
        WHERE stop_lon IS NOT NULL AND stop_lat IS NOT NULL AND stop_lon != '' AND stop_lat != ''
        """,
        "CREATE INDEX IF NOT EXISTS idx_stops_geom ON public.stops USING GIST (geom)",
        "CREATE INDEX IF NOT EXISTS idx_stops_stop_id ON public.stops (stop_id)",
        
        # 3. Fix Stop Times (Critical for arrival boards)
        "CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON public.stop_times (stop_id)",
        "CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id ON public.stop_times (trip_id)",
        "CREATE INDEX IF NOT EXISTS idx_stop_times_arrival ON public.stop_times (arrival_time)",
        
        # 4. Fix Shapes (Critical for Map lines)
        "CREATE INDEX IF NOT EXISTS idx_shapes_shape_id ON public.shapes (shape_id)",
        "CREATE INDEX IF NOT EXISTS idx_shapes_seq ON public.shapes (CAST(shape_pt_sequence AS INT))",
        
        # 5. Fix Routes & Trips (Including the missing color columns)
        "ALTER TABLE public.routes ADD COLUMN IF NOT EXISTS route_color TEXT",
        "ALTER TABLE public.routes ADD COLUMN IF NOT EXISTS route_text_color TEXT",
        "CREATE INDEX IF NOT EXISTS idx_routes_route_id ON public.routes (route_id)",
        "CREATE INDEX IF NOT EXISTS idx_trips_route_id ON public.trips (route_id)",
        "CREATE INDEX IF NOT EXISTS idx_trips_shape_id ON public.trips (shape_id)",
        
        # 6. Handle the 'Stations' Identity Crisis
        "DROP TABLE IF EXISTS public.stations CASCADE",
        
        # 7. Create the View
        """
        CREATE VIEW public.stations AS 
        SELECT 
            stop_id AS id, 
            stop_name AS name, 
            CAST(NULLIF(stop_lat, '') AS FLOAT) AS latitude, 
            CAST(NULLIF(stop_lon, '') AS FLOAT) AS longitude, 
            stop_desc AS description, 
            stop_code,
            geom
        FROM public.stops
        """
    ]  

    try:
        # Loop through and execute each command individually
        for cmd in commands:
            clean_cmd = cmd.strip()
            if not clean_cmd:
                continue
                
            print(f"Executing: {clean_cmd[:50]}...") 
            await request.app.state.postgres_dal.execute_query(text(clean_cmd), {})
            
        return {"status": "success", "message": "Indexing and View creation complete."}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Indexing failed. Check logs. Error: {str(e)}"
        )