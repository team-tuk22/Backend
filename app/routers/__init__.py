from fastapi import APIRouter
from app.routers.crawl import router as crawl_router

router = APIRouter()

router.include_router(crawl_router, prefix="/crawl", tags=["crawl"])