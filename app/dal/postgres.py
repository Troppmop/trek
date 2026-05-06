from sqlalchemy.ext.asyncio import create_async_engine

class PostgresDAL:
    def __init__(self, connection_string):
        self.engine = create_async_engine(connection_string)

    # app/dal/postgres.py

    async def execute_query(self, query, params):
        async with self.engine.connect() as conn:
            result = await conn.execute(query, params)
            # .fetchall() is a regular function, NOT a coroutine. 
            # You don't await it.
            return result.fetchall()