from sqlalchemy import create_engine

class PostgresDAL:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)

    def execute_query(self, query):
        with self.engine.connect() as connection:
            result = connection.execute(query)
            return result.fetchall()