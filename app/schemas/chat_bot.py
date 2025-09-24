from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional

class ChatRequest(BaseModel):
    user_question: str  # 유저 질문
    db_should_query_this: str = ""  # DB 검색 키워드
    model_type: str = ""  # 모델 타입