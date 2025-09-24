import os
import re
from datetime import datetime
import httpx
from dotenv import load_dotenv

from app.db import SessionLocal
from app.models.model import Judgement

load_dotenv()
BASE_URL = os.getenv("CRAWL_BASE_URL")

def _strip_html(br_text: str | None) -> str | None:
    if not br_text:
        return None
    text = re.sub(r"<br\s*/?>", "\n", br_text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()

def _parse_date(yyyymmdd: str | None):
    if not yyyymmdd:
        return None
    try:
        return datetime.strptime(yyyymmdd, "%Y%m%d").date()
    except Exception:
        return None

def fetch_law_data(law_id: str):
    url = f"{BASE_URL}{law_id}"
    resp = httpx.get(url, timeout=15)
    resp.raise_for_status()
    try:
        return resp.json()
    except Exception:
        return {
            "error": "Invalid JSON response",
            "status_code": resp.status_code,
            "raw": resp.text[:300]
        }

def save_law_data_to_db(data: dict):
    """
    law.go.kr DRF JSON(PrecService)을 Judgement 테이블에 upsert.
    반환: {"saved": True, "case_number": "..."} or {"saved": False, "reason": "..."}
    """
    if not isinstance(data, dict) or "PrecService" not in data:
        return {"saved": False, "reason": "PrecService not found in response"}

    p = data["PrecService"]

    case_name = p.get("사건명")
    case_number = p.get("사건번호")
    case_date = p.get("선고일자")
    case_result = p.get("선고")
    case_court = p.get("법원명")
    case_court_code = p.get("법원종류코드")
    case_type = p.get("사건종류명")
    case_type_code = p.get("사건종류코드")
    case_result_type = p.get("판결유형")
    case_result_decision = _strip_html(p.get("판시사항"))
    case_result_summary = _strip_html(p.get("판결요지"))
    reference = _strip_html(p.get("참조조문"))
    reference_case = _strip_html(p.get("참조판례"))
    case_precedent = _strip_html(p.get("판례내용"))

    if not case_number or not case_date:
        return {"saved": False, "reason": "missing 사건번호 or 선고일자"}

    case_date_parsed = _parse_date(case_date)

    db = SessionLocal()
    try:
        obj = db.query(Judgement).filter(
            Judgement.case_number == case_number,
            Judgement.case_date == case_date_parsed
        ).first()
        
        if obj is None:
            obj = Judgement(
                case_name=case_name,
                case_number=case_number,
                case_date=case_date_parsed,
                case_result=case_result,
                case_court=case_court,
                case_court_code=case_court_code,
                case_type=case_type,
                case_type_code=case_type_code,
                case_result_type=case_result_type,
                case_result_decision=case_result_decision,
                case_result_summary=case_result_summary,
                reference=reference,
                reference_case=reference_case,
                case_precedent=case_precedent,
            )
            db.add(obj)
        else:
            # 기존 객체 업데이트
            for field, value in [
                ("case_name", case_name),
                ("case_number", case_number),
                ("case_date", case_date_parsed),
                ("case_result", case_result),
                ("case_court", case_court),
                ("case_court_code", case_court_code),
                ("case_type", case_type),
                ("case_type_code", case_type_code),
                ("case_result_type", case_result_type),
                ("case_result_decision", case_result_decision),
                ("case_result_summary", case_result_summary),
                ("reference", reference),
                ("reference_case", reference_case),
                ("case_precedent", case_precedent),
            ]:
                setattr(obj, field, value)

        db.commit()
        return {"saved": True, "case_number": case_number}
    except Exception as e:
        db.rollback()
        return {"saved": False, "reason": str(e)}
    finally:
        db.close()
