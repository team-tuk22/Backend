from fastapi import APIRouter
from .crawl import router as crawl_router
from .chatbot import router as chatbot_router

router = APIRouter()

router.include_router(crawl_router)
router.include_router(chatbot_router)