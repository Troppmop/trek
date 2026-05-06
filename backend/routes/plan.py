from fastapi import APIRouter

router = APIRouter()

@router.post("/v1/plan")
def plan_route(start: str, end: str):
    pass