from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.routers import router as api_router

from app.databases.db import Base, engine, SessionLocal
from app.models import Base

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(api_router)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], allow_credentials=True,
#     allow_methods=["*"], allow_headers=["*"],
# )

@app.get("/health")
def health():
    return {"status": "ok"}

# @app.get("/api/v1/rulings/search")
# def search(q: str = Query("", min_length=0), limit: int = 10, offset: int = 0):
#     with SessionLocal() as db:  # type: Session
#         cond = (Ruling.title.ilike(f"%{q}%")) | (Ruling.body.ilike(f"%{q}%"))
#         stmt = select(Ruling).where(cond).limit(limit).offset(offset)
#         total_stmt = select(func.count()).select_from(select(Ruling).where(cond).subquery())
#         items = db.execute(stmt).scalars().all()
#         total = db.scalar(total_stmt) or 0
#         return {
#             "query": q, "limit": limit, "offset": offset, "total": total,
#             "items": [{"id": r.id, "title": r.title, "court": r.court, "date": r.date} for r in items],
#         }