import pandas as pd
import asyncio
import logging
from sqlalchemy import text
from core.config import Settings
from dal.postgres import PostgresDAL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize(val):
    """Ensure NaN becomes None and numbers become ints/floats properly."""
    if pd.isna(val):
        return None
    return val

async def load_stations_data():
    settings = Settings()
    # db_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"
    # postgres_dal = PostgresDAL(connection_string=db_url)

    path = "./data/stop_times.txt"
    df = pd.read_csv(path)
    print(df.to_dict(orient='records')[:5])  # Debug: Print first 5 records to verify reading
    # try:
    #     # 1. Read CSV
    #     df = pd.read_csv(path)
    #     print(df.to_dict(orient='records')[:5])  # Debug: Print first 5 records to verify reading
    #     # 2. Map and Sanitize
    #     records = []
    #     for _, row in df.iterrows():
    #         records.append({
    #             # "id": int(row['stop_id']),
    #             # "name": str(row['stop_name']),
    #             # "latitude": float(row['stop_lat']),
    #             # "longitude": float(row['stop_lon']),
    #             # # Explicitly sanitize these to handle 'nan' floats
    #             # "description": sanitize(row.get('stop_desc')),
    #             # "stop_code": sanitize(row.get('stop_code'))
    #         })

    #     # create_table_query = text("""
    #     #     CREATE TABLE IF NOT EXISTS stations (
    #     #         id INTEGER PRIMARY KEY,
    #     #         name TEXT NOT NULL,
    #     #         latitude DOUBLE PRECISION NOT NULL,
    #     #         longitude DOUBLE PRECISION NOT NULL,
    #     #         description TEXT,
    #     #         stop_code INTEGER
    #     #     );
    #     # """)

    #     # insert_query = text("""
    #     #     INSERT INTO stations (id, name, latitude, longitude, description, stop_code)
    #     #     VALUES (:id, :name, :latitude, :longitude, :description, :stop_code)
    #     #     ON CONFLICT (id) DO UPDATE SET
    #     #         name = EXCLUDED.name,
    #     #         latitude = EXCLUDED.latitude,
    #     #         longitude = EXCLUDED.longitude,
    #     #         description = EXCLUDED.description,
    #     #         stop_code = EXCLUDED.stop_code;
    #     # """)

    #     async with postgres_dal.engine.begin() as conn:
    #         await conn.execute(create_table_query)
            
    #         # 3. Chunk the inserts (Better for 70k rows)
    #         chunk_size = 5000
    #         for i in range(0, len(records), chunk_size):
    #             chunk = records[i:i + chunk_size]
    #             await conn.execute(insert_query, chunk)
    #             logger.info(f"Inserted chunk {i // chunk_size + 1}")
            
    #     logger.info(f"Successfully loaded {len(records)} stations.")

    # except Exception as e:
    #     logger.error(f"Error loading stations: {e}")
    # finally:
    #     await postgres_dal.engine.dispose()

if __name__ == "__main__":
    asyncio.run(load_stations_data())