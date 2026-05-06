import pandas as pd
import numpy as np
import asyncio
import logging
from sqlalchemy import text
from core.config import Settings
from dal.postgres import PostgresDAL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_trips():
    settings = Settings()
    db_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"
    dal = PostgresDAL(connection_string=db_url)
    
    path = "./data/trips.txt"
    
    try:
        # Load the file
        df = pd.read_csv(path)
        
        # --- DATA CLEANING ---
        # 1. Force numeric columns to integers
        int_cols = ['route_id', 'direction_id', 'wheelchair_accessible']
        for col in int_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # 2. Force text columns and handle NaNs/None
        text_cols = ['service_id', 'trip_id', 'trip_headsign', 'shape_id']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).replace({'nan': None, '': None, 'None': None})
            else:
                df[col] = None

        # 3. Final NaN cleanup to ensure compatibility with COPY
        df = df.replace({np.nan: None})

        async with dal.engine.begin() as conn:
            await conn.execute(text("TRUNCATE TABLE trips;"))
            
            raw_conn = await conn.get_raw_connection()
            records = [tuple(x) for x in df.values]
            
            await raw_conn.driver_connection.copy_records_to_table(
                'trips', 
                records=records,
                columns=[
                    'route_id', 'service_id', 'trip_id', 'trip_headsign', 
                    'direction_id', 'shape_id', 'wheelchair_accessible'
                ]
            )
            
        logger.info(f"Successfully loaded {len(df)} trips.")

    except Exception as e:
        logger.error(f"Error loading trips: {e}")
    finally:
        await dal.engine.dispose()

if __name__ == "__main__":
    asyncio.run(load_trips())