from operator import add

from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from routes.router import router
from dal.postgres import PostgresDAL
from core.config import Settings
from fastapi.middleware.cors import CORSMiddleware
settings = Settings()

# Add shutdown logic here, such as closing database connections
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n[DEBUG] ASYNC_POSTGRES_URL is: '{settings.ASYNC_POSTGRES_URL}'\n")    
    app.state.postgres_dal = PostgresDAL(connection_string=settings.ASYNC_POSTGRES_URL)   
    yield
    # Cleanup code here (e.g., close DB connections)
    await app.state.postgres_dal.engine.dispose()
    app.state.postgres_dal = None

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace ["*"] with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    # You could add logic here to check DB connections
    return {"status": "healthy"}

app.include_router(router=router)


