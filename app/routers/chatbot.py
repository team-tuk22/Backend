from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional

from chat_bot.models import make_response
from app.db import SessionLocal
from app.models.model import Judgement

router = APIRouter()

class ChatRequest(BaseModel):
    user_q: str # 유저 질문
    db_q: str = ""  # DB 검색 키워드
    model_t: str = "" # 모델 타입

@router.post("/chatbot/generate")
def chat(request: ChatRequest):
    # 키워드 받음 -> DB에서 그 단어가 들어간 판례를 일단 가져옴 -> AI 모델에 질문과 같이 던져줌 -> 답변 받아옴 -> 출력.
    # 1. 단 db_q를 써서 DB에서 검색 돌림.
    query = request.db_q
    
    # 2. 데이터베이스 세션 시작
    with SessionLocal() as db:  
        # 사건명 또는 판례내용에서 검색어가 포함된 판례를 찾습니다.
        cond = (Judgement.case_name.ilike(f"%{query}%")) | (Judgement.case_precedent.ilike(f"%{query}%"))
        # 검색 결과를 10개로 제한합니다.
        stmt = select(Judgement).where(cond).limit(10)
        items = db.execute(stmt).scalars().all()
        
    # 3. 검색 결과를 챗봇이 이해할 수 있는 형태로 변환함.
    results = [
        {
            "title": item.case_name,
            "court": item.case_court,
            "date": item.case_date.isoformat() if item.case_date else None,
            "case_precedent": item.case_precedent
        } for item in items
    ]
    print(results)
    

    # 최종 -> 변환된 결과, 사용자 질문을 함께 챗봇 모델에 전달.
    response = make_response(
        user_message=request.user_q,
        db_results=results, 
        model_type=request.model_t
    )
    
    return {"response": response}