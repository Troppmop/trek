from operator import add

from fastapi import FastAPI

from routes.router import router
from dal.postgres import PostgresDAL
from core.config import Settings

settings = Settings()

# Add shutdown logic here, such as closing database connections
def lifespan(app: FastAPI):
    app.state.postgres_dal = PostgresDAL(connection_string=f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}")
    yield
    # Cleanup code here (e.g., close DB connections)
    app.state.postgres_dal.engine.dispose()
    app.state.postgres_dal = None

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    # You could add logic here to check DB connections
    return {"status": "healthy"}

app.include_router(router=router)


