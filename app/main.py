from fastapi import FastAPI, Query
# from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .db import Base, engine, SessionLocal
from .models.model import Judgement
from app.routers import router


Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(router)
# 이제 판례 API에서 JSON 형식으로 가져오면 작동 함. 


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], allow_credentials=True,
#     allow_methods=["*"], allow_headers=["*"],
# )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/rulings/search")
def search(q: str = Query("", min_length=0), limit: int = 10, offset: int = 0):
    with SessionLocal() as db:  # type: Session
        cond = (Judgement.case_name.ilike(f"%{q}%")) | (Judgement.case_precedent.ilike(f"%{q}%"))
        stmt = select(Judgement).where(cond).limit(limit).offset(offset)
        total_stmt = select(func.count()).select_from(select(Judgement).where(cond).subquery())
        items = db.execute(stmt).scalars().all()
        total = db.scalar(total_stmt) or 0
        return {
            "query": q, "limit": limit, "offset": offset, "total": total,
            "items": [{"id": r.id, "title": r.case_name, "court": r.case_court, "date": r.case_date} for r in items],
        }
