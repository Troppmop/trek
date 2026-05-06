import pandas as pd
import numpy as np
import asyncio
import logging
from sqlalchemy import text
from core.config import Settings
from dal.postgres import PostgresDAL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_stop_times_incremental():
    settings = Settings()
    db_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"
    dal = PostgresDAL(connection_string=db_url)
    
    path = "./data/stop_times.txt"
    chunk_size = 50000 
    
    try:
        # 1. Clear the table first
        async with dal.engine.begin() as conn:
            await conn.execute(text("TRUNCATE TABLE stop_times;"))
            logger.info("Table truncated. Starting fresh load...")

        # 2. Process chunks
        # Use keep_default_na=True to let pandas catch 'nan', 'NULL', etc.
        reader = pd.read_csv(path, chunksize=chunk_size, low_memory=False)
        
        for i, chunk in enumerate(reader):
            # --- CRITICAL DATA CLEANING ---
            # 1. Force numeric conversion. 'coerce' turns empty strings/errors into NaN
            chunk['shape_dist_traveled'] = pd.to_numeric(chunk['shape_dist_traveled'], errors='coerce')
            chunk['stop_id'] = pd.to_numeric(chunk['stop_id'], errors='coerce').fillna(0).astype(int)
            chunk['stop_sequence'] = pd.to_numeric(chunk['stop_sequence'], errors='coerce').fillna(0).astype(int)
            
            # 2. Convert all NaN (not a number) to None (SQL NULL)
            # This is what prevents the "must be real number, not str" error
            chunk = chunk.replace({np.nan: None})
            
            async with dal.engine.begin() as conn:
                raw_conn = await conn.get_raw_connection()
                
                # Use values.tolist() for the most reliable tuple conversion
                records = [tuple(x) for x in chunk.values]
                
                await raw_conn.driver_connection.copy_records_to_table(
                    'stop_times', 
                    records=records,
                    columns=[
                        'trip_id', 'arrival_time', 'departure_time', 'stop_id', 
                        'stop_sequence', 'pickup_type', 'drop_off_type', 'shape_dist_traveled'
                    ]
                )
            
            logger.info(f"Successfully committed chunk {i+1} ({(i+1) * chunk_size} rows)")

        # 3. Add Indexes AFTER load
        logger.info("Creating indexes... this might take 1-2 minutes.")
        async with dal.engine.begin() as conn:
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON stop_times (stop_id);"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id ON stop_times (trip_id);"))
        
        logger.info("All data loaded and indexed successfully.")

    except Exception as e:
        logger.error(f"Critical Error during load: {e}")
    finally:
        await dal.engine.dispose()

if __name__ == "__main__":
    asyncio.run(load_stop_times_incremental())