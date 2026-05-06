from fastapi import FastAPI

from app.routes.router import router

app = FastAPI()


@app.get("/health")
async def health_check():
    # You could add logic here to check DB connections
    return {"status": "healthy"}

app.include_router(router=router)


