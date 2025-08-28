from fastapi import FastAPI
from app.routers import crawl
from app.databases.database import init_db

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

# 판례 크롤링 라우터 등록
app.include_router(crawl.router)

@app.get("/")
def root():
    return {"message": "Hello"}