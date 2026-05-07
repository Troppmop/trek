from fastapi import APIRouter
from routes.stations import router as stations_router
from routes.search import router as search_router
from routes.plan import router as plan_router
from routes.ingest import router as ingest_router
from routes.routes import router as routes_router
router = APIRouter(prefix="/v1")

router.include_router(router=stations_router)
router.include_router(router=search_router)
router.include_router(router=plan_router)
router.include_router(router=ingest_router)
router.include_router(router=routes_router)
