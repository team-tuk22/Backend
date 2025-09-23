from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional

from chat_bot.models import generate_response
from app.db import SessionLocal
from app.models.model import Judgement
router = APIRouter()

class ChatMessage(BaseModel):
    user_message: str
    search_query: str = ""  # 검색을 위한 키워드
    model_type: str = "huggingface"

@router.post("/chatbot/generate")
def chat_with_bot(message: ChatMessage):
    # 키워드 받음 -> DB에서 그 단어가 들어간 판례를 일단 가져옴 -> AI 모델에 질문과 같이 던져줌 -> 답변 받아옴 -> 출력.
    # 1. 단 search_query를 써서 DB에서 검색 돌림.
    query = message.search_query
    
    # 2. 데이터베이스 세션 시작
    with SessionLocal() as db:  # type: Session
        # 사건명 또는 판례내용에서 검색어가 포함된 판례를 찾습니다.
        cond = (Judgement.case_name.ilike(f"%{query}%")) | (Judgement.case_precedent.ilike(f"%{query}%"))
        # 검색 결과를 3개로 제한합니다.
        stmt = select(Judgement).where(cond).limit(3)
        items = db.execute(stmt).scalars().all()
        
    # 검색 결과를 챗봇이 이해할 수 있는 형태로 변환함.
    db_results = [
        {
            "title": item.case_name,
            "court": item.case_court,
            "date": item.case_date.isoformat() if item.case_date else None, # 날짜 -> 문자열
            "case_precedent": item.case_precedent
        } for item in items
    ]
    print(db_results)
    

    # 변환된 결과, 사용자 질문을 함께 챗봇 모델에 전달.
    response_text = generate_response(
        user_message=message.user_message,
        db_results=db_results, # 검색 결과를 generate_response 함수로 전달
        model_type=message.model_type
    )
    
    return {"response": response_text}