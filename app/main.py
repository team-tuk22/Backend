from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 라우터 import
from app.routers import rulings, judgement   # ✅ crawl은 제거

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(rulings.router)
app.include_router(judgement.router)   # ✅ judgement 라우터 추가
