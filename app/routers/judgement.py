from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.crawl import fetch_law_data
from app.databases.database import get_db
from app.models.model import Judgement
import uuid
from datetime import date

router = APIRouter(prefix="/api/v1", tags=["judgement"])

@router.get("/judgement")
def get_or_fetch_judgement(id: str = Query(...), db: Session = Depends(get_db)):
    # 1) DB에서 먼저 조회 (case_number 기준)
    obj = db.query(Judgement).filter(Judgement.case_number == id).first()
    if obj:
        return obj

    # 2) 외부 API 호출
    data = fetch_law_data(id)
    if not data:
        raise HTTPException(status_code=404, detail="해당 판례를 찾을 수 없습니다.")

    # 3) DB 저장
    new_case = Judgement(
        id=str(uuid.uuid4()),
        case_number=data["case_number"],
        case_name=data["case_name"],
        case_date=date.fromisoformat(data["case_date"]),  # 문자열 → date 변환
        case_result=data["case_result"],
        case_court=data["case_court"],
        case_court_code=data.get("case_court_code"),
        case_type=data.get("case_type"),
        case_type_code=data.get("case_type_code"),
        case_result_type=data.get("case_result_type"),
        case_result_decision=data.get("case_result_decision"),
        case_result_summary=data.get("case_result_summary"),
        reference=data.get("reference"),
        reference_case=data.get("reference_case"),
        case_precedent=data.get("case_precedent"),
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case
