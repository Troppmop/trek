from fastapi import APIRouter

router = APIRouter()

@router.get("/v1/search")
def search_stations(query: str):
    pass