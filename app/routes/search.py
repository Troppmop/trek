from fastapi import APIRouter

router = APIRouter()

@router.get("/search")
def search_stations(query: str):
    return {"stations": f"Search results for {query}"}