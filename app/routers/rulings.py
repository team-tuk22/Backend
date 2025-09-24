# FastAPI의 APIRouter와 에러 처리를 위한 HTTPException을 가져옵니다.
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.databases.database import get_db
from app.models.model import Judgement

# APIRouter 객체를 생성합니다. Flask의 Blueprint와 비슷한 역할을 합니다.
# prefix는 이 라우터에 속한 모든 API의 기본 경로를 의미합니다.
router = APIRouter(prefix="/api/v1/rulings")

# 상세보기 : 사건번호로 판례 조회
@router.get("/{case_number}")
def get_ruling_detail(case_number: str, db: Session = Depends(get_db)):
    obj = db.query(Judgement).filter(Judgement.case_number == case_number).first()
    if not obj:
        raise HTTPException(status_code=404, detail="해당 판례를 찾을 수 없습니다.")
    return {
        "id": obj.id,
        "case_number": obj.case_number,
        "case_name": obj.case_name,
        "case_date": obj.case_date,
        "case_result": obj.case_result,
        "case_court": obj.case_court,
        "case_court_code": obj.case_court_code,
        "case_type": obj.case_type,
        "case_type_code": obj.case_type_code,
        "case_result_type": obj.case_result_type,
        "case_result_decision": obj.case_result_decision,
        "case_result_summary": obj.case_result_summary,
        "reference": obj.reference,
        "reference_case": obj.reference_case,
        "case_precedent": obj.case_precedent,
    }

# 요약보기 : 사건번호로 판례 요약 조회
@router.get("/{case_number}/summary")
def get_ruling_summary(case_id: str):
    #1 1. case_number로 판례 데이터를 찾는다.
    case = next((case for case in mock_cases if case["id"] == case_id), None)
    
    #2 판례를 찾았다면, 요약 정보만 담은 새로운 응답을 만든다.
    if case:
        return {"id": case["id"], "summary": case["summary"]}
    #3 판례가 없다면 에러를 보냄.
    else:
        raise HTTPException(status_code=404, detail="해당 ID의 판례를 찾을 수 없습니다.")
