import pandas as pd
import numpy as np
import asyncio
import logging
from sqlalchemy import text
from core.config import Settings
from dal.postgres import PostgresDAL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_routes():
    settings = Settings()
    db_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"
    dal = PostgresDAL(connection_string=db_url)
    
    path = "./data/routes.txt"
    
    try:
        # Load the file
        df = pd.read_csv(path)
        
        # --- DATA CLEANING ---
        # 1. Force ID and Type to numeric (integers)
        df['route_id'] = pd.to_numeric(df['route_id'], errors='coerce').fillna(0).astype(int)
        df['agency_id'] = pd.to_numeric(df['agency_id'], errors='coerce').fillna(0).astype(int)
        df['route_type'] = pd.to_numeric(df['route_type'], errors='coerce').fillna(0).astype(int)

        # 2. Force all text columns to be strings and handle NaNs
        text_cols = ['route_short_name', 'route_long_name', 'route_desc', 'route_color']
        for col in text_cols:
            # fillna("") ensures we don't have floats, then replace "" with None for SQL NULL
            df[col] = df[col].astype(str).replace({'nan': None, '': None, 'None': None})

        # 3. Final conversion to None for any remaining NaNs
        df = df.replace({np.nan: None})

        async with dal.engine.begin() as conn:
            await conn.execute(text("TRUNCATE TABLE routes;"))
            
            raw_conn = await conn.get_raw_connection()
            # Convert dataframe to a list of tuples for the COPY command
            records = [tuple(x) for x in df.values]
            
            await raw_conn.driver_connection.copy_records_to_table(
                'routes', 
                records=records,
                columns=[
                    'route_id', 'agency_id', 'route_short_name', 
                    'route_long_name', 'route_desc', 'route_type', 'route_color'
                ]
            )
            
        logger.info(f"Successfully loaded {len(df)} routes.")

    except Exception as e:
        logger.error(f"Error loading routes: {e}")
    finally:
        await dal.engine.dispose()

if __name__ == "__main__":
    asyncio.run(load_routes())