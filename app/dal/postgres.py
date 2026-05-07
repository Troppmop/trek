# app/dal/postgres.py
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
import pandas as pd
import numpy as np

class PostgresDAL:
    def __init__(self, connection_string):
        # 1. SQLAlchemy needs the +asyncpg prefix
        self.engine = create_async_engine(connection_string)
        
        # 2. asyncpg (for bulk_copy) needs a standard DSN without the driver name
        # We strip '+asyncpg' to turn 'postgresql+asyncpg://' into 'postgresql://'
        self.asyncpg_dsn = connection_string.replace("+asyncpg", "")

    # app/dal/postgres.py

    async def bulk_copy(self, table_name, df: pd.DataFrame):
        """High-speed binary copy with strict string enforcement"""
        conn = await asyncpg.connect(self.asyncpg_dsn)
        try:
            # 1. Replace all variations of NaN/Null with None
            df = df.replace({np.nan: None, pd.NA: None, pd.NaT: None})
            
            # 2. Force every non-None value to be a string
            # This prevents the "got float" error by catching hidden floats
            def stringify(val):
                if val is None:
                    return None
                return str(val)

            # Convert rows to list of tuples with the stringify function
            records = [
                tuple(stringify(val) for val in row) 
                for row in df.to_numpy()
            ]
            
            columns = list(df.columns)
            
            await conn.copy_records_to_table(
                table_name, 
                records=records, 
                columns=columns
            )
        finally:
            await conn.close()

    async def execute_query(self, query, params=None):
        if params is None:
            params = {}
        async with self.engine.connect() as conn:
            result = await conn.execute(query, params)
            await conn.commit()
            if result.returns_rows:
                return result.fetchall()
            return []

    async def execute_batch(self, query, params_list: list):
        if not params_list:
            return
        async with self.engine.begin() as conn:
            await conn.execute(query, params_list)