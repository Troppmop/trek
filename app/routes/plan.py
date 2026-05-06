from fastapi import APIRouter

router = APIRouter()

@router.post("/plan")
def plan_route(start: str, end: str):
    return {"route": f"Planned route from {start} to {end}"}