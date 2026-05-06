from operator import add

from fastapi import FastAPI

from routes.router import router
from dal.postgres import PostgresDAL
from core.config import Settings

settings = Settings()
postgres_dal = PostgresDAL(connection_string=f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}")

# Add shutdown logic here, such as closing database connections


app = FastAPI()


@app.get("/health")
async def health_check():
    # You could add logic here to check DB connections
    return {"status": "healthy"}

app.include_router(router=router)


